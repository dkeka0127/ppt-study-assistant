import streamlit as st
from pptx import Presentation

st.title("PPT 학습 도우미 초기 세팅 완료! 🚀")

uploaded_file = st.file_uploader("PPT 파일을 업로드하세요", type=["pptx"])

if uploaded_file:
    prs = Presentation(uploaded_file)
    st.success(f"총 {len(prs.slides)}개의 슬라이드를 찾았습니다.")
    
    for i, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                st.write(f"Slide {i+1}: {shape.text[:50]}...")