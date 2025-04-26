import streamlit as st
import requests
import json
import os
from datetime import date
import google.generativeai as genai

st.set_page_config(page_title="AI Marketing Assistant", layout="wide")

GEMINI_API_KEY = st.secrets["api_keys"]["gemini"]
TOGETHER_API_KEY = st.secrets["api_keys"]["together"]

st.sidebar.header("👤 Your Business Profile")

user_name = st.sidebar.text_input("Your Name")
business_type = st.sidebar.selectbox("Type of Business", ["Food", "Fashion", "Personalized Gifts"])
yearly_income = st.sidebar.number_input("Yearly Income (INR)", step=100)
location = st.sidebar.text_input("Location")

user_profile = {
    "name": user_name,
    "business_type": business_type,
    "yearly_income": yearly_income,
    "location": location
}

st.title("🧠 AI-Powered Marketing Assistant")
st.write(f"👋 Hello {user_profile['name']}, here's your personalized marketing strategy for your *{user_profile['business_type']}* business!")

def generate_marketing_templates(profile):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp")

    prompt = f"""
You are a helpful digital marketing expert.

The user runs a {profile['business_type']} business based in {profile['location']} 
with an annual revenue of ${profile['yearly_income']}.

Return a marketing strategy suggestion in the following JSON format:

{{
  "marketing_campaign_goals": ["goal1", "goal2", "goal3"],
  "tone_for_posts_and_emails": "tone here",
  "best_post_types": ["type1", "type2", "type3"],
  "posting_frequency_per_week": number
}}

Make sure to consider income and location in your suggestions.
"""

    try:
        response = model.generate_content(prompt)
        content = response.text.strip()

        content = content.split("```json")[-1].split("```")[0].strip() if "```" in content else content

        parsed = json.loads(content)

        return {
            "campaign_goals": parsed.get("marketing_campaign_goals", []),
            "tone": parsed.get("tone_for_posts_and_emails", ""),
            "post_types": parsed.get("best_post_types", []),
            "posting_frequency": parsed.get("posting_frequency_per_week", 0)
        }

    except Exception as e:
        st.error("⚠️ Failed to generate strategy.")
        st.code(str(e))
        return {"error": str(e), "raw": content if 'content' in locals() else ""}

if "template_data" not in st.session_state:
    st.session_state.template_data = generate_marketing_templates(user_profile)

if st.button("🔁 Refresh Suggestions"):
    st.session_state.template_data = generate_marketing_templates(user_profile)

template_data = st.session_state.template_data

if "error" in template_data:
    st.error(template_data["error"])
    st.code(template_data.get("raw", ""))
    st.stop()

st.subheader("📌 Personalized Strategy")
st.markdown("*Campaign Goals:*")
campaign_goals = [str(goal) for goal in template_data.get("campaign_goals", [])]
st.markdown("- " + "\n- ".join(campaign_goals))

st.markdown(f"*Recommended Tone:* {template_data['tone']}")

st.markdown("*Content Types to Focus On:*")
st.markdown("- " + "\n- ".join(template_data["post_types"]))

st.markdown(f"*Posting Frequency:* {template_data['posting_frequency']}")

def generate_content_calendar(profile, template):
    user_prompt = f"""
Create a 15-day social media content calendar for a {profile['business_type']} brand.
Goals: {', '.join(template['campaign_goals'])}
Tone: {template['tone']}
Post types: {', '.join(template['post_types'])}
Location: {profile['location']}
Income: ${profile['yearly_income']}

Each day should include: Post Idea, Caption, Hashtags.
Format as markdown table.
"""

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are an expert content strategist."},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 10000
    }

    response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

if st.button("📅 Generate 15-Day Content Calendar"):
    with st.spinner("Crafting your content plan..."):
        calendar = generate_content_calendar(user_profile, template_data)
        st.subheader("📆 Your Social Media Calendar")
        st.markdown(calendar)

def generate_email(subject, tone, product):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp")
    prompt = f"Write a promotional email for {product}. Subject: {subject}. Tone: {tone}. Audience: returning customers."
    response = model.generate_content(prompt)
    return response.text

with st.expander("✉ Generate Email Campaign"):
    email_subject = st.text_input("Subject")
    email_product = st.text_input("Product Highlight")
    email_tone = st.selectbox("Tone", ["Friendly", "Exciting", "Elegant", "Professional"])
    if st.button("Generate Email"):
        email_text = generate_email(email_subject, email_tone, email_product)
        st.text_area("Generated Email", email_text, height=300)
