"""PDF 시험지 생성 유틸리티"""

import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def generate_exam_pdf(quizzes, title, include_answers=False):
    """Generate exam PDF from quizzes"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    # 프로젝트 폴더 내의 폰트 파일 사용
    base_dir = os.path.dirname(os.path.dirname(__file__))
    font_path = os.path.join(base_dir, "fonts", "ArialUnicode.ttf")

    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Korean', font_path))
        font_name = 'Korean'
    else:
        font_name = 'Helvetica'

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='KoreanTitle',
        fontName=font_name,
        fontSize=18,
        leading=24,
        spaceAfter=12,
        alignment=1  # Center
    ))
    styles.add(ParagraphStyle(
        name='KoreanHeading',
        fontName=font_name,
        fontSize=14,
        leading=20,
        spaceAfter=10,
        spaceBefore=15
    ))
    styles.add(ParagraphStyle(
        name='KoreanBody',
        fontName=font_name,
        fontSize=11,
        leading=16,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='KoreanOption',
        fontName=font_name,
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='KoreanAnswer',
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor='blue'
    ))

    story = []

    # Title
    story.append(Paragraph("시험지", styles['KoreanTitle']))
    if title:
        story.append(Paragraph(title, styles['KoreanBody']))
    story.append(Spacer(1, 10*mm))

    # Name field
    story.append(Paragraph("이름: ___________________    날짜: ___________________", styles['KoreanBody']))
    story.append(Spacer(1, 10*mm))

    # Questions
    q_num = 1
    for stage in quizzes:
        stage_name = stage.get("stage", "")
        if stage_name:
            story.append(Paragraph(f"[ {stage_name} ]", styles['KoreanHeading']))

        for q in stage.get("questions", []):
            q_type = q.get("type", "short_answer")
            question_text = q.get("question", "")

            # Question
            story.append(Paragraph(f"{q_num}. {question_text}", styles['KoreanBody']))

            if q_type == "multiple_choice":
                options = q.get("options", [])
                for idx, opt in enumerate(options):
                    option_label = chr(ord('①') + idx)
                    story.append(Paragraph(f"{option_label} {opt}", styles['KoreanOption']))

                if include_answers:
                    answer_idx = q.get("answer", 0)
                    answer_label = chr(ord('①') + answer_idx)
                    story.append(Paragraph(f"정답: {answer_label}", styles['KoreanAnswer']))

            elif q_type == "short_answer":
                story.append(Paragraph("답: _______________________________", styles['KoreanOption']))
                if include_answers:
                    story.append(Paragraph(f"정답: {q.get('answer', '')}", styles['KoreanAnswer']))

            story.append(Spacer(1, 3*mm))
            q_num += 1

    doc.build(story)
    buffer.seek(0)
    return buffer
