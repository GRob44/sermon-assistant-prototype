import streamlit as st
import openai
import os
import tiktoken
from io import BytesIO
from docx import Document
from fpdf import FPDF
import random

# OpenAI client setup
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-3.5-turbo"
PRICE_PER_1K_INPUT = 0.0015
PRICE_PER_1K_OUTPUT = 0.002
tokenizer = tiktoken.encoding_for_model(MODEL)

# Title and welcome
st.title("Faith Conversation Assistant")
st.caption("Helping you reflect, study, and wrestle through Scripture and life — together.")

# Assistant styles
content_type = st.selectbox("What kind of help do you need today?", [
    "Just Talk — I need to process something",
    "Bible Study Companion",
    "Devotional Creator",
    "Small Group Guide",
    "Message or Sermon Brainstorm",
])

# Gentle system prompt
system_prompts = {
    "Just Talk — I need to process something": "You are a kind, patient spiritual companion. Ask gentle follow-up questions, listen well, and speak with pastoral care.",
    "Bible Study Companion": "You are a thoughtful Bible study partner. Help reflect on Scripture, ask what stands out, and suggest related passages.",
    "Devotional Creator": "You are a devotional guide. Help turn themes and verses into heartfelt devotionals with reflection and prayer.",
    "Small Group Guide": "You are a group leader. Suggest questions, reflections, and themes to open up conversation and connection.",
    "Message or Sermon Brainstorm": "You are a sermon idea coach. Help the user unpack themes and develop outlines based on Scripture and life."
}
system_prompt = system_prompts[content_type]

# Setup session
if "messages" not in st.session_state or st.session_state.get("last_role") != content_type:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Hey there. I'm here to help you reflect, study, or just process what's on your heart today. Want to start with a verse, a topic, or something you're walking through?"}
    ]
    st.session_state.last_role = content_type

# Display full conversation
for msg in st.session_state.messages:
    if msg["role"] in ["user", "assistant"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Chat input
user_input = st.chat_input("Type your question, verse, or thought here...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    prompt_text = ''.join([m['content'] for m in st.session_state.messages])
    input_tokens = len(tokenizer.encode(prompt_text))

    # OpenAI call
    response = client.chat.completions.create(
        model=MODEL,
        messages=st.session_state.messages,
        temperature=0.7,
        max_tokens=1200,
    )
    output_text = response.choices[0].message.content

    # More human-style closing suggestions
    follow_ups = [
        "Want to keep exploring this?",
        "Would you like me to help turn this into a devotional or prayer?",
        "Do you want to share this with someone or keep reflecting?",
        "Need some help making this a group discussion?",
        "Would a related Scripture help here?"
    ]
    output_text += "\n\n" + random.choice(follow_ups)

    output_tokens = len(tokenizer.encode(output_text))
    input_cost = (input_tokens / 1000) * PRICE_PER_1K_INPUT
    output_cost = (output_tokens / 1000) * PRICE_PER_1K_OUTPUT
    total_cost = input_cost + output_cost

    with st.chat_message("assistant"):
        st.write(output_text)

    st.session_state.messages.append({"role": "assistant", "content": output_text})

# Divider
st.divider()

# Save full chat
transcript = ""
for msg in st.session_state.messages:
    if msg["role"] == "user":
        transcript += f"You: {msg['content']}\n\n"
    elif msg["role"] == "assistant":
        transcript += f"Assistant: {msg['content']}\n\n"

# Export functions
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

# Friendly footer
st.write("### 💾 Save this conversation")
col1, col2 = st.columns([1, 1])
with col1:
    st.download_button("📝 Save as Text", export_text(transcript), file_name="faith_conversation.txt")
    st.download_button("📄 Save as Word", export_docx(transcript), file_name="faith_conversation.docx")
    st.download_button("📰 Save as PDF", export_pdf(transcript), file_name="faith_conversation.pdf")

with col2:
    if "input_tokens" in locals() and "output_tokens" in locals():
        with st.expander("💡 Behind the Scenes"):
            st.write(f"Input Tokens: {input_tokens}")
            st.write(f"Output Tokens: {output_tokens}")
            st.write(f"Estimated Cost: ${round(input_cost + output_cost, 4)}")
    else:
        with st.expander("💡 Behind the Scenes"):
            st.write("Send a message to view token details.")

# Reset chat
if st.button("🧹 Start Over"):
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Hey there. I'm here to help you reflect, study, or just process what's on your heart today. Want to start with a verse, a topic, or something you're walking through?"}
    ]
    st.success("Conversation reset.")
