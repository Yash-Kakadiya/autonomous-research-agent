import streamlit as st
import os
from agent import run_research

# Streamlit UI Configuration
st.set_page_config(
    page_title="Autonomous Research Agent", page_icon="🤖", layout="centered"
)

st.title("🤖 Autonomous Market Research Agent")
st.markdown("""
This app uses **LangChain**, **Gemini 3 Flash Preview**, and **DuckDuckGo** to autonomously research a topic and generate a structured report. 
Enter a topic below to get started!
""")

# API Key handling in UI (useful for deployment)
api_key = st.sidebar.text_input(
    "Gemini API Key (Optional if set in .env)", type="password"
)
if api_key:
    os.environ["GEMINI_API_KEY"] = api_key

topic = st.text_input(
    "What would you like to research?",
    placeholder="e.g., Electric Vehicle market trends in 2026",
)

if st.button("Generate Report"):
    if not os.getenv("GEMINI_API_KEY"):
        st.error("Please provide a Gemini API Key in the sidebar or your .env file.")
    elif not topic:
        st.warning("Please enter a research topic.")
    else:
        with st.spinner(f"Agent is searching the web for: '{topic}'..."):
            try:
                # Call our LCEL pipeline
                report = run_research(topic)

                # Render the Output
                st.success("Research Complete!")

                st.subheader("Executive Summary")
                st.write(report.executive_summary)

                st.subheader("Key Statistics")
                for stat in report.key_statistics:
                    st.markdown(f"- {stat}")

                st.subheader("Sources / Entities Referenced")
                for source in report.sources_used:
                    st.markdown(f"- {source}")

            except Exception as e:
                st.error(f"An error occurred: {e}")
