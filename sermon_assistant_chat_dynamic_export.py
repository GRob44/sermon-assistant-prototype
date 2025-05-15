import streamlit as st
import openai
import os
import tiktoken
from io import BytesIO
from docx import Document
from fpdf import FPDF

# Initialize OpenAI Client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-3.5-turbo"
PRICE_PER_1K_INPUT = 0.0015
PRICE_PER_1K_OUTPUT = 0.002

tokenizer = tiktoken.encoding_for_model(MODEL)

st.title("AI Ministry Chat Assistant (Dynamic Role + Export)")

content_type = st.selectbox("Select Assistant Role", [
    "Sermon Writer",
    "Devotional Writer",
    "Bible Study Guide Writer",
    "Small Group Discussion Facilitator",
    "Children's Lesson Creator",
    "Social Media Content Creator"
])

system_prompts = {
    "Sermon Writer": "You are a friendly sermon assistant...",
    "Devotional Writer": "You are a devotional writer...",
    "Bible Study Guide Writer": "You are a Bible study guide writer...",
    "Small Group Discussion Facilitator": "You are a small group facilitator...",
    "Children's Lesson Creator": "You are a children's lesson creator...",
    "Social Media Content Creator": "You are a social media content creator...",
}

system_prompt = system_prompts[content_type]

if "messages" not in st.session_state or st.session_state.get("last_role") != content_type:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.session_state.last_role = content_type

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

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
    output_tokens = len(tokenizer.encode(output_text))
    input_cost = (input_tokens / 1000) * PRICE_PER_1K_INPUT
    output_cost = (output_tokens / 1000) * PRICE_PER_1K_OUTPUT
    total_cost = input_cost + output_cost

    st.chat_message("assistant").write(output_text)
    st.session_state.messages.append({"role": "assistant", "content": output_text})

    st.info(f"🔢 Estimated Tokens Used: Input: {input_tokens} | Output: {output_tokens}")
    st.info(f"💰 Estimated Cost: ${total_cost:.4f} (Input: ${input_cost:.4f} | Output: ${output_cost:.4f})")

    # --- Export Options ---
    st.write("### 📥 Export Options")

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

    # Only show export for latest assistant message
    if output_text:
        st.download_button("📄 Download as TXT", export_text(output_text), file_name="generated_content.txt")
        st.download_button("📄 Download as DOCX", export_docx(output_text), file_name="generated_content.docx")
        st.download_button("📄 Download as PDF", export_pdf(output_text), file_name="generated_content.pdf")
