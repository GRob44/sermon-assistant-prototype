import streamlit as st
import openai
import os

# Initialize OpenAI Client with API Key from environment
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("AI Sermon Assistant Prototype")
st.write("Generate sermon outlines by topic, scripture, and audience.")

topic = st.text_input("Enter your sermon topic", "Faith in Difficult Times")
scripture = st.text_input("Enter key scripture (optional)", "James 1:2-4")
audience = st.selectbox("Select audience", ["General", "Men", "Women", "Youth", "Children"])

if st.button("Generate Sermon Outline"):
    with st.spinner("Generating outline..."):
        system_prompt = (
            "You are a friendly and encouraging AI sermon assistant who writes in a personal, pastoral tone. "
            "Generate a sermon outline with 3-5 main points for the given topic and scripture, tailored to the given audience. "
            "Include supporting Bible verses for each point."
        )
        user_prompt = f"Topic: {topic}\nScripture: {scripture}\nAudience: {audience}\n\nPlease provide the sermon outline."

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=1200,
        )

        outline = response.choices[0].message.content
        st.success("Outline generated:")
        st.write(outline)
