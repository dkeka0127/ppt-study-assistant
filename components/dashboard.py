"""Dashboard 탭 컴포넌트"""

import streamlit as st
from utils.pdf_generator import generate_exam_pdf


def render_dashboard():
    """Dashboard 탭 렌더링"""
    # Two-column layout for dashboard
    dash_left, dash_right = st.columns([2, 1])

    with dash_left:
        st.subheader("📊 전체 요약")

        # 애니메이션 효과를 위한 컨테이너
        with st.container():
            st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 16px;
                    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
                    animation: fadeIn 0.6s ease-out;
                    margin-bottom: 1rem;
                ">
                    <div style="font-size: 1.1rem; line-height: 1.6;">
                        """ + st.session_state.summary.get("one_line", "요약 정보가 없습니다.") + """
                    </div>
                </div>
            """, unsafe_allow_html=True)

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
        # Keywords section with enhanced styling
        st.subheader("🎯 핵심 키워드")
        keywords = st.session_state.summary.get("keywords", [])
        if keywords:
            for i, kw in enumerate(keywords):
                # 각 키워드에 다른 그라데이션 적용
                colors = [
                    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                    "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
                    "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
                    "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
                ]
                color = colors[i % len(colors)]
                st.markdown(f"""
                    <div style="
                        background: {color};
                        color: white;
                        padding: 0.8rem 1.2rem;
                        border-radius: 12px;
                        margin-bottom: 0.8rem;
                        font-weight: 600;
                        text-align: center;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                        transition: all 0.3s ease;
                        animation: slideInRight 0.5s ease-out;
                        animation-delay: {i * 0.1}s;
                        opacity: 0;
                        animation-fill-mode: forwards;
                    ">
                        {kw}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("키워드가 없습니다.")

        if st.session_state.wrong_answers:
            st.markdown("---")
            st.warning(f"오답 {len(st.session_state.wrong_answers)}개가 있습니다.")

        # 시험지 생성
        st.markdown("---")
        st.subheader("시험지 생성")

        include_answers = st.checkbox("정답지 포함", value=False)

        if st.button("PDF 시험지 생성", use_container_width=True, type="primary"):
            pdf_buffer = generate_exam_pdf(
                st.session_state.quizzes,
                st.session_state.summary.get("one_line", ""),
                include_answers
            )
            st.download_button(
                label="시험지 다운로드",
                data=pdf_buffer,
                file_name="exam_sheet.pdf",
                mime="application/pdf",
                use_container_width=True
            )
