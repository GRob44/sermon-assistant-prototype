import streamlit as st
import openai
import os
import tiktoken
from io import BytesIO
from docx import Document
from fpdf import FPDF
import random

# Initialize OpenAI Client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-3.5-turbo"
PRICE_PER_1K_INPUT = 0.0015
PRICE_PER_1K_OUTPUT = 0.002

tokenizer = tiktoken.encoding_for_model(MODEL)

st.title("AI Ministry Conversational Assistant (Polished ChatGPT Style)")

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

# Initialize or reset chat based on role change
if "messages" not in st.session_state or st.session_state.get("last_role") != content_type:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.session_state.last_role = content_type

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- Chat input ---
user_input = st.chat_input(f"Chat with your {content_type.lower()}...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    all_messages_text = ''.join([m['content'] for m in st.session_state.messages])
    input_tokens = len(tokenizer.encode(all_messages_text))

    response = client.chat.completions.create(
        model=MODEL,
        messages=st.session_state.messages,
        temperature=0.7,
        max_tokens=1200,
    )

    output_text = response.choices[0].message.content

    # Vary follow-up question
    follow_ups = [
        "Would you like me to suggest a closing illustration?",
        "Should I help you create a group discussion starter from this?",
        "Would you like me to offer a call to action?",
        "Would you like me to suggest a related Scripture passage?",
        "Would you like me to help outline the next point?"
    ]
    output_text += "\n\n" + random.choice(follow_ups)

    output_tokens = len(tokenizer.encode(output_text))
    input_cost = (input_tokens / 1000) * PRICE_PER_1K_INPUT
    output_cost = (output_tokens / 1000) * PRICE_PER_1K_OUTPUT
    total_cost = input_cost + output_cost

    # Assistant message bubble ONLY with text
    with st.chat_message("assistant"):
        st.write(output_text)

    # --- BELOW the chat message: Export & Token Info ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("##### 📥 Export")
        def export_text(content):
            return BytesIO(content.encode())

        def export_docx(content):
            doc = Document()
            doc.add_paragraph(content)
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return buffer

        def export_pdf(content):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            for line in content.split('\n'):
                pdf.multi_cell(0, 10, line)
            pdf_output = pdf.output(dest='S').encode('latin-1')
            return BytesIO(pdf_output)

        st.download_button("TXT", export_text(output_text), file_name="chat_content.txt", key=f"txt_{len(st.session_state.messages)}")
        st.download_button("DOCX", export_docx(output_text), file_name="chat_content.docx", key=f"docx_{len(st.session_state.messages)}")
        st.download_button("PDF", export_pdf(output_text), file_name="chat_content.pdf", key=f"pdf_{len(st.session_state.messages)}")

    with col2:
        st.write("##### 🔢 Tokens & Cost")
        st.info(f"Input: {input_tokens} | Output: {output_tokens}")
        st.info(f"💰 Estimated: ${total_cost:.4f}")

    # Append assistant message to state
    st.session_state.messages.append({"role": "assistant", "content": output_text})

# Reset chat button at the bottom
if st.button("🧹 Reset Chat"):
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.success("Chat reset.")
