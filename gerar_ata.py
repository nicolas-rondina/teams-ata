import sys
import os
import re
import subprocess
import tempfile
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

DURACAO_CHUNK = 1200  # 20 minutos por pedaço

PERFIS = {
    "Padrão": {
        "descricao": "Ata geral para qualquer tipo de reunião",
        "instrucoes": """
## Resumo Executivo
(2-3 frases resumindo o que foi discutido)

## Tópicos Discutidos
(lista dos principais assuntos abordados)

## Decisões Tomadas
(liste cada decisão com um ✅)

## Itens de Ação
(tabela com: Tarefa | Responsável | Prazo)

## Próximos Passos
(o que acontece depois dessa reunião)
"""
    },
    "Planejamento": {
        "descricao": "Reuniões de planejamento de sprint, trimestre ou projeto",
        "instrucoes": """
## Resumo Executivo
(objetivo do planejamento e período coberto)

## Metas Definidas
(liste cada meta com indicador de sucesso)

## Tarefas Planejadas
(tabela com: Tarefa | Responsável | Prazo | Prioridade)

## Riscos Identificados
(liste os riscos mencionados e como mitigá-los)

## Decisões Tomadas
(liste cada decisão com um ✅)

## Próxima Revisão
(quando será a próxima reunião de acompanhamento)
"""
    },
    "Status / Acompanhamento": {
        "descricao": "Reuniões de acompanhamento de projetos em andamento",
        "instrucoes": """
## Resumo Executivo
(situação geral do projeto)

## Status das Tarefas
(tabela com: Tarefa | Responsável | Status | Observação)
Status pode ser: ✅ Concluído | 🔄 Em andamento | ⚠️ Atrasado | ❌ Bloqueado

## Bloqueios e Problemas
(liste os impedimentos mencionados e quem vai resolver)

## Decisões Tomadas
(liste cada decisão com um ✅)

## Itens de Ação
(tabela com: Tarefa | Responsável | Prazo)

## Próximos Passos
(o que acontece até a próxima reunião)
"""
    },
    "Comercial / Vendas": {
        "descricao": "Reuniões com clientes, negociações e apresentações comerciais",
        "instrucoes": """
## Resumo Executivo
(contexto da reunião e cliente envolvido)

## Necessidades do Cliente
(o que o cliente precisa ou solicitou)

## Proposta / Solução Apresentada
(o que foi apresentado ou proposto)

## Objeções Levantadas
(dúvidas ou resistências do cliente)

## Decisões e Acordos
(liste cada acordo com um ✅)

## Itens de Ação
(tabela com: Tarefa | Responsável | Prazo)

## Próximos Passos Comerciais
(próxima etapa do processo de venda)
"""
    },
    "Técnica / Desenvolvimento": {
        "descricao": "Reuniões de arquitetura, code review, decisões técnicas",
        "instrucoes": """
## Resumo Executivo
(contexto técnico e objetivo da reunião)

## Problemas Técnicos Discutidos
(liste cada problema e seu contexto)

## Soluções e Decisões Técnicas
(liste cada decisão técnica com ✅ e justificativa)

## Itens de Ação Técnicos
(tabela com: Tarefa | Desenvolvedor | Prazo)

## Dívidas Técnicas Identificadas
(pontos que precisam ser resolvidos no futuro)

## Próximos Passos
(o que cada desenvolvedor fará a seguir)
"""
    },
    "RH / One-on-One": {
        "descricao": "Reuniões de feedback, avaliação e desenvolvimento de pessoas",
        "instrucoes": """
## Resumo Executivo
(contexto da conversa)

## Pontos Positivos Destacados
(conquistas e comportamentos reconhecidos)

## Pontos de Desenvolvimento
(áreas de melhoria discutidas)

## Metas e Compromissos
(tabela com: Meta | Responsável | Prazo)

## Suporte Necessário
(o que o colaborador precisa da empresa ou liderança)

## Próximo Acompanhamento
(data da próxima reunião de feedback)
"""
    },
}


