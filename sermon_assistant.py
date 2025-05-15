import streamlit as st
import openai
import os
import tiktoken

# Initialize OpenAI Client with API Key from environment
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set model
MODEL = "gpt-3.5-turbo"

# Token pricing for GPT-3.5 Turbo
PRICE_PER_1K_INPUT = 0.0015
PRICE_PER_1K_OUTPUT = 0.002

# Setup tokenizer
tokenizer = tiktoken.encoding_for_model(MODEL)

# --- APP TITLE ---
st.title("AI Ministry Content Assistant (GPT-3.5 Turbo)")
st.write("Create sermon outlines, devotionals, Bible studies, and more. Token usage and cost tracked per request.")

# --- SELECT CONTENT TYPE ---
content_type = st.selectbox("What do you want to generate?", [
    "Sermon Outline",
    "Devotional",
    "Bible Study Guide",
    "Small Group Discussion",
    "Children's Lesson",
    "Social Media Post"
])

# --- INPUT FIELDS ---
topic = st.text_input("Enter your topic", "Faith in Difficult Times")
scripture = st.text_input("Enter key scripture (optional)", "James 1:2-4")
audience = st.selectbox("Select audience", ["General", "Men", "Women", "Youth", "Children"])

# --- ADJUST PROMPT BASED ON CONTENT TYPE ---
if content_type == "Sermon Outline":
    system_prompt = (
        "You are a friendly and encouraging AI sermon assistant who writes in a personal, pastoral tone. "
        "Generate a sermon outline with 3-5 main points for the given topic and scripture, tailored to the given audience. "
        "Include supporting Bible verses for each point."
    )
elif content_type == "Devotional":
    system_prompt = (
        "You are a devotional writer. Create a devotional thought for the given topic and scripture, "
        "including a reflection, prayer, and a life application. Keep the tone warm, personal, and encouraging."
    )
elif content_type == "Bible Study Guide":
    system_prompt = (
        "You are a Bible study guide writer. Create a structured Bible study guide for the given topic and scripture, "
        "including key questions, main points, and application steps for group discussion."
    )
elif content_type == "Small Group Discussion":
    system_prompt = (
        "You are a small group discussion guide writer. Create a discussion starter based on the topic and scripture, "
        "including 3-5 open-ended questions that encourage personal reflection and group interaction."
    )
elif content_type == "Children's Lesson":
    system_prompt = (
        "You are a children's Bible lesson writer. Create a simple and fun Bible lesson with a story, key point, and activity suggestion for kids. "
        "Make sure it's understandable for children."
    )
elif content_type == "Social Media Post":
    system_prompt = (
        "You are a social media content creator for a Christian audience. Write a short, engaging post based on the given topic and scripture, "
        "including a call to action and hashtags."
    )

# --- GENERATE OUTLINE BUTTON ---
if st.button("Generate Content"):
    with st.spinner("Generating content..."):
        user_prompt = f"Topic: {topic}\nScripture: {scripture}\nAudience: {audience}\n\nPlease provide the {content_type.lower()}."

        # Count input tokens
        prompt_tokens = len(tokenizer.encode(system_prompt)) + len(tokenizer.encode(user_prompt))

        # Call OpenAI API
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=1200,
        )

        # Get output and calculate tokens
        output_text = response.choices[0].message.content
        output_tokens = len(tokenizer.encode(output_text))

        # Calculate estimated cost
        input_cost = (prompt_tokens / 1000) * PRICE_PER_1K_INPUT
        output_cost = (output_tokens / 1000) * PRICE_PER_1K_OUTPUT
        total_cost = input_cost + output_cost

        # --- DISPLAY RESULTS ---
        st.success(f"{content_type} generated:")
        st.write(output_text)

        st.info(f"🔢 Estimated Tokens Used: Input: {prompt_tokens} | Output: {output_tokens}")
        st.info(f"💰 Estimated Cost: ${total_cost:.4f} (Input: ${input_cost:.4f} | Output: ${output_cost:.4f})")
