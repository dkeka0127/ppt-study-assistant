"""Review Note 탭 컴포넌트"""

import streamlit as st
from modules.generator import generate_feedback


def render_review():
    """Review Note 탭 렌더링"""
    if not st.session_state.wrong_answers:
        st.success("오답이 없습니다!")
        return

    # Two-column layout
    review_left, review_right = st.columns([2, 1])

    with review_right:
        st.subheader("학습 통계")

        # Statistics
        total_q = sum(len(stage.get("questions", [])) for stage in st.session_state.quizzes)
        answered = len(st.session_state.quiz_answers)
        wrong_count = len(st.session_state.wrong_answers)

        st.metric("오답 수", wrong_count)
        if answered > 0:
            accuracy = ((answered - wrong_count) / answered * 100)
            st.metric("정답률", f"{accuracy:.1f}%")

        st.markdown("---")

        # AI feedback button
        if st.session_state.feedback is None:
            if st.button("AI 취약점 분석", type="primary", use_container_width=True):
                with st.spinner("학습 패턴 분석 중..."):
                    feedback = generate_feedback(
                        st.session_state.wrong_answers,
                        st.session_state.slides_data
                    )
                    st.session_state.feedback = feedback
                st.rerun()

        # Show AI Feedback if available
        if st.session_state.feedback:
            st.subheader("AI 분석 결과")
            feedback = st.session_state.feedback
            st.info(feedback.get("analysis", ""))

            weak_areas = feedback.get("weak_areas", [])
            if weak_areas:
                st.markdown("**취약 영역**")
                for area in weak_areas:
                    st.warning(area.get("area", "영역"))
                    st.caption(area.get("description", ""))

            recommendations = feedback.get("recommendations", [])
            if recommendations:
                st.markdown("**학습 추천**")
                for rec in recommendations:
                    st.markdown(f"- {rec}")

    with review_left:
        st.subheader("오답 목록")

        for i, wrong in enumerate(st.session_state.wrong_answers):
            q = wrong["question"]
            with st.expander(f"Q{q['id']}: {q['question'][:60]}...", expanded=(i == 0)):
                ans_col1, ans_col2 = st.columns(2)

                with ans_col1:
                    st.markdown("**내 답변**")
                    st.error(wrong["user_answer"])

                with ans_col2:
                    st.markdown("**정답**")
                    st.success(wrong["correct_answer"])

                # AI Explanation
                st.markdown("**해설**")
                st.info(q.get("explanation", "해설이 없습니다."))

                st.caption(f"출처: Slide #{q.get('source_slide', '?')}")
