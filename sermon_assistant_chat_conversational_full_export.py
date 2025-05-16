import streamlit as st
import openai
import os
import tiktoken
from io import BytesIO
from docx import Document
from fpdf import FPDF
import random

# Setup
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-3.5-turbo"
PRICE_PER_1K_INPUT = 0.0015
PRICE_PER_1K_OUTPUT = 0.002
tokenizer = tiktoken.encoding_for_model(MODEL)

st.title("AI Ministry Conversational Assistant (Full Chat Export Version)")

# Assistant type selector
content_type = st.selectbox("Select Assistant Style", [
    "Pastoral Chat & Sermon Coach",
    "Devotional Guide",
    "Bible Study Partner",
    "Small Group Coach",
    "Children's Lesson Creator",
    "Social Media Pastor"
])

system_prompts = {
    "Pastoral Chat & Sermon Coach": "You are a caring, conversational AI ministry coach...",
    "Devotional Guide": "You are a devotional companion...",
    "Bible Study Partner": "You are a Bible study partner...",
    "Small Group Coach": "You are a small group discussion coach...",
    "Children's Lesson Creator": "You are a creative, fun children's ministry helper...",
    "Social Media Pastor": "You are a social media pastor...",
}

system_prompt = system_prompts[content_type]

# Session initialization
if "messages" not in st.session_state or st.session_state.get("last_role") != content_type:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.session_state.last_role = content_type

# Display previous messages
for msg in st.session_state.messages:
    if msg["role"] in ["user", "assistant"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Chat input
user_input = st.chat_input(f"Chat with your {content_type.lower()}...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    prompt_text = ''.join([m['content'] for m in st.session_state.messages])
    input_tokens = len(tokenizer.encode(prompt_text))

    response = client.chat.completions.create(
        model=MODEL,
        messages=st.session_state.messages,
        temperature=0.7,
        max_tokens=1200,
    )

    output_text = response.choices[0].message.content

    # Add a random conversational follow-up
    follow_ups = [
        "Would you like me to suggest a closing illustration?",
        "Would you like help turning this into a devotional?",
        "Would you like a group discussion starter for this?",
        "Want a related Scripture passage?",
        "Need help outlining the next part?"
    ]
    output_text += "\n\n" + random.choice(follow_ups)

    output_tokens = len(tokenizer.encode(output_text))
    input_cost = (input_tokens / 1000) * PRICE_PER_1K_INPUT
    output_cost = (output_tokens / 1000) * PRICE_PER_1K_OUTPUT
    total_cost = input_cost + output_cost

    # Display assistant message
    with st.chat_message("assistant"):
        st.write(output_text)

    # Add to chat history
    st.session_state.messages.append({"role": "assistant", "content": output_text})

# Divider and export tools AFTER the chat input
st.divider()
st.write("### 📁 Export Full Conversation or View Stats")

# Compile full chat transcript (excluding system)
transcript = ""
for msg in st.session_state.messages:
    if msg["role"] == "user":
        transcript += f"You: {msg['content']}\n\n"
    elif msg["role"] == "assistant":
        transcript += f"Assistant: {msg['content']}\n\n"

# Export helpers
def export_text(chat_text):
    return BytesIO(chat_text.encode())

def export_docx(chat_text):
    doc = Document()
    for block in chat_text.split('\n\n'):
        doc.add_paragraph(block)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def clean_text_for_pdf(text):
    return ''.join([c if ord(c) < 256 else '' for c in text])

def export_pdf(chat_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    safe_text = clean_text_for_pdf(chat_text)
    for line in safe_text.split('\n'):
        pdf.multi_cell(0, 10, line)
    output = pdf.output(dest='S').encode('latin-1')
    return BytesIO(output)

# Display export + token usage
col1, col2 = st.columns([1, 1])

with col1:
    st.download_button("⬇️ Export as TXT", export_text(transcript), file_name="full_chat.txt")
    st.download_button("⬇️ Export as DOCX", export_docx(transcript), file_name="full_chat.docx")
    st.download_button("⬇️ Export as PDF", export_pdf(transcript), file_name="full_chat.pdf")

with col2:
    st.write("##### 🔢 Token Usage (Last Response)")
    st.info(f"Input Tokens: {input_tokens}  \nOutput Tokens: {output_tokens}")
    st.info(f"💰 Est. Cost: ${total_cost:.4f}")

# Reset Button
if st.button("🧹 Reset Chat"):
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.success("Chat history cleared.")
