import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from time import time
import pandas as pd
from datetime import datetime
import pdfkit
from fpdf import FPDF

def initialize_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_started = False
        st.session_state.user_info = {
            "name": None,
            "age": None,
            "gender": None,
            "parents_status": None,
            "financial_background": None,
            "living_situation": None,
            "academic_year": None
        }
        st.session_state.session_start = None
        st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.session_state.crisis_info_shown = False

def get_ai_response(prompt, conversation_history, is_diagnostic=False):
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Server error: Api key not found!"
    
    client = Groq(api_key=api_key)
    
    if is_diagnostic:
        system_prompt = """You are a psychologist generating a diagnostic summary based on a student's conversation.
        This summary will be used by professional counselors to understand the student's situation.
        
        The student has been sharing their concerns gradually throughout the conversation. 
        Review the entire conversation history to identify patterns and issues rather than focusing only on explicitly stated problems.
        
        You have the following background information about the student:
        - Name: {name}
        - Age: {age}
        - Gender: {gender}
        - Parents Status: {parents_status}
        - Financial Background: {financial_background}
        - Living Situation: {living_situation}
        - Academic Year: {academic_year}
        
        Analyze the conversation and provide:
        1. Main concerns or issues presented (include both explicit and implicit concerns)
        2. Mood and emotional state assessment
        3. Risk factors identified (if any)
        4. Coping mechanisms observed
        5. Recommended support strategies
        6. Urgency level (Low, Moderate, High, Critical)
        
        Format your response in a professional clinical summary style suitable for a college counselor.
        Be objective, thorough, and focused on patterns rather than isolated statements.
        Include only factual observations from the conversation, not speculations.
        Consider how the student's background information might relate to their current concerns.
        """
        
        # Format system prompt with user info
        system_prompt = system_prompt.format(
            name=st.session_state.user_info["name"] or "Unknown",
            age=st.session_state.user_info["age"] or "Unknown",
            gender=st.session_state.user_info["gender"] or "Unknown",
            parents_status=st.session_state.user_info["parents_status"] or "Unknown",
            financial_background=st.session_state.user_info["financial_background"] or "Unknown",
            living_situation=st.session_state.user_info["living_situation"] or "Unknown",
            academic_year=st.session_state.user_info["academic_year"] or "Unknown"
        )
    else:
        system_prompt = """You are an empathetic and supportive counselor for college students.
        Your responses should be:
        1. Compassionate and non-judgmental
        2. Encouraging but realistic
        3. Focused on helping students develop healthy coping strategies
        4. Clear about your role as an AI support tool, not a replacement for professional help

        You have the following background information about the student:
        - Name: {name}
        - Age: {age}
        - Gender: {gender}
        - Parents Status: {parents_status}
        - Financial Background: {financial_background}
        - Living Situation: {living_situation}
        - Academic Year: {academic_year}

        IMPORTANT: Only mention crisis resources when you detect serious mental health concerns. 
        Do not mention these resources in every message. Use your judgment to determine when a student 
        might need professional help. Even in concerning situations, only mention these resources once 
        per conversation:
        - The college counseling center
        - 24/7 mental health helpline: 1098
        - Encouraging them to talk to trusted friends, family, or counselors

        Students often reveal their concerns gradually. Listen attentively and build upon previous 
        messages to form a coherent understanding of their situation. Ask thoughtful follow-up 
        questions to understand deeper issues, but don't interrogate.
        
        Keep your responses concise and focused on the immediate concern while remembering the 
        conversation context.
        """
        
        # Format system prompt with user info
        system_prompt = system_prompt.format(
            name=st.session_state.user_info["name"] or "Unknown",
            age=st.session_state.user_info["age"] or "Unknown",
            gender=st.session_state.user_info["gender"] or "Unknown",
            parents_status=st.session_state.user_info["parents_status"] or "Unknown",
            financial_background=st.session_state.user_info["financial_background"] or "Unknown",
            living_situation=st.session_state.user_info["living_situation"] or "Unknown",
            academic_year=st.session_state.user_info["academic_year"] or "Unknown"
        )
    
    try:
        if not is_diagnostic and not st.session_state.crisis_info_shown:
            system_prompt += "\nNote: You haven't shared crisis resources with this student yet in this session."
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1000
        )
        
        response_text = response.choices[0].message.content if response.choices else "Server down (Check groq gateway)!"
        
        if not is_diagnostic and not st.session_state.crisis_info_shown:
            crisis_indicators = ["mental health helpline", "1098", "counseling center", "professional help"]
            if any(indicator in response_text.lower() for indicator in crisis_indicators):
                st.session_state.crisis_info_shown = True
        
        return response_text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_diagnostic_summary():
    if len(st.session_state.messages) < 4:
        return "Insufficient conversation data for meaningful analysis."
    
    conversation_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages
    ]
    
    prompt = "Please provide a comprehensive psychological diagnostic summary of this student based on our entire conversation."
    diagnostic = get_ai_response(prompt, conversation_history, is_diagnostic=True)
    
    return diagnostic

