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
        st.subheader("📈 학습 통계")

        # Statistics
        total_q = sum(len(stage.get("questions", [])) for stage in st.session_state.quizzes)
        answered = len(st.session_state.quiz_answers)
        wrong_count = len(st.session_state.wrong_answers)
        correct_count = answered - wrong_count

        # 정답률 계산
        if answered > 0:
            accuracy = ((answered - wrong_count) / answered * 100)
        else:
            accuracy = 0

        # 원형 진행률 표시
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                padding: 1.5rem;
                border-radius: 16px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
                text-align: center;
                margin-bottom: 1rem;
            ">
                <div style="
                    width: 120px;
                    height: 120px;
                    margin: 0 auto 1rem;
                    border-radius: 50%;
                    background: conic-gradient(
                        #28a745 0deg {accuracy * 3.6}deg,
                        #e9ecef {accuracy * 3.6}deg 360deg
                    );
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 16px rgba(40, 167, 69, 0.2);
                ">
                    <div style="
                        width: 90px;
                        height: 90px;
                        border-radius: 50%;
                        background: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.8rem;
                        font-weight: 700;
                        color: #28a745;
                    ">
                        {accuracy:.0f}%
                    </div>
                </div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #333; margin-bottom: 0.5rem;">
                    정답률
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 통계 바 차트
        st.markdown(f"""
            <div style="
                background: white;
                padding: 1rem;
                border-radius: 12px;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
                margin-bottom: 1rem;
            ">
                <div style="margin-bottom: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                        <span style="font-weight: 600; color: #28a745;">✓ 정답</span>
                        <span style="font-weight: 600; color: #28a745;">{correct_count}</span>
                    </div>
                    <div style="
                        height: 12px;
                        background: #e9ecef;
                        border-radius: 6px;
                        overflow: hidden;
                    ">
                        <div style="
                            width: {(correct_count / answered * 100) if answered > 0 else 0}%;
                            height: 100%;
                            background: linear-gradient(90deg, #28a745, #20c997);
                            transition: width 1s ease-out;
                        "></div>
                    </div>
                </div>
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                        <span style="font-weight: 600; color: #dc3545;">✗ 오답</span>
                        <span style="font-weight: 600; color: #dc3545;">{wrong_count}</span>
                    </div>
                    <div style="
                        height: 12px;
                        background: #e9ecef;
                        border-radius: 6px;
                        overflow: hidden;
                    ">
                        <div style="
                            width: {(wrong_count / answered * 100) if answered > 0 else 0}%;
                            height: 100%;
                            background: linear-gradient(90deg, #dc3545, #f5576c);
                            transition: width 1s ease-out;
                        "></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

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
