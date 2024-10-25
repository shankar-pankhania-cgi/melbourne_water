import os
import requests
import streamlit as st
from PIL import Image
import base64

# API URL to the FastAPI server
API_URL = "http://127.0.0.1:8000/answer"

# Load logos (replace these with your actual image paths)
left_logo_path = "Melbourne-Water-Logo-RGB.png"  # Path to the first logo image
right_logo_path = "CGI_logo.svg.png"  # Path to the second logo image
submit_logo_path = "BtnSubmit.png"  # Path to the third logo image

# Convert images to base64 so they can be displayed with HTML in Streamlit
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Base64 encoded images
left_logo_base64 = get_image_base64(left_logo_path)
right_logo_base64 = get_image_base64(right_logo_path)
submit_logo_base64 = get_image_base64(submit_logo_path)

# Function to get answer from FastAPI backend
def get_answer_response(question):
    try:
        response = requests.post(API_URL, json={"question": question})
        if response.status_code == 200:
            json_response = response.json()
            answer_content = json_response.get('answer', 'No answer found')
            return answer_content
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error communicating with API: {e}"

# Streamlit UI Configuration
st.set_page_config(page_title="WaterWise Insights", layout="wide")

# Session state to hold the conversation history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Function to handle the question input and show answers
def handle_question_input():
    question = st.session_state.question_input
    if question:
        answer = get_answer_response(question)
        st.session_state.conversation.append({"question": question, "answer": answer})
        st.session_state.question_input = ""  # Clear input after submission

# Custom CSS to style the page layout
st.markdown(
    f"""
    <style>
        /* Set the body margin to zero to remove excess space */
        body {{
            margin: 0;
            padding: 0;
        }}

        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {{
            position: sticky;
            top: 3.7rem;
            background-color: white;
            z-index: 999;
            padding-top: 10px;
        }}            
        
        .logo-container {{
            display: flex;
            justify-content: space-between;
            width: 100%;
            padding: 0;  /* Remove any padding around the logo container */
        }}
        
        .logo-left {{
            width: 150px;
            height: 40px;
            margin: 0;  /* Remove any margin above the logo */
        }}
        
        .logo-right {{
            width: 100px;
            height: 40px;
            margin: 0;  /* Remove any margin above the logo */
        }}
        
        .title-box {{
            font-family: Arial, sans-serif;
            font-size: 32px;
            font-weight: bold;
            color: #ffffff;
            background-color: #003a8c;
            padding: 10px;
            text-align: center;
            border-radius: 10px;
            margin-top: 10px;
            width: 100%;
        }}
        
        .separator {{
            width: 100%;
            height: 2px;
            background-color: #003a8c;
            margin: 10px 0;
        }}
        
        .subtitle {{
            font-family: Arial, sans-serif;
            font-size: 24px;
            color: #ffffff;
            padding: 5px;
        }}
        
        .question-box {{
            background-color: #0047AB;
            padding: 10px;
            color: #ffffff;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 20px;
            width: 45%;
            display: inline-block;
            text-align: left;
            float: right;
        }}
        
        .answer-box {{
            background-color: #e0e7ff;
            padding: 10px;
            color: #0047AB;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 20px;
            width: 45%;
            display: inline-block;
            text-align: left;
            float: left;
        }}
        
        .submit-logo {{
            margin-top: 40px;
            float: right;
        }}

        .stTextInput {{
            width:100%;
        }}
        
        /* Footer styling */
        .footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            font-size: 14px;
            color: #a0a0a0;
            margin-top: 50px;
            position: fixed; /* Make footer fixed */
            bottom: 0; /* Align to the bottom */
            left: 0; /* Align to the left */
            background-color: #ffffff; /* Add background color for visibility */
            padding: 10px; /* Add some padding */
        }}
        
        .footer div {{
            flex: 1;
        }}
        
        .footer-left {{
            text-align: left;
        }}
        
        .footer-center {{
            text-align: center;
        }}
        
        .footer-right {{
            text-align: right;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Header with logos and title in one box
st.markdown(
    f"""
    <div class="fixed-header">
        <div class="logo-container">
            <img src="data:image/png;base64,{left_logo_base64}" class="logo-left">
            <img src="data:image/png;base64,{right_logo_base64}" class="logo-right">
        </div>
        <hr style="width:100%; border: 1px solid #003a8c; margin: 20px 0;">
        <div class="title-box">
            WaterWise
            <br>
            <span class="subtitle">AI-Powered Insights from Melbourne Water's Annual Report</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Display the conversation history
if st.session_state.conversation:
    for item in st.session_state.conversation:
        st.markdown(f'<div class="question-box">{item["question"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="answer-box">{item["answer"]}</div>', unsafe_allow_html=True)


col1, col2 = st.columns([0.96,0.04])
with col1:
    st.text_input(
        "Question",  # Provide a meaningful label here
        key="question_input",
        on_change=handle_question_input,
        placeholder="Enter Question...",
        label_visibility="hidden",  # Hide the label for aesthetics
    )
with col2:
    st.markdown(
        f'<img src="data:image/png;base64,{submit_logo_base64}" class="submit-logo" onclick="document.getElementById(\'question_input\').dispatchEvent(new Event(\'change\'));">',
        unsafe_allow_html=True
    )

# Footer and branding
st.markdown(
    """
    <div class="footer">
        <div class="footer-left">© 2024 CGI. All rights reserved.</div>
        <div class="footer-center">ChatGPT can make mistakes. Check important info</div>
        <div class="footer-right">Developed by AI Factory. EVP. CGI</div>
    </div>
    """,
    unsafe_allow_html=True
)
