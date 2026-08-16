import streamlit as st
import os
import tempfile
import ast
from langchain_core.messages import HumanMessage, AIMessage
from agent import get_agent_executor, process_document, generate_structured_report

st.set_page_config(page_title="Conversational RAG Agent", page_icon="🤖", layout="wide")

st.title("🤖 Advanced Research Assistant")
st.markdown("Equipped with **Memory**, **Web Search**, and **Document RAG**.")


def clean_agent_output(output):
    if isinstance(output, list):
        return "".join(
            [
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in output
            ]
        )

    if (
        isinstance(output, str)
        and output.strip().startswith("[{")
        and output.strip().endswith("}]")
    ):
        try:
            parsed = ast.literal_eval(output)
            if isinstance(parsed, list):
                return "".join(
                    [
                        block.get("text", "") if isinstance(block, dict) else str(block)
                        for block in parsed
                    ]
                )
        except Exception:
            pass
    return output


# 1. Sidebar Configuration & File Upload
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    st.header("📄 Document RAG")
    uploaded_file = st.file_uploader("Upload a PDF to chat with it", type=["pdf"])

    if uploaded_file:
        if (
            "retriever_tool" not in st.session_state
            or st.session_state.get("uploaded_file_name") != uploaded_file.name
        ):
            if not os.getenv("GEMINI_API_KEY"):
                st.error("Please enter Gemini API Key first to generate embeddings.")
            else:
                with st.spinner("Processing PDF and building Vector Store..."):
                    # Save uploaded file to a temporary file
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".pdf"
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name

                    # Process the document to get the retriever tool
                    try:
                        retriever_tool = process_document(tmp_file_path)
                        st.session_state.retriever_tool = retriever_tool
                        st.session_state.uploaded_file_name = uploaded_file.name
                        st.success(
                            "Document Vector Store Built! The agent can now read your PDF."
                        )
                    except Exception as e:
                        st.error(f"Error processing PDF: {e}")
        else:
            st.success(f"Loaded: {uploaded_file.name}")
    else:
        if "retriever_tool" in st.session_state:
            del st.session_state["retriever_tool"]
        if "uploaded_file_name" in st.session_state:
            del st.session_state["uploaded_file_name"]

    st.header("📊 Structured Reporting")
    if st.button("Generate Final Report"):
        if "messages" in st.session_state and len(st.session_state.messages) > 0:
            with st.spinner("Synthesizing conversation into a structured report..."):
                # Join the conversation history into a single text block
                chat_text = "\n".join(
                    [f"{msg.type}: {msg.content}" for msg in st.session_state.messages]
                )
                report = generate_structured_report(chat_text)

                st.success("Report Generated!")
                st.subheader("Executive Summary")
                st.write(report.executive_summary)

                st.subheader("Key Statistics")
                for stat in report.key_statistics:
                    st.markdown(f"- {stat}")

                st.subheader("Sources / Entities")
                for source in report.sources_used:
                    st.markdown(f"- {source}")
        else:
            st.warning("Chat history is empty. Start a conversation first!")

# 2. Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.markdown(message.content)

# 3. Chat Input and Agent Execution
if prompt := st.chat_input("Ask me anything or ask about the uploaded PDF..."):
    if not os.getenv("GEMINI_API_KEY"):
        st.error("Please provide a Gemini API Key in the sidebar.")
    else:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add to history
        st.session_state.messages.append(HumanMessage(content=prompt))

        # Display assistant thinking
        with st.chat_message("assistant"):
            with st.spinner("Agent is thinking and using tools..."):
                try:
                    # Get the agent (passing the retriever tool if it exists)
                    retriever_tool = st.session_state.get("retriever_tool")
                    agent_executor = get_agent_executor(retriever_tool)

                    # We pass the prior history (excluding the current prompt we just appended)
                    history_for_agent = st.session_state.messages[:-1]

                    # Invoke Agent
                    result = agent_executor.invoke(
                        {"input": prompt, "chat_history": history_for_agent}
                    )

                    response_text = clean_agent_output(result["output"])
                    st.markdown(response_text)

                    # Save assistant response to history
                    st.session_state.messages.append(AIMessage(content=response_text))

                except Exception as e:
                    st.error(f"An error occurred: {e}")
