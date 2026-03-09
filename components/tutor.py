"""AI Tutor 탭 컴포넌트"""

import streamlit as st
from modules.chatbot import get_tutor_response
from modules.chatbot_rag import get_tutor_response_rag, get_suggested_questions_rag


def render_tutor():
    """AI Tutor 탭 렌더링"""
    # Two-column layout
    tutor_left, tutor_right = st.columns([3, 1])

    with tutor_right:
        st.subheader("💡 추천 질문")

        # RAG 기반 추천 질문 생성
        if st.session_state.get("rag_initialized", False):
            try:
                # RAG를 사용한 동적 추천 질문 생성
                dynamic_questions = get_suggested_questions_rag(
                    user_query=st.session_state.chat_history[-1]["content"] if st.session_state.chat_history else None,
                    level=st.session_state.level,
                    fallback_context=st.session_state.ppt_context[:2000]
                )
                # 아이콘과 함께 매핑
                icons = ["🎯", "📝", "🔍", "💭", "💡"]
                suggested_questions = [(icons[i % len(icons)], q) for i, q in enumerate(dynamic_questions[:4])]
            except:
                # 실패 시 기본 질문 사용
                suggested_questions = [
                    ("🎯", "핵심 개념 정리해줘"),
                    ("📝", "시험 포인트 3가지"),
                    ("🔍", "쉽게 설명해줘"),
                    ("💭", "예시를 들어줘")
                ]
        else:
            # RAG가 없으면 기본 질문
            suggested_questions = [
                ("🎯", "핵심 개념 정리해줘"),
                ("📝", "시험 포인트 3가지"),
                ("🔍", "쉽게 설명해줘"),
                ("💭", "예시를 들어줘")
            ]

        for icon, sq in suggested_questions:
            # 커스텀 스타일 버튼
            if st.button(f"{icon} {sq}", key=f"suggested_{sq}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": sq})
                with st.spinner("답변 생성 중..."):
                    # RAG 또는 기본 응답 사용
                    if st.session_state.get("rag_initialized", False):
                        response, sources = get_tutor_response_rag(
                            user_input=sq,
                            chat_history=st.session_state.chat_history[:-1],
                            level=st.session_state.level,
                            use_rag=True,
                            fallback_context=st.session_state.ppt_context,
                            session_id=st.session_state.get("session_id", "default")
                        )
                    else:
                        response = get_tutor_response(
                            sq,
                            st.session_state.ppt_context,
                            st.session_state.chat_history[:-1],
                            st.session_state.level
                        )
                        sources = []

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "sources": sources if st.session_state.get("rag_initialized", False) else []
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
                # RAG 또는 기본 응답 사용
                if st.session_state.get("rag_initialized", False):
                    response, sources = get_tutor_response_rag(
                        user_input=user_input,
                        chat_history=st.session_state.chat_history[:-1],
                        level=st.session_state.level,
                        use_rag=True,
                        fallback_context=st.session_state.ppt_context,
                        session_id=st.session_state.get("session_id", "default")
                    )
                else:
                    response = get_tutor_response(
                        user_input,
                        st.session_state.ppt_context,
                        st.session_state.chat_history[:-1],
                        st.session_state.level
                    )
                    sources = []

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "sources": sources if st.session_state.get("rag_initialized", False) else []
            })
            st.rerun()
