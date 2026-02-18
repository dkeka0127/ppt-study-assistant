"""CSS 스타일 정의"""

CUSTOM_CSS = """
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

    /* Quiz button styling */
    .quiz-btn {
        width: 100%;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        font-weight: 500;
        font-size: 1rem;
        border: 1px solid rgba(49, 51, 63, 0.2);
        background-color: white;
        color: rgb(49, 51, 63);
        cursor: default;
    }
    .quiz-btn.correct {
        background-color: #d4edda;
        border-color: #28a745;
        color: #155724;
    }
    .quiz-btn.wrong {
        background-color: #f8d7da;
        border-color: #dc3545;
        color: #721c24;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 16px 32px;
        border-radius: 8px 8px 0 0;
        font-size: 1.1rem;
        font-weight: 600;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #fff8e6;
        border: 1px solid #ffe4a0;
        padding: 0.8rem;
        border-radius: 10px;
    }

    [data-testid="stMetric"] label {
        color: #666666 !important;
        font-size: 0.85rem !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #333333 !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
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
"""
