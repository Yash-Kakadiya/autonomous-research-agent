# 🤖 Autonomous Research Assistant

Welcome to the **Autonomous Research Assistant**! This is a beginner-friendly, fully open-source portfolio project demonstrating how to build a powerful AI agent using LangChain, Google's Gemini LLM, and Streamlit.

This app is designed to act as your personal researcher. You can ask it questions, and it will autonomously browse the internet or read through a PDF you upload to find the answers. Once you're done chatting, it can automatically synthesize everything you talked about into a perfectly formatted PDF report!

---

## 🌟 What Can This App Do?

- **💬 Conversational Memory**: It remembers what you talked about earlier in the chat.
- **🌐 Autonomous Web Search**: If you ask it a question about current events or facts it doesn't know, it will automatically use DuckDuckGo to search the web for the answer.
- **📄 Document RAG (Chat with PDFs)**: You can upload any PDF (up to 5MB). The agent will read it, memorize it, and accurately answer questions based *only* on the document's contents.
- **📊 Structured Report Generation**: With the click of a button, the agent will analyze your entire conversation and format it into a professional Research Report (complete with an Executive Summary, Key Statistics, and Sources).
- **📥 Export to PDF**: You can instantly download your final Research Report as a formatted PDF.

---

## 🧠 Core AI Concepts Explained (For Beginners)

If you have zero knowledge of AI development, this repository is a perfect place to learn! Here are the core concepts powering this app:

1. **Agentic Workflows**: Standard chatbots just reply to you. An "Agent" is a chatbot equipped with *Tools*. When you ask our agent a question, it pauses, decides if it needs to use a tool (like "Search the Web" or "Search the PDF"), uses the tool, reads the result, and *then* replies to you. 
2. **RAG (Retrieval-Augmented Generation)**: Large Language Models (like ChatGPT or Gemini) don't know the contents of your personal PDFs. RAG is a technique where we take your PDF, chop it into small paragraphs, and convert those paragraphs into numbers (Embeddings). When you ask a question, the app finds the most relevant paragraphs using math, and hands them to the AI so it can answer your question accurately. We use **FAISS** for this.
3. **Structured Outputs (Pydantic)**: Normally, AI generates free-flowing text. In this app, when you click "Generate Final Report", we force the AI to return data in a strict JSON format (an Executive Summary, a list of Statistics, and a list of Sources).
4. **Google Gemini 3.5 API**: We use Google's Gemini model for the AI's "brain" because it is incredibly fast, smart, and offers a generous free tier for developers!

---

## 🛠️ Step-by-Step Setup Guide

Follow these steps to run this app on your own computer:

### 1. Prerequisites
- Install **Python 3.10** or higher on your computer.
- Get a **Free Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Download the Code
Clone this repository to your computer, or download it as a ZIP file and extract it.

### 3. Install Dependencies
Open your terminal (or Command Prompt / PowerShell) and navigate to the project folder. Run the following commands:

```bash
# Create an isolated virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows use: venv\Scripts\activate
# On Mac/Linux use: source venv/bin/activate

# Install all required libraries
pip install -r requirements.txt
```

### 4. Add Your API Key
You can either:
- Type your Gemini API key directly into the sidebar of the app while it's running.
- **OR** create a file named `.env` in the same folder as `app.py` and write your key inside it like this:
  ```
  GEMINI_API_KEY=your_api_key_here
  ```

### 5. Run the App!
Run this command in your terminal:
```bash
streamlit run app.py
```
Your browser will automatically open a new tab with the app running!

---

## 🚀 How to Use the App

1. **Enter your API Key** in the left sidebar (if you didn't use a `.env` file).
2. **Ask a question** in the chat box at the bottom. Try asking about today's news! The app will open a "Thinking..." box and search the web.
3. **Upload a PDF** in the sidebar. Once it processes, ask the agent a question about the PDF. The agent will automatically switch from searching the web to searching your document.
4. **Generate a Report**: When you are satisfied with your research, click the **"Generate Final Report"** button in the sidebar.
5. **Download**: On the report page, you can copy the raw Markdown, or click **"Create PDF"** to download a clean, formatted PDF copy of your research!

---

## 🌍 Deployment (Hosting it on the Internet)

Want to share your app with the world? The easiest way is using **HuggingFace Spaces** or **Streamlit Community Cloud**:

1. Push your code to a public GitHub repository.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/) or [HuggingFace Spaces](https://huggingface.co/spaces).
3. Create a new app and connect it to your GitHub repository.
4. In the hosting platform's settings, find the "Secrets" or "Environment Variables" section and add your `GEMINI_API_KEY`.
5. Deploy! Your app will be live on a public URL.

---


## 📜 License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

<br>
<div align="center">
  <b>Developed with 💖 by <a href="https://github.com/Yash-Kakadiya" target="_blank" style="text-decoration:none; color:#F4C430;"> ¥@$# Kakadiya</a></b>
</div>