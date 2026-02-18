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
        st.subheader("학습 단계")
        for i, stage in enumerate(stages):
            if i < current_stage:
                st.success(f"완료: {stage}")
            elif i == current_stage:
                st.info(f"진행중: {stage}")
            else:
                st.markdown(f"대기: {stage}")

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
                # Progress Bar
                total_q = len(questions)
                answered_q = sum(1 for q in questions if q["id"] in st.session_state.quiz_answers)
                st.progress(answered_q / total_q if total_q > 0 else 0)
                st.caption(f"진행: {answered_q}/{total_q}")

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
