# 🤖 Autonomous Market Research Agent

This is a portfolio project demonstrating an **Autonomous Market Research Agent** built with LangChain, Gemini 1.5 Pro, and Streamlit. 

## Features & Concepts Used

This project implements several advanced GenAI concepts:
1. **Agentic Workflows**: Uses a LangChain Tool Calling Agent equipped with the `DuckDuckGoSearchRun` tool to autonomously browse the web.
2. **Structured Outputs (Pydantic)**: Uses `with_structured_output` to force the LLM to synthesize the raw research into a strictly typed JSON/Pydantic schema (Executive Summary, Key Statistics, Sources).
3. **LCEL (LangChain Expression Language)**: Chains the raw agent response directly into the parsing and formatting pipeline.
4. **Google Gemini API**: A highly capable and cost-effective (free tier available) LLM for reasoning.
5. **Streamlit UI**: A clean, interactive web interface.

## How to Run Locally

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate # or .\venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory and add your Gemini API Key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Deployment (HuggingFace Spaces / Streamlit Cloud)
To deploy this project:
1. Push this repository to GitHub.
2. Go to [HuggingFace Spaces](https://huggingface.co/spaces) and create a new Space.
3. Select **Streamlit** as the SDK.
4. Connect it to your GitHub repository or upload these files.
5. In the Space settings, add your `GEMINI_API_KEY` to the **Secrets**.
