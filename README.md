# AI Ministry Conversational Assistant (Polished ChatGPT Style)

An AI-powered conversational assistant designed for pastors, church leaders, and ministry teams.  
This assistant provides:
- 🗨 ChatGPT-style natural conversation flow
- 📥 Export to TXT, DOCX, PDF (inside the assistant message)
- 🔢 Real-time token & cost monitoring (inside assistant message, right-aligned)
- 🔄 Dynamic role switching (Sermon, Devotional, Bible Study, etc.)
- 🧹 Chat reset button

---

## Features
- Clean ChatGPT-like chat interface using Streamlit's `st.chat_message`
- Export options and token usage **inside** the assistant reply (split left and right)
- Randomized follow-up prompts to make the assistant feel more personal and conversational
- Session state memory for smooth, ongoing conversations

---

## Setup Instructions

### Requirements
- Python 3.8+
- OpenAI API key with access to GPT-3.5 Turbo

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-ministry-assistant-polished.git
cd ai-ministry-assistant-polished
