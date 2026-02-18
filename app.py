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
    initial_sidebar_state="collapsed"
)

# Custom CSS for PC optimization
st.markdown("""
<style>
    /* Main container optimization */
    .main .block-container {
        max-width: 1400px;
        padding: 1rem 2rem;
    }

    /* Card style for sections */
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }

    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        border-radius: 8px 8px 0 0;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }

    [data-testid="stMetric"] label {
        color: rgba(255,255,255,0.8) !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important;
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 12px;
        margin: 0.5rem 0;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 1rem;
    }

    /* Hide sidebar toggle on PC */
    @media (min-width: 1024px) {
        [data-testid="collapsedControl"] {
            display: none;
        }
    }

    /* Quick stats bar */
    .quick-stats {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

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
if "auto_process" not in st.session_state:
    st.session_state.auto_process = True
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

# Check Bedrock configuration
bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
if not bearer_token:
    st.error("AWS_BEARER_TOKEN_BEDROCK이 설정되지 않았습니다.")
    with st.expander("설정 방법 보기"):
        st.code("""
export AWS_BEARER_TOKEN_BEDROCK="your-token"
export AWS_REGION="us-west-2"
export ANTHROPIC_MODEL="arn:aws:bedrock:..."
        """, language="bash")
    st.stop()


# ============================================
# Helper function for processing
# ============================================
def process_ppt(uploaded_file, level, num_questions, include_types):
    """Process PPT file and generate study materials"""
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
        status_text.text("PPT 파일 분석 중...")
        progress_bar.progress(10)

        slides_data = extract_slide_content(uploaded_file)
        st.session_state.slides_data = slides_data
        progress_bar.progress(30)

        # Step 2: Analyze images (if any)
        status_text.text("이미지 분석 중...")
        for slide in slides_data:
            if slide.get("images"):
                slide_text = "\n".join(slide.get("texts", []))
                if slide["images"]:
                    analysis = analyze_image(slide["images"][0], slide_text)
                    slide["vision_analysis"] = analysis
        progress_bar.progress(50)

        # Step 3: Generate summary
        status_text.text("요약 생성 중...")
        summary = generate_summary(slides_data, level)
        st.session_state.summary = summary
        progress_bar.progress(70)

        # Step 4: Generate quizzes
        status_text.text("퀴즈 생성 중...")
        quizzes = generate_quizzes(slides_data, level, num_questions, include_types)
        st.session_state.quizzes = quizzes
        progress_bar.progress(90)

        # Step 5: Prepare chatbot context
        status_text.text("AI 튜터 준비 중...")
        st.session_state.ppt_context = format_ppt_for_context(slides_data)
        progress_bar.progress(100)

        st.session_state.processed = True
        status_text.empty()
        progress_bar.empty()
        return True

    except Exception as e:
        st.error(f"오류 발생: {str(e)}")
        progress_bar.empty()
        status_text.empty()
        return False

# ============================================
# MAIN PANEL
# ============================================

# Header with title and quick actions
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("Smart Study Assistant")
with header_col2:
    if st.session_state.processed:
        if st.button("새 파일 업로드", use_container_width=True):
            st.session_state.processed = False
            st.session_state.slides_data = []
            st.session_state.summary = None
            st.session_state.quizzes = []
            st.rerun()

# ============================================
# NOT PROCESSED: Upload & Settings View
# ============================================
if not st.session_state.processed:
    st.markdown("AI 기반 PPT 학습 도우미 - 파일을 업로드하면 자동으로 학습 자료가 생성됩니다.")

    # Main upload area with settings
    upload_col, settings_col = st.columns([2, 1])

    with upload_col:
        st.subheader("파일 업로드")
        uploaded_file = st.file_uploader(
            "PPT 파일을 드래그하거나 클릭하여 업로드",
            type=["pptx"],
            help="PowerPoint 파일(.pptx)만 지원됩니다",
            label_visibility="collapsed"
        )

        # Feature preview cards
        st.markdown("---")
        st.markdown("##### 생성되는 학습 자료")
        feat_cols = st.columns(4)
        features = [
            ("📊 Dashboard", "핵심 요약 & 분석"),
            ("✍️ Quiz Zone", "맞춤형 퀴즈"),
            ("📝 Review Note", "오답 노트"),
            ("🤖 AI Tutor", "실시간 Q&A")
        ]
        for i, (title, desc) in enumerate(features):
            with feat_cols[i]:
                st.markdown(f"**{title}**")
                st.caption(desc)

    with settings_col:
        st.subheader("학습 설정")

        # Level selector
        level = st.selectbox(
            "난이도",
            options=["중학생", "고등학생", "대학생", "전문가"],
            index=2
        )

        # Quiz settings
        num_questions = st.slider("문제 수", 5, 30, 10, 5)

        with st.expander("퀴즈 유형 선택", expanded=False):
            include_multiple_choice = st.checkbox("객관식", value=True, help="4지선다 객관식")
            include_short_answer = st.checkbox("단답형", value=True, help="1~3단어 짧은 답변")

        # Auto-process toggle
        st.session_state.auto_process = st.checkbox(
            "자동 생성",
            value=True,
            help="파일 업로드 시 자동으로 학습 자료 생성"
        )

    # Process when file is uploaded
    if uploaded_file:
        include_types = {
            "multiple_choice": include_multiple_choice if 'include_multiple_choice' in dir() else True,
            "short_answer": include_short_answer if 'include_short_answer' in dir() else True
        }

        if st.session_state.auto_process:
            # Auto process
            with st.container():
                if process_ppt(uploaded_file, level, num_questions, include_types):
                    st.rerun()
        else:
            # Manual process button
            if st.button("학습 자료 생성", type="primary", use_container_width=True):
                if process_ppt(uploaded_file, level, num_questions, include_types):
                    st.rerun()

# ============================================
# PROCESSED: Main Study View
# ============================================
else:
    # Quick Stats Bar
    total_questions = sum(len(stage.get("questions", [])) for stage in st.session_state.quizzes)
    answered = len(st.session_state.quiz_answers)
    wrong_count = len(st.session_state.wrong_answers)
    accuracy = ((answered - wrong_count) / answered * 100) if answered > 0 else 0

    stat_cols = st.columns(5)
    with stat_cols[0]:
        st.metric("슬라이드", f"{len(st.session_state.slides_data)}장")
    with stat_cols[1]:
        st.metric("총 문제", f"{total_questions}개")
    with stat_cols[2]:
        st.metric("진행률", f"{answered}/{total_questions}")
    with stat_cols[3]:
        st.metric("오답", f"{wrong_count}개")
    with stat_cols[4]:
        st.metric("정답률", f"{accuracy:.0f}%")

    st.markdown("---")

    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Dashboard",
        "Quiz Zone",
        "Review Note",
        "AI Tutor"
    ])

    # ============================================
    # TAB 1: Dashboard (학습자료 요약)
    # ============================================
    with tab1:
        # Two-column layout for dashboard
        dash_left, dash_right = st.columns([2, 1])

        with dash_left:
            st.subheader("전체 요약")
            st.info(st.session_state.summary.get("one_line", "요약 정보가 없습니다."))

            # Slide-by-slide Cards
            st.subheader("슬라이드별 분석")

            # Get slide summaries from summary data
            slide_summaries = {
                s["slide_num"]: s
                for s in st.session_state.summary.get("slide_summaries", [])
            }

            for slide in st.session_state.slides_data:
                slide_num = slide["slide_num"]
                slide_summary = slide_summaries.get(slide_num, {})
                title = slide_summary.get("title", f"슬라이드 {slide_num}")

                with st.expander(f"Slide #{slide_num}: {title}", expanded=False):
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.markdown("**핵심 내용**")
                        key_points = slide_summary.get("key_points", [])
                        if key_points:
                            for point in key_points:
                                st.markdown(f"- {point}")
                        elif slide["texts"]:
                            for text in slide["texts"][:5]:
                                display_text = text[:300] + "..." if len(text) > 300 else text
                                st.markdown(f"- {display_text}")
                        else:
                            st.caption("텍스트 내용이 없습니다.")

                    with col2:
                        st.markdown("**Vision AI 분석**")
                        if slide.get("vision_analysis"):
                            st.markdown(slide["vision_analysis"])
                        else:
                            st.caption("이미지 분석 결과가 없습니다.")

                        if slide.get("images"):
                            st.caption(f"이미지 {len(slide['images'])}개 포함")

        with dash_right:
            # Keywords section
            st.subheader("핵심 키워드")
            keywords = st.session_state.summary.get("keywords", [])
            if keywords:
                for kw in keywords:
                    st.markdown(f"`{kw}`")
            else:
                st.caption("키워드가 없습니다.")

            st.markdown("---")

            # Quick navigation
            st.subheader("바로가기")
            if st.button("퀴즈 풀기", use_container_width=True):
                st.query_params["tab"] = "quiz"
                st.rerun()
            if st.button("AI 튜터에게 질문", use_container_width=True):
                st.query_params["tab"] = "tutor"
                st.rerun()

            if st.session_state.wrong_answers:
                st.markdown("---")
                st.warning(f"오답 {len(st.session_state.wrong_answers)}개가 있습니다.")
                if st.button("오답 노트 확인", use_container_width=True):
                    st.query_params["tab"] = "review"
                    st.rerun()

    # ============================================
    # TAB 2: Quiz Zone (학습 확인)
    # ============================================
    with tab2:
        if not st.session_state.quizzes or all(len(stage.get("questions", [])) == 0 for stage in st.session_state.quizzes):
            st.warning("퀴즈가 생성되지 않았습니다. PPT 내용이 충분한지 확인해주세요.")
        else:
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
                                    options = q.get("options", [])
                                    if options:
                                        selected = st.session_state.quiz_answers.get(q["id"])
                                        cols = st.columns(len(options))
                                        for i, option in enumerate(options):
                                            with cols[i]:
                                                if selected is not None:
                                                    if i == q.get("answer"):
                                                        st.success(option)
                                                    elif selected == i:
                                                        st.error(option)
                                                    else:
                                                        st.button(option, key=f"{q_key}_opt_{i}", disabled=True)
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

                                elif q_type == "short_answer":
                                    # 단답형: 간단한 입력 필드
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

    # ============================================
    # TAB 3: Review Note (오답 노트 & 피드백)
    # ============================================
    with tab3:
        if not st.session_state.wrong_answers:
            st.success("오답이 없습니다!")
            st.balloons()
        else:
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

    # ============================================
    # TAB 4: AI Tutor (실시간 Q&A)
    # ============================================
    with tab4:
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
