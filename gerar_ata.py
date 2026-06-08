import sys
import os
from datetime import datetime
from faster_whisper import WhisperModel


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


def gerar_ata(transcricao, nome_reuniao, participantes):
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    ata = f"""=====================================
        ATA DE REUNIÃO
=====================================
Reunião  : {nome_reuniao}
Data     : {agora}
Participantes: {participantes}
=====================================

TRANSCRIÇÃO:

{transcricao}

=====================================
Gerado automaticamente por TeamsAta
=====================================
"""
    return ata


def salvar_ata(ata, nome_reuniao):
    os.makedirs("atas", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"atas/ata_{timestamp}.txt"

    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(ata)

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

    nome_reuniao = input("Nome da reunião: ")
    participantes = input("Participantes (separe por vírgula): ")

    transcricao = transcrever_audio(caminho_audio)
    ata = gerar_ata(transcricao, nome_reuniao, participantes)
    arquivo_salvo = salvar_ata(ata, nome_reuniao)

    print(f"\nAta gerada com sucesso!")
    print(f"Arquivo salvo em: {arquivo_salvo}")
    print("\n--- Preview ---")
    print(ata[:600])
