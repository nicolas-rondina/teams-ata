import streamlit as st
import os
import re
import tempfile
from datetime import datetime
from dotenv import load_dotenv
from gerar_ata import (
    transcrever_audio, corrigir_transcricao, extrair_participantes,
    mapear_locutores, gerar_ata_com_ia, refinar_bloco, montar_documento,
    traduzir_erro, PERFIS,
)
from exportar import gerar_docx, gerar_pdf
from tema import aplicar_tema, rodape
import diarizacao


def nome_da_gravacao(nome_arquivo):
    """Deriva o nome da reunião a partir do nome do arquivo da gravação do Teams."""
    base = os.path.splitext(nome_arquivo)[0]
    base = re.sub(r"[-_ ]*\d{8}[_ ]?\d{6}.*$", "", base)  # carimbo de data 20260610_140000
    base = re.sub(r"[-_ ]*(meeting recording|grava[çc][ãa]o|recording|v[íi]deo)\b.*$", "", base, flags=re.IGNORECASE)
    base = base.replace("_", " ").strip(" -")
    return base or os.path.splitext(nome_arquivo)[0]


def dividir_em_blocos(conteudo):
    """Divide a ata (Markdown) em blocos por título '## '. Retorna lista de (titulo, texto)."""
    blocos, titulo, buffer = [], "Início", []
    for linha in conteudo.split("\n"):
        if linha.strip().startswith("## "):
            if buffer:
                blocos.append((titulo, "\n".join(buffer)))
            titulo, buffer = linha.strip()[3:].strip(), [linha]
        else:
            buffer.append(linha)
    if buffer:
        blocos.append((titulo, "\n".join(buffer)))
    return blocos

load_dotenv()

st.set_page_config(
    page_title="TeamsAta · Nexxa",
    page_icon="📋",
    layout="centered"
)

aplicar_tema()
st.caption("Gerador automático de atas de reunião com IA")
st.divider()

arquivo_audio = st.file_uploader(
    "Selecione a gravação da reunião",
    type=["mp3", "mp4", "wav", "ogg", "m4a"],
    help="Baixe a gravação do Teams (OneDrive › Gravações) e anexe aqui. Formatos: mp3, mp4, wav, ogg, m4a"
)

# Auto-preenche o nome da reunião a partir do nome do arquivo da gravação
if arquivo_audio is not None and st.session_state.get("_arquivo_atual") != arquivo_audio.name:
    st.session_state["_arquivo_atual"] = arquivo_audio.name
    st.session_state["nome_reuniao"] = nome_da_gravacao(arquivo_audio.name)

# Preenche o campo Participantes com o que a IA detectou na geração anterior
if "_part_pendente" in st.session_state:
    st.session_state["participantes"] = st.session_state.pop("_part_pendente")

col1, col2 = st.columns(2)

with col1:
    nome_reuniao = st.text_input("Nome da reunião", key="nome_reuniao", placeholder="Preenchido pela gravação")

with col2:
    participantes = st.text_input(
        "Participantes",
        key="participantes",
        placeholder="Detectado automaticamente se vazio",
        help="Deixe em branco para a IA identificar os participantes (e preencher aqui) automaticamente"
    )

opcoes_perfil = list(PERFIS.keys())
tipo_reuniao = st.selectbox(
    "Tipo de reunião",
    opcoes_perfil,
    help="\n".join([f"**{k}**: {v['descricao']}" for k, v in PERFIS.items()])
)
st.caption(f"📌 {PERFIS[tipo_reuniao]['descricao']}")

st.divider()

if st.button("Gerar Ata", type="primary", use_container_width=True):

    if not arquivo_audio:
        st.error("Selecione um arquivo de áudio.")
    elif not nome_reuniao:
        st.error("Digite o nome da reunião.")
    elif not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY não encontrada. Verifique o arquivo .env")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(arquivo_audio.name)[1]) as tmp:
            tmp.write(arquivo_audio.read())
            caminho_tmp = tmp.name

        participantes_auto = not participantes.strip()
        usar_diarizacao = diarizacao.disponivel()

        try:
            with st.status("Processando reunião...", expanded=True) as status:
                if usar_diarizacao:
                    st.write("⏳ Etapa 1/2 — Transcrevendo e separando os locutores (AssemblyAI)...")
                    transcricao = diarizacao.transcrever_diarizado(caminho_tmp)
                    st.write("✅ Transcrição com locutores concluída!")
                    st.write("🧩 Identificando os participantes pelas vozes...")
                    transcricao, detectados = mapear_locutores(transcricao)
                    if participantes_auto:
                        participantes = detectados or "Não identificado"
                    st.write(f"✅ Participantes: {detectados or 'Não identificado'}")
                else:
                    st.write("⏳ Etapa 1/2 — Extraindo e transcrevendo o áudio via Groq...")
                    transcricao = transcrever_audio(caminho_tmp)
                    st.write("✅ Transcrição concluída!")
                    st.write("🔎 Revisando termos técnicos e nomes com IA...")
                    transcricao = corrigir_transcricao(transcricao)
                    st.write("✅ Revisão concluída!")
                    if participantes_auto:
                        st.write("🧩 Identificando os participantes pelos nomes citados...")
                        participantes = extrair_participantes(transcricao) or "Não identificado"
                        st.write(f"✅ Participantes: {participantes}")

                st.write(f"⏳ Etapa 2/2 — Gerando ata ({tipo_reuniao}) com IA...")
                conteudo_ia = gerar_ata_com_ia(transcricao, nome_reuniao, participantes, tipo_reuniao)
                status.update(label="✅ Ata gerada com sucesso!", state="complete")

            st.session_state["ata"] = {
                "conteudo": conteudo_ia,
                "transcricao": transcricao,
                "nome": nome_reuniao,
                "participantes": participantes,
                "tipo": tipo_reuniao,
                "participantes_auto": participantes_auto,
                "usar_diarizacao": usar_diarizacao,
            }

            # Se a IA detectou os participantes, agenda o preenchimento do campo
            if participantes_auto and participantes and participantes != "Não identificado":
                st.session_state["_part_pendente"] = participantes

        except Exception as exc:
            st.error(f"❌ {traduzir_erro(exc)}")

        finally:
            os.unlink(caminho_tmp)

