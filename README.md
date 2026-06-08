# TeamsAta

Gerador automático de atas de reuniões do Microsoft Teams usando inteligência artificial.

## Como funciona

1. Você fornece o áudio da reunião (mp3, mp4, ogg, wav)
2. O modelo **Faster-Whisper** transcreve o áudio em texto
3. O script formata e salva a ata com timestamps

## Tecnologias

- **Python 3.x**
- **Faster-Whisper** — transcrição de áudio com IA (open-source)
- **FFmpeg** — processamento de arquivos de áudio e vídeo

## Instalação

**Pré-requisitos:** Python 3.8+ e FFmpeg instalados.

```bash
git clone https://github.com/nicolas-rondina/teams-ata.git
cd teams-ata
pip install -r requirements.txt
```

## Como usar

```bash
python gerar_ata.py "caminho/do/audio.mp3"
```

O script vai perguntar o nome da reunião e os participantes.
A ata gerada é salva automaticamente na pasta `atas/`.

## Exemplo de saída

```
=====================================
        ATA DE REUNIÃO
=====================================
Reunião  : Planejamento Q3
Data     : 08/06/2026 às 14:00
Participantes: João, Ana, Pedro
=====================================

TRANSCRIÇÃO:

[00:03] Bom dia pessoal, vamos começar a reunião.
[00:45] A meta do trimestre é aumentar as vendas em 20%.
[02:10] Ficou definido que João vai enviar a proposta até sexta.
```

## Roadmap

- [x] Transcrição de áudio com Faster-Whisper
- [ ] Geração de ata estruturada com IA (resumo, decisões, itens de ação)
- [ ] Interface web para upload do áudio
- [ ] Integração automática com Microsoft Teams

## Licença

MIT
