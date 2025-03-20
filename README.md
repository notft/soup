# 🌱 Soup's Safe Space - A Mental Health Support Chat for Students

Soup's Safe Space is a supportive chat application designed to provide mental health assistance to college students. This platform offers a safe, confidential environment where students can express their concerns, receive empathetic guidance, and develop healthy coping strategies. Dedicated to that little sister I couldnt help when she was alive. 
Life is not a donation but generations of wealth.

## 🌟 Features

- **Supportive Chat Interface**: A calming, aesthetically pleasing UI designed to create a sense of safety and hope
- **AI-Powered Responses**: Utilizes the Groq API with LLaMa 3.3 (70B) model to generate empathetic and supportive responses
- **Crisis Detection**: Intelligently identifies when a student might need professional help and provides appropriate resources only when necessary
- **Diagnostic Summaries**: Generates comprehensive psychological assessment summaries for counselors (professional use only)
- **Report Generation**: Creates downloadable session reports in TXT or PDF formats
- **Session Management**: Tracks chat duration and handles timeouts automatically

## 📋 Requirements

- Python 3.7+
- Streamlit
- Groq API key
- Additional Python libraries (see `requirements.txt`) 

## 🚀 Installation

1. Clone this repository:
   ```
   git clone https://github.com/notft/soups-safe-space.git
   cd soups-safe-space
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. Run the application:
   ```
   streamlit run main.py
   ```

## 💡 How It Works

The application operates as a conversational interface where:

1. Students start by entering their name to begin a session
2. They can freely express their thoughts, concerns, and feelings
3. The AI responds with supportive, non-judgmental guidance
4. For counselors, diagnostic tools are available in the sidebar
5. Session data can be saved for professional review

## 🔒 Privacy & Ethics

- All conversations are processed through the Groq API
- Session data is stored locally for diagnostic purposes only
- Crisis resources are provided when needed, but not in every interaction
- The application clearly communicates it is not a replacement for professional help

## 🛠️ For Counselors

The sidebar contains tools specifically for mental health professionals:

- Generate diagnostic summaries
- Download session reports in TXT or PDF format
- Track session duration
- End sessions with automatic report generation

## ⚠️ Important Note

This application is designed as a supplementary resource and should not replace professional mental health services. In cases of serious mental health concerns, users are encouraged to seek help from qualified professionals.


## 👥 Contributors

- Aibel Bin Zacariah


Life isnt a donation but generations of wealth. 