# Recarrega para preencher o campo Participantes com o que foi detectado
if "_part_pendente" in st.session_state:
    st.rerun()


# ── Ata gerada: exibição, ajuste interativo e download ──────────────────────
if "ata" in st.session_state:
    ata = st.session_state["ata"]

    if ata["participantes_auto"] and ata["usar_diarizacao"]:
        st.info(
            f"👥 **Participantes (por separação de voz):** {ata['participantes']}\n\n"
            "A IA separou as vozes e nomeou **só quem se identificou claramente**. ⚠️ **Confira e edite:** "
            "nomes podem precisar de correção; quem aparece como 'Locutor X' não disse o próprio nome; "
            "e **quem ficou totalmente calado não aparece**. Ajuste o campo **Participantes** e gere novamente se precisar."
        )
    elif ata["participantes_auto"]:
        st.info(
            f"👥 **Participantes identificados automaticamente:** {ata['participantes']}\n\n"
            "A lista vem dos nomes citados na reunião, então pode não incluir quem ficou calado."
        )

    st.markdown("### Ata gerada")
    st.markdown(ata["conteudo"])

    # Ajuste interativo por bloco: o usuário escolhe a seção e pede a correção
    with st.expander("✏️ Não gostou de um bloco? Peça à IA para ajustar", expanded=False):
        blocos = dividir_em_blocos(ata["conteudo"])
        titulos = [t for t, _ in blocos]
        bloco_escolhido = st.selectbox("Qual bloco você quer ajustar?", titulos, key="bloco_escolhido")
        instrucao = st.text_area(
            "O que mudar nesse bloco?",
            placeholder="Ex.: detalhe melhor; resuma em tópicos; corrija 'Joao' para 'João'; "
                        "deixe o tom mais formal; remova o que não foi decidido",
            key="instrucao_bloco",
        )
        if st.button("Corrigir este bloco", use_container_width=True):
            if instrucao.strip():
                try:
                    with st.spinner(f"Ajustando o bloco '{bloco_escolhido}'..."):
                        idx = titulos.index(bloco_escolhido)
                        titulo, texto_bloco = blocos[idx]
                        blocos[idx] = (titulo, refinar_bloco(texto_bloco, instrucao))
                        st.session_state["ata"]["conteudo"] = "\n".join(t for _, t in blocos)
                    st.rerun()
                except Exception as exc:
                    st.error(f"❌ {traduzir_erro(exc)}")
            else:
                st.warning("Escreva o que você quer ajustar nesse bloco.")

    # Download — sempre reflete a versão mais recente da ata
    st.divider()
    st.markdown("#### Baixar")
    documento = montar_documento(ata["conteudo"], ata["nome"], ata["participantes"], ata["transcricao"], ata["tipo"])
    base_nome = f"ata_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    docx_bytes = gerar_docx(ata["conteudo"], ata["nome"], ata["participantes"], ata["transcricao"], ata["tipo"])
    pdf_bytes = gerar_pdf(ata["conteudo"], ata["nome"], ata["participantes"], ata["transcricao"], ata["tipo"])

    col_docx, col_pdf, col_txt = st.columns(3)
    with col_docx:
        st.download_button(
            label="Word (.docx)", data=docx_bytes, file_name=f"{base_nome}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    with col_pdf:
        st.download_button(
            label="PDF (.pdf)", data=pdf_bytes, file_name=f"{base_nome}.pdf",
            mime="application/pdf", use_container_width=True,
        )
    with col_txt:
        st.download_button(
            label="Texto (.txt)", data=documento.encode("utf-8"), file_name=f"{base_nome}.txt",
            mime="text/plain", use_container_width=True,
        )

rodape()
