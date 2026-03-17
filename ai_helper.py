import requests
import json
from config import Config


def _call_llama(system_prompt, user_prompt):
    """Make a call to LLaMA 4 Maverick via Together AI API."""
    headers = {
        'Authorization': f'Bearer {Config.TOGETHER_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': Config.TOGETHER_MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        'temperature': 0.7,
        'max_tokens': 1024
    }

    try:
        response = requests.post(Config.TOGETHER_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"LLaMA API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response body: {e.response.text}")
        return None


def analyze_sentiment(text):
    """Analyze the sentiment of a complaint text. Returns 'Urgent', 'Neutral', or 'Positive'."""
    system_prompt = (
        "You are a sentiment analyzer for a college complaint system. "
        "Analyze the given complaint text and respond with EXACTLY one word: "
        "'Urgent' (if the complaint is serious, safety-related, or needs immediate attention), "
        "'Neutral' (if it's a regular complaint or feedback), or "
        "'Positive' (if it's positive feedback or appreciation). "
        "Respond with only the single word, nothing else."
    )
    result = _call_llama(system_prompt, text)
    if result and result.strip() in ['Urgent', 'Neutral', 'Positive']:
        return result.strip()
    return 'Neutral'


def categorize_complaint(text):
    """Auto-categorize a complaint into a department."""
    system_prompt = (
        "You are a complaint categorizer for a college system. "
        "Read the complaint and respond with EXACTLY one category from this list: "
        "Hostel, Faculty, Lab, Library, Canteen, Transport, Administration, Infrastructure, Other. "
        "Respond with only the category name, nothing else."
    )
    result = _call_llama(system_prompt, text)
    valid_categories = ['Hostel', 'Faculty', 'Lab', 'Library', 'Canteen',
                        'Transport', 'Administration', 'Infrastructure', 'Other']
    if result and result.strip() in valid_categories:
        return result.strip()
    return 'Other'


def generate_reply(complaint_title, complaint_description, department):
    """Generate a professional AI reply for an admin to send."""
    system_prompt = (
        "You are a helpful college administration assistant. "
        "Generate a professional, empathetic, and constructive reply to the following student complaint. "
        "The reply should acknowledge the issue, explain what steps will be taken, "
        "and provide a timeline if possible. Keep it concise (3-5 sentences)."
    )
    user_prompt = (
        f"Department: {department}\n"
        f"Complaint Title: {complaint_title}\n"
        f"Complaint Description: {complaint_description}"
    )
    result = _call_llama(system_prompt, user_prompt)
    return result or "We have received your complaint and our team is looking into it. We will get back to you shortly."


def generate_suggestion(text):
    """Generate AI suggestions for a student while they type their complaint."""
    system_prompt = (
        "You are a helpful college assistant. A student is writing a complaint. "
        "Based on what they've written so far, suggest a brief helpful tip or "
        "a common solution they could try before submitting. "
        "Keep it to 1-2 sentences. Be friendly and helpful."
    )
    result = _call_llama(system_prompt, text)
    return result or "Consider providing specific details like dates, times, and locations to help us address your concern faster."


def generate_weekly_summary(complaints_data):
    """Generate a weekly summary report of all complaints."""
    system_prompt = (
        "You are a college administration report writer. "
        "Generate a concise weekly summary report based on the complaints data provided. "
        "Include: total count, department breakdown, common themes, urgent items, "
        "and recommendations. Format it as a readable paragraph (5-8 sentences)."
    )
    user_prompt = f"Here are this week's complaints data:\n{complaints_data}"
    result = _call_llama(system_prompt, user_prompt)
    return result or "No summary could be generated at this time. Please try again later."
