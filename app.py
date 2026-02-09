import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from modules.parser import extract_slide_content, get_all_text_content
from modules.generator import generate_summary, generate_quizzes, analyze_image, generate_feedback
from modules.chatbot import get_tutor_response, format_ppt_for_context

# Page configuration
st.set_page_config(
    page_title="Smart Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "processed" not in st.session_state:
    st.session_state.processed = False
if "slides_data" not in st.session_state:
    st.session_state.slides_data = []
if "summary" not in st.session_state:
    st.session_state.summary = None
if "quizzes" not in st.session_state:
    st.session_state.quizzes = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "wrong_answers" not in st.session_state:
    st.session_state.wrong_answers = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_quiz_stage" not in st.session_state:
    st.session_state.current_quiz_stage = 0
if "ppt_context" not in st.session_state:
    st.session_state.ppt_context = ""
if "level" not in st.session_state:
    st.session_state.level = "대학생"
if "feedback" not in st.session_state:
    st.session_state.feedback = None

# Check Bedrock configuration
bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
if not bearer_token:
    st.error("⚠️ AWS_BEARER_TOKEN_BEDROCK이 설정되지 않았습니다. 환경변수를 확인해주세요.")
    st.info("""
    **설정 방법 (Mac)**:
    ```bash
    export AWS_BEARER_TOKEN_BEDROCK="your-token"
    export AWS_REGION="us-west-2"
    export ANTHROPIC_MODEL="arn:aws:bedrock:..."
    ```
    """)
    st.stop()

# ============================================
# SIDEBAR: File Upload & Settings
# ============================================
with st.sidebar:
    st.header("📚 Smart Study Assistant")
    st.markdown("---")

    # File Uploader
    st.subheader("📁 파일 업로드")
    uploaded_file = st.file_uploader(
        "PPT 파일을 드래그하거나 클릭하여 업로드",
        type=["pptx"],
        help="PowerPoint 파일(.pptx)만 지원됩니다"
    )

    st.markdown("---")

    # Level Selector
    st.subheader("🎯 학습 설정")
    level = st.selectbox(
        "난이도 선택",
        options=["중학생", "고등학생", "대학생", "전문가"],
        index=2,
        help="선택한 수준에 맞춰 요약과 퀴즈가 생성됩니다"
    )

    # Quiz Configuration
    st.subheader("📝 퀴즈 설정")
    num_questions = st.slider(
        "문제 수",
        min_value=5,
        max_value=30,
        value=10,
        step=5
    )

    col1, col2 = st.columns(2)
    with col1:
        include_multiple_choice = st.checkbox("객관식", value=True)
    with col2:
        include_short_answer = st.checkbox("단답형", value=True)

    col3, col4 = st.columns(2)
    with col3:
        include_fill_blank = st.checkbox("빈칸 채우기", value=True)
    with col4:
        include_essay = st.checkbox("서술형", value=False)

    st.markdown("---")

    # Process Button
    process_btn = st.button(
        "🚀 학습 자료 생성 시작",
        type="primary",
        use_container_width=True,
        disabled=uploaded_file is None
    )

    if process_btn and uploaded_file:
        # Reset previous state
        st.session_state.quiz_answers = {}
        st.session_state.wrong_answers = []
        st.session_state.current_quiz_stage = 0
        st.session_state.chat_history = []
        st.session_state.feedback = None
        st.session_state.level = level

        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Step 1: Parse PPT
            status_text.text("📄 PPT 파일 분석 중...")
            progress_bar.progress(10)

            slides_data = extract_slide_content(uploaded_file)
            st.session_state.slides_data = slides_data
            progress_bar.progress(30)

            # Step 2: Analyze images (if any)
            status_text.text("🖼️ 이미지 분석 중...")
            for slide in slides_data:
                if slide.get("images"):
                    slide_text = "\n".join(slide.get("texts", []))
                    # Analyze only the first image per slide to save API calls
                    if slide["images"]:
                        analysis = analyze_image(slide["images"][0], slide_text)
                        slide["vision_analysis"] = analysis
            progress_bar.progress(50)

            # Step 3: Generate summary
            status_text.text("📝 요약 생성 중...")
            summary = generate_summary(slides_data, level)
            st.session_state.summary = summary
            progress_bar.progress(70)

            # Step 4: Generate quizzes
            status_text.text("✍️ 퀴즈 생성 중...")
            include_types = {
                "multiple_choice": include_multiple_choice,
                "short_answer": include_short_answer,
                "fill_blank": include_fill_blank,
                "essay": include_essay
            }
            quizzes = generate_quizzes(slides_data, level, num_questions, include_types)
            st.session_state.quizzes = quizzes
            progress_bar.progress(90)

            # Step 5: Prepare chatbot context
            status_text.text("🤖 AI 튜터 준비 중...")
            st.session_state.ppt_context = format_ppt_for_context(slides_data)
            progress_bar.progress(100)

            st.session_state.processed = True
            status_text.text("✅ 완료!")
            st.success("✅ 학습 자료 생성 완료!")

        except Exception as e:
            st.error(f"❌ 오류 발생: {str(e)}")
            progress_bar.empty()
            status_text.empty()

    # Learning Progress
    if st.session_state.processed:
        st.markdown("---")
        st.subheader("📊 학습 진척도")

        total_questions = sum(len(stage["questions"]) for stage in st.session_state.quizzes)
        answered = len(st.session_state.quiz_answers)
        progress = answered / total_questions if total_questions > 0 else 0

        st.progress(progress)
        st.caption(f"퀴즈 진행: {answered}/{total_questions} 문제")

        if st.session_state.wrong_answers:
            wrong_count = len(st.session_state.wrong_answers)
            st.metric("오답 수", wrong_count)

# ============================================
# MAIN PANEL: Tabs
# ============================================
st.title("📚 Smart Study Assistant")
st.markdown("AI 기반 PPT 학습 도우미 - 핵심 정리, 퀴즈, 오답 노트, AI 튜터")

if not st.session_state.processed:
    st.info("👈 사이드바에서 PPT 파일을 업로드하고 '학습 자료 생성 시작' 버튼을 클릭하세요.")

    # Show placeholder content
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("### 📊 Dashboard")
        st.markdown("PPT 요약 및 핵심 분석")
    with col2:
        st.markdown("### ✍️ Quiz Zone")
        st.markdown("맞춤형 퀴즈 풀이")
    with col3:
        st.markdown("### 📝 Review Note")
        st.markdown("오답 노트 & 피드백")
    with col4:
        st.markdown("### 🤖 AI Tutor")
        st.markdown("실시간 Q&A 챗봇")

else:
    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "✍️ Quiz Zone",
        "📝 Review Note",
        "🤖 AI Tutor"
    ])

    # ============================================
    # TAB 1: Dashboard (학습자료 요약)
    # ============================================
    with tab1:
        st.header("📊 학습자료 요약")

        # Overall Summary Card
        st.subheader("📌 전체 요약")
        summary_col1, summary_col2 = st.columns([2, 1])

        with summary_col1:
            st.info(st.session_state.summary.get("one_line", "요약 정보가 없습니다."))

        with summary_col2:
            st.markdown("**핵심 키워드**")
            keywords = st.session_state.summary.get("keywords", [])
            if keywords:
                keywords_html = " ".join([f"`{kw}`" for kw in keywords])
                st.markdown(keywords_html)
            else:
                st.caption("키워드가 없습니다.")

        st.markdown("---")

        # Slide-by-slide Cards
        st.subheader("📑 슬라이드별 분석")

        # Get slide summaries from summary data
        slide_summaries = {
            s["slide_num"]: s
            for s in st.session_state.summary.get("slide_summaries", [])
        }

        for slide in st.session_state.slides_data:
            slide_num = slide["slide_num"]
            slide_summary = slide_summaries.get(slide_num, {})
            title = slide_summary.get("title", f"슬라이드 {slide_num}")

            with st.expander(f"📄 Slide #{slide_num}: {title}", expanded=False):
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("**📝 핵심 내용**")

                    # Show AI-generated key points if available
                    key_points = slide_summary.get("key_points", [])
                    if key_points:
                        for point in key_points:
                            st.markdown(f"• {point}")
                    elif slide["texts"]:
                        # Show original text content without truncation
                        for text in slide["texts"][:7]:
                            # Display full text or truncate very long texts
                            if len(text) > 500:
                                st.markdown(f"- {text[:500]}...")
                            else:
                                st.markdown(f"- {text}")
                    else:
                        st.caption("텍스트 내용이 없습니다.")

                with col2:
                    st.markdown("**🖼️ Vision AI 분석**")
                    if slide.get("vision_analysis"):
                        st.markdown(slide["vision_analysis"])
                    else:
                        st.caption("이미지 분석 결과가 없습니다.")

                    # Show image count
                    if slide.get("images"):
                        st.caption(f"📷 이미지 {len(slide['images'])}개 포함")

    # ============================================
    # TAB 2: Quiz Zone (학습 확인)
    # ============================================
    with tab2:
        st.header("✍️ Quiz Zone")

        if not st.session_state.quizzes or all(len(stage.get("questions", [])) == 0 for stage in st.session_state.quizzes):
            st.warning("퀴즈가 생성되지 않았습니다. PPT 내용이 충분한지 확인해주세요.")
        else:
            # Stage Progress
            stages = ["어휘다지기", "실력다지기", "심화학습"]
            current_stage = st.session_state.current_quiz_stage

            # Progress indicator
            progress_cols = st.columns(3)
            for i, stage in enumerate(stages):
                with progress_cols[i]:
                    if i < current_stage:
                        st.success(f"✅ {stage}")
                    elif i == current_stage:
                        st.info(f"▶️ {stage}")
                    else:
                        st.markdown(f"⬜ {stage}")

            st.markdown("---")

            # Current Stage Questions
            if current_stage < len(st.session_state.quizzes):
                stage_data = st.session_state.quizzes[current_stage]
                questions = stage_data.get("questions", [])

                if not questions:
                    st.info(f"'{stage_data.get('stage', stages[current_stage])}' 단계에 문제가 없습니다.")
                    col1, col2 = st.columns(2)
                    with col2:
                        if current_stage < len(stages) - 1:
                            if st.button("다음 단계 ➡️"):
                                st.session_state.current_quiz_stage += 1
                                st.rerun()
                else:
                    st.subheader(f"📝 {stage_data.get('stage', stages[current_stage])}")

                    # Progress Bar
                    total_q = len(questions)
                    answered_q = sum(1 for q in questions if q["id"] in st.session_state.quiz_answers)
                    st.progress(answered_q / total_q if total_q > 0 else 0)
                    st.caption(f"진행: {answered_q}/{total_q} 문제")

                    # Questions
                    for q in questions:
                        st.markdown(f"**문제 {q['id']}** (출처: Slide #{q.get('source_slide', '?')})")
                        st.markdown(q["question"])

                        q_key = f"q_{q['id']}"
                        q_type = q.get("type", "short_answer")

                        if q_type == "multiple_choice":
                            options = q.get("options", [])
                            if options:
                                selected = st.session_state.quiz_answers.get(q["id"])

                                cols = st.columns(len(options))
                                for i, option in enumerate(options):
                                    with cols[i]:
                                        if selected is not None:
                                            if i == q.get("answer"):
                                                st.success(f"✅ {option}")
                                            elif selected == i:
                                                st.error(f"❌ {option}")
                                            else:
                                                st.button(option, key=f"{q_key}_opt_{i}", disabled=True)
                                        else:
                                            if st.button(option, key=f"{q_key}_opt_{i}"):
                                                st.session_state.quiz_answers[q["id"]] = i
                                                if i != q.get("answer"):
                                                    st.session_state.wrong_answers.append({
                                                        "question": q,
                                                        "user_answer": option,
                                                        "correct_answer": options[q.get("answer", 0)]
                                                    })
                                                st.rerun()

                        elif q_type in ["short_answer", "fill_blank"]:
                            if q["id"] in st.session_state.quiz_answers:
                                user_ans = st.session_state.quiz_answers[q["id"]]
                                correct_ans = q.get("answer", "")
                                if user_ans.strip().lower() == correct_ans.strip().lower():
                                    st.success(f"✅ 정답입니다! ({user_ans})")
                                else:
                                    st.error(f"❌ 오답입니다. 내 답변: {user_ans} / 정답: {correct_ans}")
                            else:
                                user_answer = st.text_input("답변 입력", key=q_key)
                                if st.button("제출", key=f"{q_key}_submit"):
                                    st.session_state.quiz_answers[q["id"]] = user_answer
                                    correct_ans = q.get("answer", "")
                                    if user_answer.strip().lower() != correct_ans.strip().lower():
                                        st.session_state.wrong_answers.append({
                                            "question": q,
                                            "user_answer": user_answer,
                                            "correct_answer": correct_ans
                                        })
                                    st.rerun()

                        elif q_type == "essay":
                            if q["id"] in st.session_state.quiz_answers:
                                st.info("✅ 답변이 제출되었습니다.")
                                st.text_area("제출된 답변", value=st.session_state.quiz_answers[q["id"]], disabled=True, height=100)
                            else:
                                user_answer = st.text_area("답변 작성", key=q_key, height=150)
                                if st.button("제출", key=f"{q_key}_submit"):
                                    st.session_state.quiz_answers[q["id"]] = user_answer
                                    st.rerun()

                        st.markdown("---")

                    # Stage Navigation
                    col1, col2 = st.columns(2)
                    with col1:
                        if current_stage > 0:
                            if st.button("⬅️ 이전 단계"):
                                st.session_state.current_quiz_stage -= 1
                                st.rerun()
                    with col2:
                        if current_stage < len(stages) - 1:
                            if st.button("다음 단계 ➡️"):
                                st.session_state.current_quiz_stage += 1
                                st.rerun()
            else:
                st.success("🎉 모든 퀴즈를 완료했습니다!")
                if st.button("처음부터 다시 풀기"):
                    st.session_state.current_quiz_stage = 0
                    st.session_state.quiz_answers = {}
                    st.session_state.wrong_answers = []
                    st.session_state.feedback = None
                    st.rerun()

    # ============================================
    # TAB 3: Review Note (오답 노트 & 피드백)
    # ============================================
    with tab3:
        st.header("📝 Review Note")

        if not st.session_state.wrong_answers:
            st.success("🎉 오답이 없습니다! 훌륭합니다!")
        else:
            # Generate AI feedback button
            if st.session_state.feedback is None:
                if st.button("🔍 AI 취약점 분석 받기", type="primary"):
                    with st.spinner("AI가 학습 패턴을 분석 중입니다..."):
                        feedback = generate_feedback(
                            st.session_state.wrong_answers,
                            st.session_state.slides_data
                        )
                        st.session_state.feedback = feedback
                    st.rerun()

            # Show AI Feedback if available
            if st.session_state.feedback:
                st.subheader("🎯 AI 학습 분석")

                feedback = st.session_state.feedback
                st.info(feedback.get("analysis", ""))

                # Weak areas
                weak_areas = feedback.get("weak_areas", [])
                if weak_areas:
                    st.markdown("**📉 취약 영역**")
                    for area in weak_areas:
                        with st.expander(f"🔸 {area.get('area', '영역')}"):
                            st.write(area.get("description", ""))
                            related = area.get("related_slides", [])
                            if related:
                                st.caption(f"관련 슬라이드: {', '.join(map(str, related))}")

                # Recommendations
                recommendations = feedback.get("recommendations", [])
                if recommendations:
                    st.markdown("**💡 학습 추천**")
                    for rec in recommendations:
                        st.markdown(f"• {rec}")

                st.markdown("---")

            # Wrong Answers Table
            st.subheader("❌ 오답 목록")

            for i, wrong in enumerate(st.session_state.wrong_answers):
                q = wrong["question"]
                with st.expander(f"문제 {q['id']}: {q['question'][:50]}...", expanded=True):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("**내 답변**")
                        st.error(wrong["user_answer"])

                    with col2:
                        st.markdown("**정답**")
                        st.success(wrong["correct_answer"])

                    with col3:
                        st.markdown("**출처**")
                        slide_num = q.get("source_slide", "?")
                        st.info(f"📄 Slide #{slide_num}")

                    # AI Explanation
                    st.markdown("**💡 AI 해설**")
                    st.info(q.get("explanation", "해설이 없습니다."))

            st.markdown("---")

            # Statistics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("총 오답 수", len(st.session_state.wrong_answers))
            with col2:
                total_q = sum(len(stage.get("questions", [])) for stage in st.session_state.quizzes)
                answered = len(st.session_state.quiz_answers)
                if answered > 0:
                    accuracy = ((answered - len(st.session_state.wrong_answers)) / answered * 100)
                    st.metric("정답률", f"{accuracy:.1f}%")

    # ============================================
    # TAB 4: AI Tutor (실시간 Q&A)
    # ============================================
    with tab4:
        st.header("🤖 AI Tutor")
        st.markdown("PPT 내용에 대해 궁금한 점을 자유롭게 질문하세요.")

        # Suggested Questions
        st.subheader("💡 추천 질문")
        suggested_cols = st.columns(3)
        suggested_questions = [
            "이 주제의 핵심 개념이 뭐야?",
            "시험에 나올만한 중요 문장 3개만 뽑아줘",
            "이 내용을 쉽게 설명해줘"
        ]

        for i, sq in enumerate(suggested_questions):
            with suggested_cols[i]:
                if st.button(sq, key=f"suggested_{i}", use_container_width=True):
                    st.session_state.chat_history.append({"role": "user", "content": sq})

                    with st.spinner("AI 튜터가 답변을 작성 중..."):
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

        # Chat History
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.chat_message("user").write(msg["content"])
                else:
                    st.chat_message("assistant").write(msg["content"])

        # Chat Input
        user_input = st.chat_input("질문을 입력하세요...")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            with st.spinner("AI 튜터가 답변을 작성 중..."):
                response = get_tutor_response(
                    user_input,
                    st.session_state.ppt_context,
                    st.session_state.chat_history[:-1],
                    st.session_state.level
                )

            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

        # Clear Chat Button
        if st.session_state.chat_history:
            if st.button("🗑️ 대화 내역 지우기"):
                st.session_state.chat_history = []
                st.rerun()
