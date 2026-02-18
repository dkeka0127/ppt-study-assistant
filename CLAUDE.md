# CLAUDE.md - Project Guidelines for Claude Code

## Project Overview

PPT 학습 도우미 (PPT Study Assistant) - A Streamlit-based application that processes PowerPoint files and provides AI-powered study assistance using LangChain and Anthropic's Claude API.
https://rural-hook-0bd.notion.site/PPT-3017a8033999806b80f9d98233d195cf?source=copy_link

## Tech Stack

- **Framework**: Streamlit
- **Language**: Python 3.9
- **AI/LLM**: LangChain + Anthropic Claude API
- **PPT Processing**: python-pptx
- **Data**: pandas, numpy

## Project Structure

```
ppt-study-assistant/
├── app.py              # Main Streamlit application entry point
├── modules/
│   ├── parser.py       # PPT file parsing logic
│   ├── generator.py    # Content generation logic
│   └── chatbot.py      # Chatbot interaction logic
├── data/
│   └── temp/           # Temporary file storage (gitignored)
├── doc/                # Documentation
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (gitignored)
└── venv/               # Virtual environment (gitignored)
```

## Development Setup

### Virtual Environment

```bash
# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Save new dependencies
pip freeze > requirements.txt
```

### Environment Variables

```bash
# Load .env variables
export $(grep -v '^#' .env | xargs)

# Verify API key
echo $ANTHROPIC_API_KEY
```

### Running the Application

```bash
streamlit run app.py
```

## Coding Conventions

### Python Style

- Follow PEP 8
- Use Korean for user-facing strings (UI text, messages)
- Use English for code (variables, functions, comments)

### File Organization

- Keep modules focused and single-purpose
- `parser.py` - PPT parsing and text extraction
- `generator.py` - AI content generation (quizzes, summaries)
- `chatbot.py` - Interactive Q&A functionality

### Error Handling

- Validate uploaded files before processing
- Handle API errors gracefully with user-friendly messages
- Use `st.error()`, `st.warning()`, `st.success()` for feedback

## Key Dependencies

- `streamlit` - Web UI framework
- `python-pptx` - PowerPoint file handling
- `langchain` + `langchain-anthropic` - LLM integration
- `python-dotenv` - Environment variable management

## Git Workflow

- Main branch: `main`
- Commit messages in Korean or English
- Never commit `.env` or `venv/`

## Common Commands

```bash
# Run app
streamlit run app.py

# Check installed packages
pip list

# Deactivate venv
deactivate
```
