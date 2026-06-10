"""Transcrição com separação de locutores (diarização) via AssemblyAI.

Quando há ASSEMBLYAI_API_KEY configurada, a transcrição é feita pela AssemblyAI
com speaker_labels, identificando quem falou cada trecho ("Locutor A", "B"...).
Depois a IA mapeia cada locutor a um nome real (ver gerar_ata.mapear_locutores).

Usa a API REST via httpx (sem SDK), para não exigir dependências pesadas.
"""
import os
import time

import httpx

from gerar_ata import extrair_audio_mp3, _corrigir_termos

_BASE = "https://api.assemblyai.com/v2"
_BLOCO = 5 * 1024 * 1024  # 5 MB por bloco no upload


def disponivel():
    """Indica se a diarização está habilitada (chave da AssemblyAI presente)."""
    return bool(os.getenv("ASSEMBLYAI_API_KEY"))


def _ler_em_blocos(arquivo):
    while True:
        dados = arquivo.read(_BLOCO)
        if not dados:
            break
        yield dados


def transcrever_diarizado(caminho_audio):
    """Transcreve o áudio separando os locutores. Retorna o texto no formato
    '[mm:ss] Locutor A: fala', com o glossário de termos já aplicado."""
    chave = os.getenv("ASSEMBLYAI_API_KEY")
    if not chave:
        raise RuntimeError("ASSEMBLYAI_API_KEY não configurada no arquivo .env.")

    cabecalho = {"authorization": chave}
    caminho_mp3 = extrair_audio_mp3(caminho_audio)  # reduz o tamanho do upload

    try:
        with httpx.Client(timeout=600) as cli:
            print("Enviando áudio para a AssemblyAI...")
            with open(caminho_mp3, "rb") as f:
                envio = cli.post(f"{_BASE}/upload", headers=cabecalho, content=_ler_em_blocos(f))
            envio.raise_for_status()
            audio_url = envio.json()["upload_url"]

            pedido = cli.post(
                f"{_BASE}/transcript",
                headers=cabecalho,
                json={"audio_url": audio_url, "speaker_labels": True, "language_code": "pt"},
            )
            pedido.raise_for_status()
            id_transcricao = pedido.json()["id"]

            print("Transcrevendo e separando locutores...")
            while True:
                consulta = cli.get(f"{_BASE}/transcript/{id_transcricao}", headers=cabecalho)
                consulta.raise_for_status()
                dados = consulta.json()
                situacao = dados["status"]
                if situacao == "completed":
                    break
                if situacao == "error":
                    raise RuntimeError(f"AssemblyAI: {dados.get('error')}")
                time.sleep(4)
    finally:
        if os.path.exists(caminho_mp3):
            os.unlink(caminho_mp3)

    linhas = []
    for fala in dados.get("utterances") or []:
        segundos = int(fala["start"] // 1000)
        minutos, seg = divmod(segundos, 60)
        texto = _corrigir_termos(fala["text"].strip())
        linhas.append(f"[{minutos:02d}:{seg:02d}] Locutor {fala['speaker']}: {texto}")

    return "\n".join(linhas)