def extrair_audio_mp3(caminho_arquivo):
    print("Extraindo áudio...")
    arquivo_mp3 = tempfile.mktemp(suffix=".mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-i", caminho_arquivo, "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k", arquivo_mp3],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    return arquivo_mp3


def obter_duracao(caminho_audio):
    resultado = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", caminho_audio],
        capture_output=True, text=True
    )
    return float(resultado.stdout.strip())


def dividir_audio(caminho_audio):
    duracao = obter_duracao(caminho_audio)
    if duracao <= DURACAO_CHUNK:
        return [(caminho_audio, 0)], False

    print(f"Áudio longo ({int(duracao//60)} min) — dividindo em pedaços de 20 minutos...")
    chunks = []
    inicio = 0
    while inicio < duracao:
        arquivo_chunk = tempfile.mktemp(suffix=".mp3")
        subprocess.run(
            ["ffmpeg", "-y", "-i", caminho_audio, "-ss", str(inicio),
             "-t", str(DURACAO_CHUNK), "-ac", "1", "-ar", "16000", "-b:a", "64k", arquivo_chunk],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        chunks.append((arquivo_chunk, inicio))
        inicio += DURACAO_CHUNK

    return chunks, True


# Modelo de transcrição. "whisper-large-v3" é o mais preciso e o que menos alucina.
# Troque por "whisper-large-v3-turbo" se quiser priorizar velocidade em vez de precisão.
MODELO_TRANSCRICAO = "whisper-large-v3"

# Limites para descartar segmentos provavelmente "alucinados" (texto inventado no silêncio).
# Um segmento só é descartado quando atende AOS DOIS critérios ao mesmo tempo,
# para evitar apagar fala real. Ajuste se necessário.
LIMITE_NO_SPEECH = 0.6        # acima disso: provável trecho sem fala
LIMITE_LOGPROB = -0.5         # abaixo disso: baixa confiança na transcrição
LIMITE_NO_SPEECH_FORTE = 0.8  # acima disso: descarta mesmo com boa confiança (silêncio quase certo)

# Frases que o Whisper costuma inventar em trechos de silêncio/ruído (estilo legenda de vídeo).
FRASES_ALUCINACAO = {
    "legendas pela comunidade amara.org",
    "amara.org",
    "obrigado por assistir",
    "obrigado por assistir!",
    "inscreva-se no canal",
    "até o próximo vídeo",
    "muito obrigado.",
}

# Padrões (início da frase) típicos de alucinação de legenda/silêncio.
PADROES_ALUCINACAO = [
    re.compile(r"^\s*legendas?\s+(por|pela)\b", re.IGNORECASE),
    re.compile(r"amara\.org", re.IGNORECASE),
    re.compile(r"^\s*inscreva-se\b", re.IGNORECASE),
    re.compile(r"^\s*obrigado por assistir", re.IGNORECASE),
]

# Glossário de correção: termos que o Whisper costuma ouvir/escrever errado.
# A chave é uma expressão regular (sem distinção de maiúsc/minúsc); o valor é a forma correta.
# Adicione aqui os termos da sua empresa (nomes de pessoas, sistemas internos, siglas, etc.).
GLOSSARIO_CORRECAO = {
    r"prote[uú]s": "Protheus",
    r"\b(?:totos|totus|tots|toto)\b": "TOTVS",
    r"\b(?:cefaz|cfaz|cfazia)\b": "SEFAZ",
    r"\bpico\s*fins\b": "PIS/COFINS",
}


def _campo_segmento(segmento, nome, padrao=0.0):
    """Lê um campo do segmento, funcionando tanto para dict quanto para objeto."""
    valor = segmento[nome] if isinstance(segmento, dict) else getattr(segmento, nome, padrao)
    return padrao if valor is None else valor


def _segmento_confiavel(texto, no_speech_prob, avg_logprob):
    """Decide se um segmento é fala real ou provável alucinação."""
    limpo = texto.strip().lower()
    if not limpo:
        return False
    if limpo in FRASES_ALUCINACAO:
        return False
    if any(padrao.search(texto) for padrao in PADROES_ALUCINACAO):
        return False
    if no_speech_prob > LIMITE_NO_SPEECH_FORTE:
        return False
    if no_speech_prob > LIMITE_NO_SPEECH and avg_logprob < LIMITE_LOGPROB:
        return False
    return True


def _corrigir_termos(texto):
    """Aplica o glossário de correção de jargão/nomes próprios na transcrição."""
    for padrao, correto in GLOSSARIO_CORRECAO.items():
        texto = re.sub(padrao, correto, texto, flags=re.IGNORECASE)
    return texto


def transcrever_audio(caminho_audio):
    cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))

    caminho_mp3 = extrair_audio_mp3(caminho_audio)
    chunks, foi_dividido = dividir_audio(caminho_mp3)
    os.unlink(caminho_mp3)

    linhas = []
    total = len(chunks)
    for i, (chunk, offset) in enumerate(chunks):
        print(f"Transcrevendo parte {i+1}/{total}...")
        with open(chunk, "rb") as f:
            # NÃO passamos 'prompt' aqui de propósito: o Whisper repete o texto
            # do prompt nos trechos de silêncio, criando alucinações.
            resposta = cliente.audio.transcriptions.create(
                file=(os.path.basename(chunk), f.read()),
                model=MODELO_TRANSCRICAO,
                language="pt",
                temperature=0.0,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )

        for segmento in resposta.segments:
            texto_seg = segmento["text"] if isinstance(segmento, dict) else segmento.text
            no_speech_prob = _campo_segmento(segmento, "no_speech_prob")
            avg_logprob = _campo_segmento(segmento, "avg_logprob")

            if not _segmento_confiavel(texto_seg, no_speech_prob, avg_logprob):
                continue

            tempo_real = _campo_segmento(segmento, "start") + offset
            minutos = int(tempo_real // 60)
            segundos = int(tempo_real % 60)
            texto_corrigido = _corrigir_termos(texto_seg.strip())
            linhas.append(f"[{minutos:02d}:{segundos:02d}] {texto_corrigido}")

        if foi_dividido:
            os.unlink(chunk)

    return "\n".join(linhas)


PALAVRAS_POR_CHUNK = 1500


def dividir_transcricao(transcricao):
    linhas = transcricao.split("\n")
    chunks = []
    chunk_atual = []
    palavras_atual = 0

    for linha in linhas:
        palavras_linha = len(linha.split())
        if palavras_atual + palavras_linha > PALAVRAS_POR_CHUNK and chunk_atual:
            chunks.append("\n".join(chunk_atual))
            chunk_atual = [linha]
            palavras_atual = palavras_linha
        else:
            chunk_atual.append(linha)
            palavras_atual += palavras_linha

    if chunk_atual:
        chunks.append("\n".join(chunk_atual))

    return chunks


def resumir_chunk(cliente, chunk, indice, total):
    import time
    print(f"  Resumindo parte {indice+1}/{total}...")
    prompt = f"""Leia este trecho de transcrição de reunião e extraia SOMENTE o que foi explicitamente dito.

Trecho:
{chunk}

Extraia em tópicos:
1. ASSUNTOS: o que foi discutido
2. DECISÕES: somente o que foi aprovado ou acordado (não inclua problemas ou dúvidas)
3. TAREFAS: tarefas concretas com responsável e prazo (somente se foram mencionados)

Seja fiel ao que foi dito. Não adicione informações que não estão no trecho."""

    resposta = cliente.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    time.sleep(12)
    return resposta.choices[0].message.content


def gerar_ata_com_ia(transcricao, nome_reuniao, participantes, tipo_reuniao="Padrão"):
    import time
    print(f"Gerando ata ({tipo_reuniao})...")

    cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))
    perfil = PERFIS.get(tipo_reuniao, PERFIS["Padrão"])

    chunks = dividir_transcricao(transcricao)

    if len(chunks) == 1:
        resumos = transcricao
    else:
        print(f"Transcrição longa — processando em {len(chunks)} partes...")
        partes = [resumir_chunk(cliente, c, i, len(chunks)) for i, c in enumerate(chunks)]
        resumos = "\n\n---\n\n".join(partes)

    print("Montando ata final...")
    prompt = f"""Você é um especialista em gerar atas de reunião precisas e profissionais em português brasileiro.

Analise cuidadosamente o conteúdo da reunião abaixo e gere uma ata estruturada.

Tipo de reunião: {tipo_reuniao}
Nome: {nome_reuniao}
Participantes: {participantes}
Data: {datetime.now().strftime("%d/%m/%Y")}

Conteúdo da reunião:
{resumos}

REGRAS IMPORTANTES — siga à risca:
- "Decisões Tomadas" deve conter APENAS decisões reais — coisas que foram APROVADAS ou ACORDADAS. Problemas identificados NÃO são decisões.
- "Itens de Ação" deve conter APENAS tarefas concretas atribuídas a alguém. Se ninguém foi nomeado, coloque "A definir". Não invente responsáveis.
- Seja fiel ao que foi dito. Não adicione informações que não estão na transcrição.
- Se uma seção não tiver conteúdo suficiente, escreva apenas: "Não mencionado na reunião."
- Escreva de forma clara, objetiva e profissional.

Gere a ata no seguinte formato:{perfil["instrucoes"]}
"""

    resposta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    return resposta.choices[0].message.content


