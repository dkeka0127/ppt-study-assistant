"""Smart Study Assistant - 메인 애플리케이션"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from modules.parser import extract_slide_content
from modules.generator import generate_summary, generate_quizzes, analyze_image
from modules.chatbot import format_ppt_for_context

# Import components
from components import render_dashboard, render_quiz, render_review, render_tutor
from config import CUSTOM_CSS

# Page configuration
st.set_page_config(
    page_title="Smart Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================
# Session State 초기화
# ============================================
def init_session_state():
    """Session state 초기화"""
    defaults = {
        "processed": False,
        "slides_data": [],
        "summary": None,
        "quizzes": [],
        "quiz_answers": {},
        "quiz_submitted": False,
        "wrong_answers": [],
        "chat_history": [],
        "current_quiz_stage": 0,
        "ppt_context": "",
        "level": "대학생",
        "feedback": None,
        "auto_process": True,
        "show_settings": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ============================================
# PPT 처리 함수
# ============================================
def process_ppt(uploaded_file, level, num_questions, include_types):
    """PPT 파일 처리 및 학습 자료 생성"""
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
        status_text.markdown("### 📄 PPT 파일 분석 중...")
        progress_bar.progress(10)
        slides_data = extract_slide_content(uploaded_file)
        st.session_state.slides_data = slides_data
        progress_bar.progress(30)

        # Step 2: Analyze images
        status_text.markdown("### 🔍 이미지 분석 중...")
        for slide in slides_data:
            if slide.get("images"):
                slide_text = "\n".join(slide.get("texts", []))
                if slide["images"]:
                    analysis = analyze_image(slide["images"][0], slide_text)
                    slide["vision_analysis"] = analysis
        progress_bar.progress(50)

        # Step 3: Generate summary
        status_text.markdown("### 📝 요약 생성 중...")
        summary = generate_summary(slides_data, level)
        st.session_state.summary = summary
        progress_bar.progress(70)

        # Step 4: Generate quizzes
        status_text.markdown("### ✍️ 퀴즈 생성 중...")
        quizzes = generate_quizzes(slides_data, level, num_questions, include_types)
        st.session_state.quizzes = quizzes
        progress_bar.progress(90)

        # Step 5: Prepare chatbot context
        status_text.markdown("### 🤖 AI 튜터 준비 중...")
        st.session_state.ppt_context = format_ppt_for_context(slides_data)
        progress_bar.progress(100)

        st.session_state.processed = True
        progress_bar.progress(100)
        status_text.markdown("### ✅ 학습 자료 생성 완료!")
        st.success("🎉 모든 준비가 완료되었습니다! 이제 학습을 시작하세요.")
        st.balloons()
        status_text.empty()
        progress_bar.empty()
        return True

    except Exception as e:
        st.error(f"오류 발생: {str(e)}")
        progress_bar.empty()
        status_text.empty()
        return False


# ============================================
# 환경 설정 체크
# ============================================
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
# 메인 UI
# ============================================

# Header
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
# 업로드 화면 (처리 전)
# ============================================
if not st.session_state.processed:
    st.markdown("AI 기반 PPT 학습 도우미 - 파일을 업로드하면 자동으로 학습 자료가 생성됩니다.")

    upload_col, settings_col = st.columns([2, 1])

    with upload_col:
        st.subheader("파일 업로드")
        uploaded_file = st.file_uploader(
            "PPT 파일을 드래그하거나 클릭하여 업로드",
            type=["pptx"],
            help="PowerPoint 파일(.pptx)만 지원됩니다",
            label_visibility="collapsed"
        )

        # Feature preview with enhanced cards
        st.markdown("---")
        st.markdown("##### ✨ 생성되는 학습 자료")
        feat_cols = st.columns(4)
        features = [
            ("📊", "Dashboard", "핵심 요약 & 분석", "#667eea"),
            ("✍️", "Quiz Zone", "맞춤형 퀴즈", "#f093fb"),
            ("📝", "Review Note", "오답 노트", "#4facfe"),
            ("🤖", "AI Tutor", "실시간 Q&A", "#43e97b")
        ]
        for i, (icon, title, desc, color) in enumerate(features):
            with feat_cols[i]:
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, {color}22 0%, {color}44 100%);
                        border: 2px solid {color};
                        border-radius: 12px;
                        padding: 1.2rem;
                        text-align: center;
                        transition: all 0.3s ease;
                        animation: fadeIn 0.5s ease-out;
                        animation-delay: {i * 0.1}s;
                        opacity: 0;
                        animation-fill-mode: forwards;
                    ">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                        <div style="font-weight: 700; font-size: 1rem; margin-bottom: 0.3rem; color: #333;">
                            {title}
                        </div>
                        <div style="font-size: 0.85rem; color: #666;">{desc}</div>
                    </div>
                """, unsafe_allow_html=True)

    with settings_col:
        st.subheader("학습 설정")
        level = st.selectbox(
            "난이도",
            options=["중학생", "고등학생", "대학생", "전문가"],
            index=2
        )
        num_questions = st.slider("문제 수", 5, 30, 10, 5)

        with st.expander("퀴즈 유형 선택", expanded=False):
            include_multiple_choice = st.checkbox("객관식", value=True, help="4지선다 객관식")
            include_short_answer = st.checkbox("단답형", value=True, help="1~3단어 짧은 답변")

        st.session_state.auto_process = st.checkbox(
            "자동 생성",
            value=True,
            help="파일 업로드 시 자동으로 학습 자료 생성"
        )

    # Process file
    if uploaded_file:
        include_types = {
            "multiple_choice": include_multiple_choice if 'include_multiple_choice' in dir() else True,
            "short_answer": include_short_answer if 'include_short_answer' in dir() else True
        }

        if st.session_state.auto_process:
            with st.container():
                if process_ppt(uploaded_file, level, num_questions, include_types):
                    st.rerun()
        else:
            if st.button("학습 자료 생성", type="primary", use_container_width=True):
                if process_ppt(uploaded_file, level, num_questions, include_types):
                    st.rerun()


# ============================================
# 학습 화면 (처리 후)
# ============================================
else:
    # Quick Stats Bar with enhanced visuals
    total_questions = sum(len(stage.get("questions", [])) for stage in st.session_state.quizzes)
    answered = len(st.session_state.quiz_answers)
    wrong_count = len(st.session_state.wrong_answers)
    accuracy = ((answered - wrong_count) / answered * 100) if answered > 0 else 0

    stat_cols = st.columns(5)
    with stat_cols[0]:
        st.metric("📄 슬라이드", f"{len(st.session_state.slides_data)}장")
    with stat_cols[1]:
        st.metric("📝 총 문제", f"{total_questions}개")
    with stat_cols[2]:
        st.metric("⏱️ 진행률", f"{answered}/{total_questions}")
    with stat_cols[3]:
        st.metric("❌ 오답", f"{wrong_count}개")
    with stat_cols[4]:
        st.metric("✅ 정답률", f"{accuracy:.0f}%")

    st.markdown("---")

    # Main Tabs with icons
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "✍️ Quiz Zone",
        "📝 Review Note",
        "🤖 AI Tutor"
    ])

    with tab1:
        render_dashboard()

    with tab2:
        render_quiz()

    with tab3:
        render_review()

    with tab4:
        render_tutor()