def save_diagnostic(diagnostic, format="txt"):
    user_name = st.session_state.user_info["name"] or "anonymous"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "txt":
        content = f"PSYCHOLOGICAL DIAGNOSTIC SUMMARY\n"
        content += f"Student: {user_name}\n"
        content += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"Session ID: {st.session_state.session_id}\n\n"
        
        # Add user information section
        content += "--- STUDENT INFORMATION ---\n"
        for key, value in st.session_state.user_info.items():
            formatted_key = key.replace('_', ' ').title()
            content += f"{formatted_key}: {value or 'Not provided'}\n"
        content += "\n"
        
        content += diagnostic
        
        content += "\n\n--- FULL CONVERSATION LOG ---\n\n"
        for msg in st.session_state.messages:
            role = "Student" if msg["role"] == "user" else "AI Counselor"
            content += f"{role}: {msg['content']}\n\n"
            
        return content.encode('utf-8')
    
    elif format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "PSYCHOLOGICAL DIAGNOSTIC SUMMARY", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Student: {user_name}", ln=True)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.cell(0, 10, f"Session ID: {st.session_state.session_id}", ln=True)
        pdf.ln(5)
        
        # Add student information section
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "STUDENT INFORMATION", ln=True)
        pdf.set_font("Arial", size=10)
        for key, value in st.session_state.user_info.items():
            formatted_key = key.replace('_', ' ').title()
            pdf.cell(0, 10, f"{formatted_key}: {value or 'Not provided'}", ln=True)
        pdf.ln(10)
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "DIAGNOSTIC SUMMARY", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", size=10)
        
        for line in diagnostic.split('\n'):
            pdf.multi_cell(0, 10, line)
        
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "FULL CONVERSATION LOG", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", size=10)
        
        for msg in st.session_state.messages:
            role = "Student" if msg["role"] == "user" else "AI Counselor"
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 10, role, ln=True)
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 10, msg["content"])
            pdf.ln(5)
            
        return pdf.output(dest='S').encode('latin1')
    
    else:
        return None

def chat_interface():
    st.title(" Soup's Safe Space :)")
    initialize_chat()
    
    if not st.session_state.chat_started:
        st.markdown("""
        Welcome to Soup's Space! This is a safe space where you can talk out, laugh out or cry out. 
        
        While I'm here to listen and support you, remember that I'm an AI assistant.
        For serious concerns, please reach out to professional counselors or mental health services who are always ready to help you :)
        
        Please fill in the following information to help us understand you better. This will help us provide more personalized support.
        """)
        
        # Create a form for user information
        with st.form("user_info_form"):
            st.session_state.user_info["name"] = st.text_input("What would you like me to call you?")
            
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.user_info["age"] = st.number_input("Age", min_value=16, max_value=100, step=1)
                st.session_state.user_info["gender"] = st.selectbox("Gender", ["", "Male", "Female", "Non-binary", "Prefer not to say", "Other"])
                st.session_state.user_info["parents_status"] = st.selectbox("Parents Status", ["", "Married", "Divorced", "Separated", "Single Parent", "Guardian(s)", "Deceased", "Other"])
            
            with col2:
                st.session_state.user_info["financial_background"] = st.selectbox("Financial Background", ["", "Low Income", "Middle Income", "High Income", "Scholarship Student", "Student Loans", "Self-Supporting", "Prefer not to say"])
                st.session_state.user_info["living_situation"] = st.selectbox("Living Situation", ["", "On-campus", "Off-campus with roommates", "Off-campus alone", "With family", "Other"])
                st.session_state.user_info["academic_year"] = st.selectbox("Academic Year", ["", "Freshman", "Sophomore", "Junior", "Senior", "Graduate Student", "Other"])
            
            submit_button = st.form_submit_button("Start Chatting")
            
            if submit_button and st.session_state.user_info["name"]:
                st.session_state.chat_started = True
                st.session_state.session_start = time()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Hi {st.session_state.user_info['name']}, I'm here to listen and support you. What's on your mind today?"
                })
                st.rerun()
            elif submit_button and not st.session_state.user_info["name"]:
                st.error("Please provide a name to continue.")
    
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Share your thoughts..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                conversation_history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]
                ]
                response = get_ai_response(prompt, conversation_history)
                st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        if st.session_state.session_start:
            elapsed_time = int(time() - st.session_state.session_start)
            if elapsed_time < 1800:
                st.sidebar.info(f"Chat time: {elapsed_time // 60} minutes")
            else:
                st.warning("Session timeout. Starting new session...")
                reset_chat()
                st.rerun()
        
        with st.sidebar.expander("Counselor Tools", expanded=False):
            if st.button("Generate Diagnostic Summary"):
                diagnostic = generate_diagnostic_summary()
                st.session_state.diagnostic = diagnostic
                st.success("Diagnostic summary generated!")
            
            if 'diagnostic' in st.session_state:
                st.markdown("### Diagnostic Summary")
                st.markdown(st.session_state.diagnostic)
                
                # User info display in sidebar
                st.markdown("### User Information")
                user_info_text = ""
                for key, value in st.session_state.user_info.items():
                    formatted_key = key.replace('_', ' ').title()
                    user_info_text += f"**{formatted_key}:** {value or 'Not provided'}\n"
                st.markdown(user_info_text)
                
                download_format = st.radio("Select format:", ["TXT", "PDF"])
                
                if download_format == "TXT":
                    file_content = save_diagnostic(st.session_state.diagnostic, format="txt")
                    st.download_button(
                        label="Download Summary (TXT)",
                        data=file_content,
                        file_name=f"diagnostic_{st.session_state.user_info['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                else:
                    file_content = save_diagnostic(st.session_state.diagnostic, format="pdf")
                    st.download_button(
                        label="Download Summary (PDF)",
                        data=file_content,
                        file_name=f"diagnostic_{st.session_state.user_info['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
        
        if st.sidebar.button("End Chat"):
            if len(st.session_state.messages) >= 4 and st.session_state.user_info["name"]:
                if 'diagnostic' not in st.session_state:
                    diagnostic = generate_diagnostic_summary()
                    st.session_state.diagnostic = diagnostic
            reset_chat()
            st.rerun()

def reset_chat():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def main():
    chat_interface()

if __name__ == "__main__":
    main()