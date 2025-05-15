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

st.title("AI Ministry Conversational Assistant (ChatGPT Style + Export)")

content_type = st.selectbox("Select Assistant Style", [
    "Pastoral Chat & Sermon Coach",
    "Devotional Guide",
    "Bible Study Partner",
    "Small Group Coach",
    "Children's Lesson Creator",
    "Social Media Pastor"
])

# Conversational style system prompts for each role
system_prompts = {
    "Pastoral Chat & Sermon Coach": "You are a caring, conversational AI ministry coach. You help users brainstorm sermon ideas, life applications, and illustrations, while asking them reflective questions about their audience, challenges, and what message they feel led to share. Always keep the tone pastoral, warm, and encouraging.",
    "Devotional Guide": "You are a devotional companion, walking alongside users to reflect on Scripture and life. Share gentle insights, ask follow-up questions about their day, and suggest ways they can experience God's presence. Keep it authentic, personal, and never robotic.",
    "Bible Study Partner": "You are a Bible study partner. You explore Scripture with users, helping them find key truths, asking what speaks to them personally, and suggesting questions they can take to their group or journal about. Always prompt for personal reflection.",
    "Small Group Coach": "You are a small group discussion coach. Help users brainstorm discussion topics, ask engaging, open-ended questions, and suggest creative ways to get the group talking. Always check if they'd like alternative angles or follow-up questions.",
    "Children's Lesson Creator": "You are a creative, fun children's ministry helper. Help write lessons, stories, or activities, but also ask what age group they're serving and suggest ways to make lessons interactive and age-appropriate.",
    "Social Media Pastor": "You are a social media pastor. Help create short, inspiring posts but also coach the user on how to connect with their audience authentically. Always end by asking if they'd like hashtags, call to action, or image caption ideas."
}

system_prompt = system_prompts[content_type]

# Initialize or reset chat based on role change
if "messages" not in st.session_state or st.session_state.get("last_role") != content_type:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.session_state.last_role = content_type

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

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
    output_tokens = len(tokenizer.encode(output_text))
    input_cost = (input_tokens / 1000) * PRICE_PER_1K_INPUT
    output_cost = (output_tokens / 1000) * PRICE_PER_1K_OUTPUT
    total_cost = input_cost + output_cost

    # Add follow-up question to make it more human
    output_text += "\n\nWould you like me to suggest related Scriptures, illustrations, or group discussion starters?"

    st.chat_message("assistant").write(output_text)
    st.session_state.messages.append({"role": "assistant", "content": output_text})

    st.info(f"🔢 Estimated Tokens Used: Input: {input_tokens} | Output: {output_tokens}")
    st.info(f"💰 Estimated Cost: ${total_cost:.4f} (Input: ${input_cost:.4f} | Output: ${output_cost:.4f})")

    # Export options
    st.write("### 📥 Export Latest Reply")

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
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer

    if output_text:
        st.download_button("📄 Download as TXT", export_text(output_text), file_name="chat_content.txt")
        st.download_button("📄 Download as DOCX", export_docx(output_text), file_name="chat_content.docx")
        st.download_button("📄 Download as PDF", export_pdf(output_text), file_name="chat_content.pdf")

# Reset chat button
if st.button("🧹 Reset Chat"):
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.success("Chat reset.")
