import streamlit as st
import os
import tempfile
from datetime import datetime
from dotenv import load_dotenv
from gerar_ata import transcrever_audio, gerar_ata_com_ia, montar_documento, PERFIS

load_dotenv()

st.set_page_config(
    page_title="TeamsAta",
    page_icon="📋",
    layout="centered"
)

st.title("📋 TeamsAta")
st.subheader("Gerador automático de atas de reunião com IA")
st.divider()

arquivo_audio = st.file_uploader(
    "Selecione o áudio da reunião",
    type=["mp3", "mp4", "wav", "ogg", "m4a"],
    help="Formatos aceitos: mp3, mp4, wav, ogg, m4a"
)

col1, col2 = st.columns(2)

with col1:
    nome_reuniao = st.text_input("Nome da reunião", placeholder="Ex: Planejamento Q3")

with col2:
    participantes = st.text_input("Participantes", placeholder="Ex: João, Ana, Pedro")

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
    elif not participantes:
        st.error("Digite os participantes.")
    elif not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY não encontrada. Verifique o arquivo .env")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(arquivo_audio.name)[1]) as tmp:
            tmp.write(arquivo_audio.read())
            caminho_tmp = tmp.name

        try:
            with st.status("Processando reunião...", expanded=True) as status:
                st.write("⏳ Etapa 1/3 — Extraindo e transcrevendo o áudio via Groq...")
                transcricao = transcrever_audio(caminho_tmp)
                st.write("✅ Transcrição concluída!")

                st.write(f"⏳ Etapa 2/3 — Gerando ata ({tipo_reuniao}) com IA...")
                conteudo_ia = gerar_ata_com_ia(transcricao, nome_reuniao, participantes, tipo_reuniao)
                st.write("✅ Ata gerada!")

                st.write("⏳ Etapa 3/3 — Montando documento final...")
                documento = montar_documento(conteudo_ia, nome_reuniao, participantes, transcricao, tipo_reuniao)
                status.update(label="✅ Ata gerada com sucesso!", state="complete")

            st.success("Pronto! Sua ata está abaixo.")

            st.markdown("### Ata gerada")
            st.markdown(conteudo_ia)

            st.divider()
            st.download_button(
                label="Baixar ata completa (.txt)",
                data=documento.encode("utf-8"),
                file_name=f"ata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        finally:
            os.unlink(caminho_tmp)
