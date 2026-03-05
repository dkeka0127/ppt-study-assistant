"""Quiz Zone 탭 컴포넌트"""

import streamlit as st


def render_quiz():
    """Quiz Zone 탭 렌더링"""
    if not st.session_state.quizzes or all(len(stage.get("questions", [])) == 0 for stage in st.session_state.quizzes):
        st.warning("퀴즈가 생성되지 않았습니다. PPT 내용이 충분한지 확인해주세요.")
        return

    # Two-column layout: Quiz on left, Progress on right
    quiz_col, progress_col = st.columns([3, 1])

    stages = ["기초다지기", "실력다지기", "심화학습"]
    current_stage = st.session_state.current_quiz_stage

    with progress_col:
        st.subheader("🎯 학습 단계")

        # 단계별 진행 상황을 시각적으로 표시
        for i, stage in enumerate(stages):
            if i < current_stage:
                # 완료된 단계
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white;
                        padding: 1rem;
                        border-radius: 12px;
                        margin-bottom: 0.8rem;
                        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
                        animation: fadeIn 0.5s ease-out;
                    ">
                        <div style="font-weight: 600; font-size: 1rem; margin-bottom: 0.3rem;">
                            ✓ {stage}
                        </div>
                        <div style="font-size: 0.85rem; opacity: 0.9;">완료</div>
                    </div>
                """, unsafe_allow_html=True)
            elif i == current_stage:
                # 현재 진행 중인 단계
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 1rem;
                        border-radius: 12px;
                        margin-bottom: 0.8rem;
                        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                        animation: pulse 2s infinite;
                    ">
                        <div style="font-weight: 600; font-size: 1rem; margin-bottom: 0.3rem;">
                            ▶ {stage}
                        </div>
                        <div style="font-size: 0.85rem; opacity: 0.9;">진행 중</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # 대기 중인 단계
                st.markdown(f"""
                    <div style="
                        background: #f8f9fa;
                        color: #6c757d;
                        padding: 1rem;
                        border-radius: 12px;
                        margin-bottom: 0.8rem;
                        border: 2px dashed #dee2e6;
                    ">
                        <div style="font-weight: 600; font-size: 1rem; margin-bottom: 0.3rem;">
                            ○ {stage}
                        </div>
                        <div style="font-size: 0.85rem;">대기 중</div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Stage navigation
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if current_stage > 0:
                if st.button("이전", use_container_width=True):
                    st.session_state.current_quiz_stage -= 1
                    st.rerun()
        with nav_col2:
            if current_stage < len(stages) - 1:
                if st.button("다음", use_container_width=True):
                    st.session_state.current_quiz_stage += 1
                    st.rerun()

    with quiz_col:
        if current_stage < len(st.session_state.quizzes):
            stage_data = st.session_state.quizzes[current_stage]
            questions = stage_data.get("questions", [])

            if not questions:
                st.info(f"'{stage_data.get('stage', stages[current_stage])}' 단계에 문제가 없습니다.")
            else:
                # Enhanced Progress Bar
                total_q = len(questions)
                answered_q = sum(1 for q in questions if q["id"] in st.session_state.quiz_answers)
                progress_percent = (answered_q / total_q * 100) if total_q > 0 else 0

                st.markdown(f"""
                    <div style="
                        background: white;
                        padding: 1rem;
                        border-radius: 12px;
                        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
                        margin-bottom: 1.5rem;
                    ">
                        <div style="
                            display: flex;
                            justify-content: space-between;
                            margin-bottom: 0.5rem;
                        ">
                            <span style="font-weight: 600; color: #667eea;">진행 상황</span>
                            <span style="font-weight: 700; color: #667eea;">{answered_q}/{total_q}</span>
                        </div>
                        <div style="
                            height: 16px;
                            background: #e9ecef;
                            border-radius: 8px;
                            overflow: hidden;
                            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
                        ">
                            <div style="
                                width: {progress_percent}%;
                                height: 100%;
                                background: linear-gradient(90deg, #667eea, #764ba2);
                                border-radius: 8px;
                                transition: width 0.5s ease-out;
                                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
                            "></div>
                        </div>
                        <div style="
                            text-align: center;
                            margin-top: 0.5rem;
                            font-size: 0.9rem;
                            color: #6c757d;
                        ">
                            {progress_percent:.0f}% 완료
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Questions in card-style
                for q in questions:
                    with st.container():
                        q_header_col, q_source_col = st.columns([4, 1])
                        with q_header_col:
                            st.markdown(f"**Q{q['id']}** {q['question']}")
                        with q_source_col:
                            st.caption(f"Slide #{q.get('source_slide', '?')}")

                        q_key = f"q_{q['id']}"
                        q_type = q.get("type", "short_answer")

                        if q_type == "multiple_choice":
                            _render_multiple_choice(q, q_key)
                        elif q_type == "short_answer":
                            _render_short_answer(q, q_key)

                        st.markdown("---")

        else:
            st.success("모든 퀴즈를 완료했습니다!")
            reset_col1, reset_col2 = st.columns([1, 3])
            with reset_col1:
                if st.button("다시 풀기", type="primary"):
                    st.session_state.current_quiz_stage = 0
                    st.session_state.quiz_answers = {}
                    st.session_state.wrong_answers = []
                    st.session_state.feedback = None
                    st.rerun()


def _render_multiple_choice(q, q_key):
    """객관식 문제 렌더링"""
    options = q.get("options", [])
    if not options:
        return

    selected = st.session_state.quiz_answers.get(q["id"])
    cols = st.columns(len(options))

    for i, option in enumerate(options):
        with cols[i]:
            if selected is not None:
                if i == q.get("answer"):
                    st.markdown(f'''<button class="quiz-btn correct" disabled>{option}</button>''', unsafe_allow_html=True)
                elif selected == i:
                    st.markdown(f'''<button class="quiz-btn wrong" disabled>{option}</button>''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''<button class="quiz-btn" disabled>{option}</button>''', unsafe_allow_html=True)
            else:
                if st.button(option, key=f"{q_key}_opt_{i}", use_container_width=True):
                    st.session_state.quiz_answers[q["id"]] = i
                    if i != q.get("answer"):
                        st.session_state.wrong_answers.append({
                            "question": q,
                            "user_answer": option,
                            "correct_answer": options[q.get("answer", 0)]
                        })
                    st.rerun()


def _render_short_answer(q, q_key):
    """단답형 문제 렌더링"""
    if q["id"] in st.session_state.quiz_answers:
        user_ans = st.session_state.quiz_answers[q["id"]]
        correct_ans = q.get("answer", "")
        if user_ans.strip().lower() == correct_ans.strip().lower():
            st.success(f"정답: {user_ans}")
        else:
            st.error(f"오답 - 내 답변: {user_ans} / 정답: {correct_ans}")
    else:
        input_col, btn_col = st.columns([4, 1])
        with input_col:
            user_answer = st.text_input("답변", key=q_key, label_visibility="collapsed", placeholder="정답 입력")
        with btn_col:
            if st.button("제출", key=f"{q_key}_submit", use_container_width=True):
                st.session_state.quiz_answers[q["id"]] = user_answer
                correct_ans = q.get("answer", "")
                if user_answer.strip().lower() != correct_ans.strip().lower():
                    st.session_state.wrong_answers.append({
                        "question": q,
                        "user_answer": user_answer,
                        "correct_answer": correct_ans
                    })
                st.rerun()
