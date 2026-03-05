"""CSS 스타일 정의"""

CUSTOM_CSS = """
<style>
    /* 애니메이션 키프레임 정의 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    /* Main container optimization */
    .main .block-container {
        max-width: 1400px;
        padding: 1rem 2rem;
        animation: fadeIn 0.5s ease-out;
    }

    /* Card style for sections */
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        margin-bottom: 0.8rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    }

    .stExpander:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }

    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }

    /* Primary button special effect */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        font-size: 1.05rem;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
        animation: pulse 1s infinite;
    }

    /* Quiz button styling */
    .quiz-btn {
        width: 100%;
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        border: 2px solid rgba(49, 51, 63, 0.15);
        background-color: white;
        color: rgb(49, 51, 63);
        cursor: default;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    .quiz-btn.correct {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-color: #28a745;
        color: #155724;
        animation: pulse 0.5s ease-out;
        box-shadow: 0 4px 16px rgba(40, 167, 69, 0.3);
    }

    .quiz-btn.wrong {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-color: #dc3545;
        color: #721c24;
        animation: pulse 0.5s ease-out;
        box-shadow: 0 4px 16px rgba(220, 53, 69, 0.3);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: linear-gradient(90deg, #f8f9fa 0%, #ffffff 100%);
        padding: 0.5rem;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 16px 32px;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
        transform: translateY(-2px);
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #fff8e6 0%, #fffbf0 100%);
        border: 2px solid #ffe4a0;
        padding: 1rem;
        border-radius: 14px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 12px rgba(255, 228, 160, 0.2);
        animation: slideInRight 0.5s ease-out;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 8px 24px rgba(255, 228, 160, 0.4);
        border-color: #ffd966;
    }

    [data-testid="stMetric"] label {
        color: #666666 !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #333333 !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        background-size: 200% 100%;
        animation: shimmer 2s linear infinite;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    .stProgress > div {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 16px;
        margin: 0.8rem 0;
        animation: fadeIn 0.4s ease-out;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    .stChatMessage:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }

    .stChatMessage[data-testid*="user"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .stChatMessage[data-testid*="assistant"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 3px dashed #667eea;
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.1);
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        transform: scale(1.01);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
    }

    /* Info/Warning/Success/Error boxes */
    .stAlert {
        border-radius: 12px;
        animation: fadeIn 0.5s ease-out;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }

    .stAlert:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }

    /* Text input styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
        padding: 0.6rem 1rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        transform: scale(1.01);
    }

    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 10px;
        transition: all 0.3s ease;
    }

    .stSelectbox > div > div:hover {
        border-color: #667eea;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
    }

    /* Checkbox styling */
    .stCheckbox {
        transition: all 0.3s ease;
    }

    .stCheckbox:hover {
        transform: scale(1.05);
    }

    /* Slider styling */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }

    /* Hide sidebar toggle on PC */
    @media (min-width: 1024px) {
        [data-testid="collapsedControl"] {
            display: none;
        }
    }

    /* Quick stats bar */
    .quick-stats {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        animation: fadeIn 0.6s ease-out;
    }

    /* Loading spinner enhancement */
    .stSpinner > div {
        border-color: #667eea;
        border-right-color: transparent;
    }

    /* Title enhancement */
    h1, h2, h3 {
        animation: slideInRight 0.5s ease-out;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
        transition: background 0.3s ease;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5568d3, #6a3f8f);
    }

    /* Container hover effects */
    .element-container {
        animation: fadeIn 0.4s ease-out;
    }

    /* Success animation */
    @keyframes successPulse {
        0% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }
        100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }
    }

    /* Error animation */
    @keyframes errorShake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
</style>
"""
