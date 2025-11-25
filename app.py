import os
import io

from dotenv import load_dotenv

import streamlit as st
import litellm
import PyPDF2

load_dotenv()

#Litellm API Key
litellm.api_key = os.getenv("OPENAI_API_KEY")

#Set page title
st.set_page_config(page_title="AI Note Summarizer and Quiz Generator", layout="wide")

#Set the title of the Streamlit app
st.title("🧠 AI Note Summarizer and Quiz Generator")
st.markdown("Turn your notes into knowledge — instantly.")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# Create two columns for input options
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Option 1: Paste Text")
    notes = st.text_area("Paste your notes or lecture content here:", height=300, key="text_input")

with col2:
    st.subheader("📄 Option 2: Upload PDF")
    uploaded_file = st.file_uploader("Upload a PDF file:", type="pdf")
    pdf_notes = ""
    if uploaded_file is not None:
        pdf_notes = extract_text_from_pdf(uploaded_file)
        st.success(f"✅ PDF uploaded! ({len(pdf_notes)} characters extracted)")
        if st.checkbox("Preview PDF text"):
            st.text_area("Extracted PDF content:", pdf_notes, height=200, disabled=True)

# Use PDF text if available, otherwise use pasted text
final_notes = pdf_notes if pdf_notes else notes

#Choose a task type: Summarize notes or Generate quiz
st.markdown("---")
st.subheader("⚙️ What would you like to do?")
task = st.radio("", ["Summarize Notes", "Generate Quiz"], horizontal=True)

#If the user clicks the button without pasting any notes
if st.button("🚀 Start", use_container_width=True):
    if final_notes.strip() == "":
    # .strip checks if user left notes box empty + removes leading spaces and tabs
        st.warning("Please paste some notes or upload a PDF first!")
    else:
        #Define the prompt based on selected task
        if task == "Summarize Notes":
            prompt = f"Summarize the following notes in a clear and concise way: \n\n{final_notes}"
            #  \n\n  starts 2 new lines
            #  {notes} = a placeholder that gets replaced with actual notes from user
        else:
            prompt = f"Generate a quiz with 5-10 multiple-choice questions based on the following notes. Format each question clearly with options A, B, C, D and indicate the correct answer: \n\n{final_notes}"

        #  Call Litellm to get response
        try:
            with st.spinner("🤖 AI is processing your request..."):
                response = litellm.completion(
                    model = "gpt-4o",   #what AI model would be used
                    messages = [
                        {"role": "system", "content": "You are a helpful assistant that creates clear summaries and well-structured quizzes."},  #sets tone and personality of AI (system)
                        {"role": "user", "content": prompt}   # your actual request (asking AI to summarize or generate)
                    ]
                )

                # Display AI's response
                output = response["choices"][0]["message"]["content"]   #means get the first message the AI sent back and take the actual text it wrote
                st.success("✨ Here is what the AI generated:")
                st.markdown(output)
                
                # Add copy button functionality
                st.markdown("---")
                if st.button("📋 Copy to clipboard"):
                    st.write("(Use Ctrl+C to copy the text above)")
        #  give an error if smth is wrong
        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")
#Make "start" button round and longer with custom styling
st.markdown(
    """
    <style>
    .stButton > button {
        border-radius: 50px;    
        padding: 0.75em 2em; 
        font-size: 16px;
        background: linear-gradient(135deg, #4da1af 0%, #2d7a84 100%);
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(77, 161, 175, 0.4);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>"
    "Made with ❤️ for students and educators | Powered by LiteLLM & Streamlit"
    "</p>",
    unsafe_allow_html=True
)




