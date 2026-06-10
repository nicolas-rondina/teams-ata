import streamlit as st
import os
import re
import tempfile
from datetime import datetime
from dotenv import load_dotenv
from gerar_ata import (
    transcrever_audio, corrigir_transcricao, extrair_participantes,
    mapear_locutores, gerar_ata_com_ia, montar_documento, traduzir_erro, PERFIS,
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

col1, col2 = st.columns(2)

with col1:
    nome_reuniao = st.text_input("Nome da reunião", key="nome_reuniao", placeholder="Preenchido pela gravação")

with col2:
    participantes = st.text_input(
        "Participantes",
        placeholder="Detectado automaticamente se vazio",
        help="Deixe em branco para a IA identificar os participantes pelos nomes citados na reunião"
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
                    st.write("⏳ Etapa 1/3 — Transcrevendo e separando os locutores (AssemblyAI)...")
                    transcricao = diarizacao.transcrever_diarizado(caminho_tmp)
                    st.write("✅ Transcrição com locutores concluída!")
                    st.write("🧩 Identificando os participantes pelas vozes...")
                    transcricao, detectados = mapear_locutores(transcricao)
                    if participantes_auto:
                        participantes = detectados or "Não identificado"
                    st.write(f"✅ Participantes: {detectados or 'Não identificado'}")
                else:
                    st.write("⏳ Etapa 1/3 — Extraindo e transcrevendo o áudio via Groq...")
                    transcricao = transcrever_audio(caminho_tmp)
                    st.write("✅ Transcrição concluída!")
                    st.write("🔎 Revisando termos técnicos e nomes com IA...")
                    transcricao = corrigir_transcricao(transcricao)
                    st.write("✅ Revisão concluída!")
                    if participantes_auto:
                        st.write("🧩 Identificando os participantes pelos nomes citados...")
                        participantes = extrair_participantes(transcricao) or "Não identificado"
                        st.write(f"✅ Participantes: {participantes}")

                st.write(f"⏳ Etapa 2/3 — Gerando ata ({tipo_reuniao}) com IA...")
                conteudo_ia = gerar_ata_com_ia(transcricao, nome_reuniao, participantes, tipo_reuniao)
                st.write("✅ Ata gerada!")

                st.write("⏳ Etapa 3/3 — Montando documento final...")
                documento = montar_documento(conteudo_ia, nome_reuniao, participantes, transcricao, tipo_reuniao)
                status.update(label="✅ Ata gerada com sucesso!", state="complete")

            st.success("Pronto! Sua ata está abaixo.")

            if participantes_auto and usar_diarizacao:
                st.info(
                    f"👥 **Participantes identificados (separação de voz):** {participantes}\n\n"
                    "A IA separou as vozes e deduziu os nomes pelo diálogo. Se algum aparecer como "
                    "'Locutor X', o nome dele não foi dito na reunião. Ajuste o campo **Participantes** "
                    "e gere novamente se precisar."
                )
            elif participantes_auto:
                st.info(
                    f"👥 **Participantes identificados automaticamente:** {participantes}\n\n"
                    "A lista vem dos nomes citados na reunião, então pode não incluir quem ficou "
                    "calado. Se faltar alguém, preencha o campo **Participantes** e gere novamente."
                )

            st.markdown("### Ata gerada")
            st.markdown(conteudo_ia)

            st.divider()
            st.markdown("#### Baixar")

            base_nome = f"ata_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            docx_bytes = gerar_docx(conteudo_ia, nome_reuniao, participantes, transcricao, tipo_reuniao)
            pdf_bytes = gerar_pdf(conteudo_ia, nome_reuniao, participantes, transcricao, tipo_reuniao)

            col_docx, col_pdf, col_txt = st.columns(3)
            with col_docx:
                st.download_button(
                    label="Word (.docx)",
                    data=docx_bytes,
                    file_name=f"{base_nome}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            with col_pdf:
                st.download_button(
                    label="PDF (.pdf)",
                    data=pdf_bytes,
                    file_name=f"{base_nome}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with col_txt:
                st.download_button(
                    label="Texto (.txt)",
                    data=documento.encode("utf-8"),
                    file_name=f"{base_nome}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

        except Exception as exc:
            st.error(f"❌ {traduzir_erro(exc)}")

        finally:
            os.unlink(caminho_tmp)

rodape()
