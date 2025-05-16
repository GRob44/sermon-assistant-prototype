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
    }
}

# ========== OPENAI SETUP ==========
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-3.5-turbo"
PRICE_PER_1K_INPUT = 0.0015
PRICE_PER_1K_OUTPUT = 0.002
encoder = tiktoken.encoding_for_model(MODEL)

st.title("Digital Barnabas – Faith Conversation Assistant")

# ========== MODE SELECTION ==========
mode_keys = list(MODES.keys())
selected_mode_key = st.selectbox("Choose a conversation mode:", mode_keys, format_func=lambda key: MODES[key]["name"])
selected_mode = MODES[selected_mode_key]

# ========== SESSION INIT ==========
if "messages" not in st.session_state or st.session_state.get("last_mode") != selected_mode_key:
    st.session_state.messages = [
        {"role": "system", "content": f"You are a {selected_mode['tone']} spiritual companion. {selected_mode['description']}"},
        {"role": "assistant", "content": selected_mode["starting_prompt"]}
    ]
    st.session_state.last_mode = selected_mode_key

# ========== DISPLAY MESSAGES ==========
for msg in st.session_state.messages:
    if msg["role"] in ["user", "assistant"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ========== CHAT INPUT ==========
user_input = st.chat_input("Type here...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    input_tokens = len(encoder.encode(user_input))

    # Response
    response = client.chat.completions.create(
        model=MODEL,
        messages=st.session_state.messages,
        temperature=0.7,
        max_tokens=1200,
    )
    output_text = response.choices[0].message.content

    # Add gospel anchor if evangelism mode and question includes belief
    if selected_mode_key == "evangelism" and any(word in user_input.lower() for word in ["believe", "jesus", "god", "why"]):
        output_text += "\n\n💬 At the heart of Christianity is this: Jesus came to rescue, not just to teach. He said, 'I am the way, the truth, and the life. No one comes to the Father except through me.' (John 14:6)"

    output_tokens = len(encoder.encode(output_text))
    input_cost = (input_tokens / 1000) * PRICE_PER_1K_INPUT
    output_cost = (output_tokens / 1000) * PRICE_PER_1K_OUTPUT
    total_cost = input_cost + output_cost

    follow_up = random.choice(selected_mode["follow_ups"])
    output_text += f"\n\n{follow_up}"

    with st.chat_message("assistant"):
        st.write(output_text)

    st.session_state.messages.append({"role": "assistant", "content": output_text})

# ========== EXPORT ==========
transcript = ""
for msg in st.session_state.messages:
    if msg["role"] == "user":
        transcript += f"You: {msg['content']}\n\n"
    elif msg["role"] == "assistant":
        transcript += f"Assistant: {msg['content']}\n\n"

def export_text(content):
    return BytesIO(content.encode())

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
        try:
            pdf.multi_cell(0, 10, line)
        except:
            pdf.multi_cell(0, 10, line.encode('latin-1', 'ignore').decode('latin-1'))
    return BytesIO(pdf.output(dest='S').encode('latin-1', 'ignore'))

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

if st.button("🧹 Start Over"):
    st.session_state.messages = [
        {"role": "system", "content": f"You are a {selected_mode['tone']} spiritual companion. {selected_mode['description']}"},
        {"role": "assistant", "content": selected_mode["starting_prompt"]}
    ]
    st.success("Conversation reset.")