def montar_documento(conteudo_ia, nome_reuniao, participantes, transcricao, tipo_reuniao="Padrão"):
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    documento = f"""=====================================
        ATA DE REUNIÃO
=====================================
Reunião      : {nome_reuniao}
Tipo         : {tipo_reuniao}
Data         : {agora}
Participantes: {participantes}
=====================================

{conteudo_ia}

=====================================
TRANSCRIÇÃO COMPLETA
=====================================

{transcricao}

=====================================
Gerado automaticamente por TeamsAta
=====================================
"""
    return documento


def salvar_ata(documento, nome_reuniao):
    os.makedirs("atas", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"atas/ata_{timestamp}.txt"

    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(documento)

    return nome_arquivo


if __name__ == "__main__":
    print("=== TeamsAta — Gerador de Atas ===\n")

    if len(sys.argv) < 2:
        print("Como usar: python gerar_ata.py <caminho_do_audio>")
        print("Exemplo  : python gerar_ata.py reuniao.mp3")
        sys.exit(1)

    caminho_audio = sys.argv[1]

    if not os.path.exists(caminho_audio):
        print(f"Erro: arquivo '{caminho_audio}' não encontrado.")
        sys.exit(1)

    if not os.getenv("GROQ_API_KEY"):
        print("Erro: GROQ_API_KEY não encontrada. Verifique o arquivo .env")
        sys.exit(1)

    nome_reuniao = input("Nome da reunião: ")
    participantes = input("Participantes (separe por vírgula): ")
    print("Tipos disponíveis:", ", ".join(PERFIS.keys()))
    tipo_reuniao = input("Tipo de reunião (Enter para Padrão): ").strip() or "Padrão"

    transcricao = transcrever_audio(caminho_audio)
    conteudo_ia = gerar_ata_com_ia(transcricao, nome_reuniao, participantes, tipo_reuniao)
    documento = montar_documento(conteudo_ia, nome_reuniao, participantes, transcricao, tipo_reuniao)
    arquivo_salvo = salvar_ata(documento, nome_reuniao)

    print(f"\nAta gerada com sucesso!")
    print(f"Arquivo salvo em: {arquivo_salvo}")
    print("\n--- Preview ---")
    print(documento[:800])
