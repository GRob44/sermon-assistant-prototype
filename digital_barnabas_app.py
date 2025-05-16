import streamlit as st
import openai
import os
import tiktoken
from io import BytesIO
from docx import Document
from fpdf import FPDF
import random

# ========== MODE DEFINITIONS ==========
MODES = {
    "just_talk": {
        "name": "Just Talk",
        "tone": "gentle",
        "description": "Conversational companion for people who want to reflect, vent, or process life through faith.",
        "starting_prompt": "What's on your heart today?",
        "follow_ups": [
            "Would you like to talk about how this connects to your faith?",
            "Is there a Scripture or prayer that might help you right now?",
            "Would you like to reflect on Psalm 34:18—'The Lord is close to the brokenhearted'?"
        ],
        "emotionally_healthy": True
    },
    "bible_study": {
        "name": "Bible Study Companion",
        "tone": "thoughtful",
        "description": "Helps reflect on Scripture, provides insights and related verses.",
        "starting_prompt": "What verse or passage are you exploring today?",
        "follow_ups": [
            "Would you like a related Scripture?",
            "Want to reflect on how this might apply to your life?"
        ],
        "emotionally_healthy": False
    },
    "devotional": {
        "name": "Devotional Creator",
        "tone": "encouraging",
        "description": "Helps turn thoughts, verses, or struggles into devotionals with reflection and prayer.",
        "starting_prompt": "Would you like to write a devotional based on a verse, a theme, or your current season?",
        "follow_ups": [
            "Would you like a prayer to go with this?",
            "Want to add a personal reflection point or takeaway?"
        ],
        "emotionally_healthy": True
    },
    "grief_support": {
        "name": "Grief & Anxiety Support",
        "tone": "compassionate",
        "description": "Walks with those experiencing grief, fear, or emotional overwhelm.",
        "starting_prompt": "How are you feeling today? What are you carrying right now?",
        "follow_ups": [
            "Would you like a Scripture to sit with right now?",
            "Would it help to pray together through this?"
        ],
        "emotionally_healthy": True
    },
    "marriage_parenting": {
        "name": "Marriage & Parenting Help",
        "tone": "wise",
        "description": "Provides biblical support for relationship challenges and family life.",
        "starting_prompt": "Is there something you’re facing in your marriage or family today?",
        "follow_ups": [
            "Would you like a Scripture that speaks to this?",
            "Want help turning this into a conversation with your spouse or child?"
        ],
        "emotionally_healthy": True
    },
    "evangelism": {
        "name": "Exploring Faith / Evangelism",
        "tone": "respectful",
        "description": "Gently helps seekers process doubts, questions, or spiritual curiosity.",
        "starting_prompt": "Where are you at in your journey with faith or God?",
        "follow_ups": [
            "Would you like to hear what Jesus said about this?",
            "Want to see how others wrestled with this in the Bible?"
        ],
        "emotionally_healthy": False,
        "gospel_clarity_level": "high"
    },
    "pastor_support": {
        "name": "Pastor Support",
        "tone": "empathetic",
        "description": "Offers guidance, sermon support, and emotional care for ministry leaders.",
        "starting_prompt": "How are you holding up lately—in your soul, your work, your home?",
        "follow_ups": [
            "Would you like help preparing for this Sunday?",
            "Need a moment to talk through what you're carrying?"
        ],
        "emotionally_healthy": True,
        "resource_suggestions": [
            "Emotionally Healthy Leader by Peter Scazzero",
            "The Resilient Pastor by Glenn Packiam",
            "Carey Nieuwhof Leadership Podcast",
            "Barna Group research for church trends"
        ]
    }
}

# ========== OPENAI & TOKEN SETUP ==========
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-3.5-turbo"
PRICE_PER_1K_INPUT = 0.0015
PRICE_PER_1K_OUTPUT = 0.002
tokenizer = tiktoken.encoding_for_model(MODEL)

st.title("Digital Barnabas – Faith Conversation Assistant")

# Mode selector
mode_keys = list(MODES.keys())
selected_mode_key = st.selectbox("Choose a conversation mode:", mode_keys, format_func=lambda key: MODES[key]["name"])
selected_mode = MODES[selected_mode_key]

# Session setup
if "messages" not in st.session_state or st.session_state.get("last_mode") != selected_mode_key:
    st.session_state.messages = [
        {"role": "system", "content": f"You are a {selected_mode['tone']} spiritual companion. {selected_mode['description']}"},
        {"role": "assistant", "content": selected_mode["starting_prompt"]}
    ]
    st.session_state.last_mode = selected_mode_key

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] in ["user", "assistant"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Chat input
user_input = st.chat_input("Type here...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    all_text = ''.join([m["content"] for m in st.session_state.messages])
    input_tokens = len(tokenizer.encode(all_text))

    response = client.chat.completions.create(
        model=MODEL,
        messages=st.session_state.messages,
        temperature=0.7,
        max_tokens=1200,
    )
    output_text = response.choices[0].message.content
    follow_up = random.choice(selected_mode["follow_ups"])
    output_text += f"\n\n{follow_up}"

    output_tokens = len(tokenizer.encode(output_text))
    input_cost = (input_tokens / 1000) * PRICE_PER_1K_INPUT
    output_cost = (output_tokens / 1000) * PRICE_PER_1K_OUTPUT
    total_cost = input_cost + output_cost

    with st.chat_message("assistant"):
        st.write(output_text)

    st.session_state.messages.append({"role": "assistant", "content": output_text})

# Transcript for export
transcript = ""
for msg in st.session_state.messages:
    if msg["role"] == "user":
        transcript += f"You: {msg['content']}\n\n"
    elif msg["role"] == "assistant":
        transcript += f"Assistant: {msg['content']}\n\n"

def export_text(content): return BytesIO(content.encode())
def export_docx(content):
    doc = Document()
    for block in content.split('\n\n'):
        doc.add_paragraph(block)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
def export_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line)
    return BytesIO(pdf.output(dest='S').encode('latin-1'))

# Divider and export UI
st.divider()
st.write("### 💾 Save this conversation")
col1, col2 = st.columns([1, 1])
with col1:
    st.download_button("📝 Save as Text", export_text(transcript), file_name="conversation.txt")
    st.download_button("📄 Save as Word", export_docx(transcript), file_name="conversation.docx")
    st.download_button("📰 Save as PDF", export_pdf(transcript), file_name="conversation.pdf")

with col2:
    if "input_tokens" in locals():
        with st.expander("💡 Behind the Scenes"):
            st.write(f"Input Tokens: {input_tokens}")
            st.write(f"Output Tokens: {output_tokens}")
            st.write(f"Estimated Cost: ${round(total_cost, 4)}")
    else:
        st.info("Send a message to view token usage.")

# Reset button
if st.button("🧹 Start Over"):
    st.session_state.messages = [
        {"role": "system", "content": f"You are a {selected_mode['tone']} spiritual companion. {selected_mode['description']}"},
        {"role": "assistant", "content": selected_mode["starting_prompt"]}
    ]
    st.success("Conversation reset.")
