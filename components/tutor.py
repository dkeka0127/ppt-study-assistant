"""AI Tutor 탭 컴포넌트"""

import streamlit as st
from modules.chatbot import get_tutor_response


def render_tutor():
    """AI Tutor 탭 렌더링"""
    # Two-column layout
    tutor_left, tutor_right = st.columns([3, 1])

    with tutor_right:
        st.subheader("추천 질문")
        suggested_questions = [
            "핵심 개념 정리해줘",
            "시험 포인트 3가지",
            "쉽게 설명해줘",
            "예시를 들어줘"
        ]

        for sq in suggested_questions:
            if st.button(sq, key=f"suggested_{sq}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": sq})
                with st.spinner("답변 생성 중..."):
                    response = get_tutor_response(
                        sq,
                        st.session_state.ppt_context,
                        st.session_state.chat_history[:-1],
                        st.session_state.level
                    )
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
                st.rerun()

        st.markdown("---")

        if st.session_state.chat_history:
            if st.button("대화 지우기", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

    with tutor_left:
        # Chat container with fixed height
        chat_container = st.container(height=500)
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown("PPT 내용에 대해 궁금한 점을 질문하세요.")
            else:
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.chat_message("user").write(msg["content"])
                    else:
                        st.chat_message("assistant").write(msg["content"])

        # Chat Input
        user_input = st.chat_input("질문을 입력하세요...")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("답변 생성 중..."):
                response = get_tutor_response(
                    user_input,
                    st.session_state.ppt_context,
                    st.session_state.chat_history[:-1],
                    st.session_state.level
                )
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
