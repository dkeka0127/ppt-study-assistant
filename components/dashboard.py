"""Dashboard 탭 컴포넌트"""

import streamlit as st
from utils.pdf_generator import generate_exam_pdf


def render_dashboard():
    """Dashboard 탭 렌더링"""
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
