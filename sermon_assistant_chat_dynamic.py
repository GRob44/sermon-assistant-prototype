import streamlit as st
import openai
import os
import tiktoken

# Initialize OpenAI Client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-3.5-turbo"
PRICE_PER_1K_INPUT = 0.0015
PRICE_PER_1K_OUTPUT = 0.002

tokenizer = tiktoken.encoding_for_model(MODEL)

# --- APP TITLE ---
st.title("AI Ministry Chat Assistant (Dynamic Role Mode)")

# --- Select assistant behavior dynamically ---
content_type = st.selectbox("Select Assistant Role", [
    "Sermon Writer",
    "Devotional Writer",
    "Bible Study Guide Writer",
    "Small Group Discussion Facilitator",
    "Children's Lesson Creator",
    "Social Media Content Creator"
])

# --- Map roles to system prompts ---
system_prompts = {
    "Sermon Writer": "You are a friendly sermon assistant. Generate sermon outlines with 3-5 main points, include supporting Bible verses, and speak in a pastoral tone.",
    "Devotional Writer": "You are a devotional writer. Write devotionals with reflections, prayers, and life applications. Use a warm, personal, and encouraging tone.",
    "Bible Study Guide Writer": "You are a Bible study guide writer. Provide structured guides with key questions, discussion points, and scripture-based applications.",
    "Small Group Discussion Facilitator": "You are a small group facilitator. Provide discussion starters with 3-5 open-ended questions to encourage reflection and interaction.",
    "Children's Lesson Creator": "You are a children's lesson creator. Write Bible lessons in a simple, fun way with key points and activities for kids.",
    "Social Media Content Creator": "You are a social media content creator for a Christian audience. Write short, engaging posts with hashtags and a call to action.",
}

# Update system prompt based on selected type
system_prompt = system_prompts[content_type]

# Initialize session state
if "messages" not in st.session_state or st.session_state.get("last_role") != content_type:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]
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

    st.chat_message("assistant").write(output_text)
    st.session_state.messages.append({"role": "assistant", "content": output_text})

    st.info(f"🔢 Estimated Tokens Used: Input: {input_tokens} | Output: {output_tokens}")
    st.info(f"💰 Estimated Cost: ${total_cost:.4f} (Input: ${input_cost:.4f} | Output: ${output_cost:.4f})")
