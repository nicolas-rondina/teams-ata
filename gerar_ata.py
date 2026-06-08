import sys
import os
from datetime import datetime
from faster_whisper import WhisperModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def transcrever_audio(caminho_audio):
    print("Carregando modelo de transcrição (primeira vez demora um pouco)...")
    modelo = WhisperModel("base", device="cpu", compute_type="int8")

    print("Transcrevendo o áudio...")
    segmentos, info = modelo.transcribe(caminho_audio, language="pt")

    linhas = []
    for segmento in segmentos:
        minutos = int(segmento.start // 60)
        segundos = int(segmento.start % 60)
        linhas.append(f"[{minutos:02d}:{segundos:02d}] {segmento.text.strip()}")

    return "\n".join(linhas)


def gerar_ata_com_ia(transcricao, nome_reuniao, participantes):
    print("Gerando ata com inteligência artificial...")

    cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""Você é um assistente especializado em gerar atas de reunião profissionais.

Com base na transcrição abaixo, gere uma ata completa e estruturada em português.

Informações da reunião:
- Nome: {nome_reuniao}
- Participantes: {participantes}
- Data: {datetime.now().strftime("%d/%m/%Y")}

Transcrição:
{transcricao}

Gere a ata no seguinte formato:

## Resumo Executivo
(2-3 frases resumindo o que foi discutido)

## Tópicos Discutidos
(lista dos principais assuntos abordados)

## Decisões Tomadas
(liste cada decisão com um ✅)

## Itens de Ação
(tabela com: Tarefa | Responsável | Prazo)
Se não houver prazo mencionado, coloque "A definir".
Se não houver responsável mencionado, coloque "A definir".

## Próximos Passos
(o que acontece depois dessa reunião)

Se alguma seção não tiver informações suficientes na transcrição, escreva "Não mencionado na reunião."
"""

    resposta = cliente.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return resposta.choices[0].message.content


def montar_documento(conteudo_ia, nome_reuniao, participantes, transcricao):
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    documento = f"""=====================================
        ATA DE REUNIÃO
=====================================
Reunião      : {nome_reuniao}
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

    transcricao = transcrever_audio(caminho_audio)
    conteudo_ia = gerar_ata_com_ia(transcricao, nome_reuniao, participantes)
    documento = montar_documento(conteudo_ia, nome_reuniao, participantes, transcricao)
    arquivo_salvo = salvar_ata(documento, nome_reuniao)

    print(f"\nAta gerada com sucesso!")
    print(f"Arquivo salvo em: {arquivo_salvo}")
    print("\n--- Preview ---")
    print(documento[:800])
