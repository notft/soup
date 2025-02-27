import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from time import time

def initialize_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_started = False
        st.session_state.user_name = None
        st.session_state.session_start = None

def get_ai_response(prompt, conversation_history):
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return "❌ Error: Missing GROQ API Key!"
    
    client = Groq(api_key=api_key)
    
    system_prompt = """You are an empathetic and supportive counselor for college students. 
    Your responses should be:
    1. Compassionate and non-judgmental
    2. Encouraging but realistic
    3. Focused on helping students develop healthy coping strategies
    4. Clear about your role as an AI support tool, not a replacement for professional help
    5. Direct students to professional help when discussing serious issues
    
    If you detect signs of serious mental health concerns, always include information about:
    - The college counseling center
    - 24/7 mental health helpline: 1098
    - Encouraging them to talk to trusted friends, family, or counselors"""
    
    try:
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
        
        return response.choices[0].message.content if response.choices else "❌ AI Response Error!"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def chat_interface():
    st.title("💭 MindfulTalk\nA Safe Space to Share and Heal")
    
    initialize_chat()
    
    # Welcome message and name input if chat hasn't started
    if not st.session_state.chat_started:
        st.markdown("""
        Welcome to MindfulTalk! This is a safe space where you can:
        - Share your thoughts and feelings
        - Get supportive guidance
        - Learn coping strategies
        - Find resources for help
        
        While I'm here to listen and support you, remember that I'm an AI assistant. 
        For serious concerns, please reach out to professional counselors or mental health services.
        """)
        
        user_name = st.text_input("What would you like me to call you?")
        if user_name and st.button("Start Chatting"):
            st.session_state.user_name = user_name
            st.session_state.chat_started = True
            st.session_state.session_start = time()
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Hi {user_name}, I'm here to listen and support you. What's on your mind today?"
            })
            st.rerun()
            
    # Main chat interface
    else:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Share your thoughts..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get AI response
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                conversation_history = [
                    {"role": m["role"], "content": m["content"]} 
                    for m in st.session_state.messages[:-1]
                ]
                response = get_ai_response(prompt, conversation_history)
                st.markdown(response)
                
            # Add AI response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Session timer
        if st.session_state.session_start:
            elapsed_time = int(time() - st.session_state.session_start)
            if elapsed_time < 1800:  # 30 minutes
                st.sidebar.info(f"Chat time: {elapsed_time // 60} minutes")
            else:
                st.warning("Session timeout. Starting new session...")
                reset_chat()
                st.rerun()
        
        # End chat button
        if st.sidebar.button("End Chat"):
            reset_chat()
            st.rerun()

def reset_chat():
    """Reset the chat session"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def main():
    chat_interface()

if __name__ == "__main__":
    main()

