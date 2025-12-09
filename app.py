import os
import io
import pandas as pd
import streamlit as st
from core import (
    load_kb,
    append_kb_entry,
    generate_answer,
)


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
KB_PATH = os.path.join(DATA_DIR, "kb.csv")


def ensure_data_dir() -> None:
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def download_kb_button(df: pd.DataFrame) -> None:
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False, encoding="utf-8")
    st.download_button(
        label="Kuramo KB (CSV)",
        data=csv_buf.getvalue(),
        file_name="kb.csv",
        mime="text/csv",
    )


def main() -> None:
    st.set_page_config(page_title="Kosmo Chatbot - Kinyarwanda", page_icon="🤖")
    st.title("🤖 Kosmo Chatbot (Kinyarwanda)")
    st.caption(
        "Ibibazo bijyanye n'imihango, gusama/utwite, n'iterembere ry'umwana."
    )

    kb_df = load_kb()

    with st.sidebar:
        st.header("Ongeramo ikibazo n'igisubizo (Kinyarwanda)")
        with st.form("add_kb_form", clear_on_submit=True):
            q = st.text_area("Ikibazo", height=80)
            a = st.text_area("Igisubizo", height=120)
            t = st.text_input("Icyiciro/Tags (bitandukanyijwe na koma)", value="")
            submitted = st.form_submit_button("Bika mu bubiko")
            if submitted:
                if q.strip() and a.strip():
                    append_kb_entry(q, a, t)
                    st.success("Byashyizwe mu bubiko bw'amakuru!")
                else:
                    st.warning("Andika ikibazo n'igisubizo mbere yo kubika.")

        st.divider()
        st.subheader("Ubusobanuro n'Icyitonderwa")
        st.markdown(
            """
            - Ibisubizo bitangwa hashingiwe ku bugaragazwa n'ububiko bw'amakuru.
            - Ibi si inama za muganga. Mu gihe uhangayitse cyangwa ibimenyetso bikomeye bibonetse, waduhamagara kuri +250786305924 cyangwa udusure k'urubuga rwacu rwa KosmoHealth.
            - Ukeneye kongeramo ibyo uzi? Koresha ifishi yo hejuru.
            """
        )

        st.subheader("Kubika/Kureba KB")
        st.dataframe(kb_df, use_container_width=True, hide_index=True)
        download_kb_button(kb_df)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Andika ikibazo cyawe hano mu Kinyarwanda…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        answer = generate_answer(user_input, load_kb())
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)


if __name__ == "__main__":
    main()