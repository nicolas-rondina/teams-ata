# TeamsAta

Gerador automático de atas de reunião com inteligência artificial. A partir do
áudio (ou vídeo) de uma reunião, o TeamsAta transcreve a conversa e produz uma
ata estruturada e profissional em português, pronta para compartilhar.

## Como funciona

```
Áudio/vídeo  →  Transcrição (Whisper)  →  Revisão por IA  →  Ata estruturada
```

1. O **FFmpeg** extrai e normaliza o áudio (e divide automaticamente reuniões longas).
2. O **Whisper (Groq)** transcreve a fala em texto com marcações de tempo `[mm:ss]`.
3. Uma etapa de **revisão por IA** corrige termos técnicos, nomes de sistemas e siglas pelo contexto.
4. O **Llama (Groq)** gera a ata estruturada conforme o tipo de reunião escolhido.

### Qualidade da transcrição

O TeamsAta tem três camadas para reduzir erros comuns de transcrição automática:

- **Filtro anti-alucinação** — descarta texto que o Whisper costuma inventar em
  trechos de silêncio ou ruído (ex.: "Legendas por...", agradecimentos soltos).
- **Revisão automática por IA** — corrige, pelo contexto, jargão e siglas
  conhecidos (ERP, fiscal, contábil) sem precisar de lista manual.
- **Glossário** — uma "trava" opcional para nomes próprios internos que a IA não
  tem como adivinhar (nomes de pessoas, sistemas da empresa).

## Tipos de reunião

A ata é estruturada de acordo com o perfil escolhido:

| Perfil | Uso |
| --- | --- |
| Padrão | Reunião geral de qualquer tipo |
| Planejamento | Sprint, trimestre ou projeto |
| Status / Acompanhamento | Projetos em andamento |
| Comercial / Vendas | Clientes, negociações, apresentações |
| Técnica / Desenvolvimento | Arquitetura, code review, decisões técnicas |
| RH / One-on-One | Feedback, avaliação, desenvolvimento de pessoas |

## Tecnologias

- **Python 3.8+**
- **Groq API** — transcrição (Whisper) e geração da ata (Llama)
- **FFmpeg** — extração e processamento de áudio/vídeo
- **Streamlit** — interface web

## Instalação

**Pré-requisitos:** Python 3.8+ e [FFmpeg](https://ffmpeg.org/download.html)
instalados e disponíveis no `PATH`.

```bash
git clone https://github.com/nicolas-rondina/teams-ata.git
cd teams-ata
pip install -r requirements.txt
```

### Configuração da chave da Groq

1. Crie uma chave gratuita em https://console.groq.com/keys
2. Copie o arquivo de exemplo e preencha com a sua chave:

```bash
cp .env.example .env
```

```env
GROQ_API_KEY=sua_chave_aqui
```

## Como usar

### Interface web (recomendado)

```bash
streamlit run app.py
```

Faça o upload do áudio, informe o nome da reunião e os participantes, escolha o
tipo de reunião e clique em **Gerar Ata**. Ao final, a ata aparece na tela e
pode ser baixada em **Word (.docx)**, **PDF (.pdf)** ou **texto (.txt)**.

### Linha de comando

```bash
python gerar_ata.py "caminho/do/audio.mp3"
```

O script pergunta o nome da reunião, os participantes e o tipo. A ata é salva
automaticamente na pasta `atas/` nos três formatos (`.txt`, `.docx` e `.pdf`).

**Formatos aceitos:** mp3, mp4, wav, ogg, m4a.

## Exemplo de saída

```
=====================================
        ATA DE REUNIÃO
=====================================
Reunião      : Planejamento Q3
Tipo         : Planejamento
Data         : 08/06/2026 às 14:00
Participantes: João, Ana, Pedro
=====================================

## Resumo Executivo
Reunião de planejamento do terceiro trimestre, com foco em metas de vendas.

## Metas Definidas
- Aumentar as vendas em 20% no trimestre

## Decisões Tomadas
✅ João ficou responsável por enviar a proposta até sexta-feira

...
```

## Configuração avançada

Constantes no início de `gerar_ata.py` permitem ajustar o comportamento:

- `MODELO_TRANSCRICAO` — `whisper-large-v3` (mais preciso) ou `whisper-large-v3-turbo` (mais rápido)
- `REVISAR_TRANSCRICAO_COM_IA` — liga/desliga a revisão automática por IA
- `GLOSSARIO_CORRECAO` — adicione termos internos no formato `regex: "forma correta"`
- `LIMITE_NO_SPEECH` / `LIMITE_LOGPROB` — sensibilidade do filtro anti-alucinação

## Roadmap

- [x] Transcrição de áudio com IA
- [x] Geração de ata estruturada com IA (resumo, decisões, itens de ação)
- [x] Perfis de reunião (planejamento, comercial, técnica, etc.)
- [x] Interface web para upload do áudio
- [x] Correção automática de termos na transcrição
- [x] Exportar a ata em `.docx` / `.pdf`
- [x] Mensagens de erro amigáveis
- [ ] Integração automática com Microsoft Teams

## Licença

[MIT](LICENSE)
