import streamlit as st
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from datetime import datetime, timezone

@st.cache_resource
def start_health_server():
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/api/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "ok",
                    "message": "Server is healthy",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                
        def log_message(self, format, *args):
            pass  # Suppress logs

    def run_server():
        server = HTTPServer(('0.0.0.0', 8000), HealthCheckHandler)
        server.serve_forever()

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread

start_health_server()

import os
import tempfile
import ast
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.callbacks import BaseCallbackHandler
from agent import get_agent_executor, process_document, generate_structured_report
from fpdf import FPDF

st.set_page_config(page_title="Conversational RAG Agent", page_icon="🤖", layout="wide")


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


class SimpleStreamlitCallbackHandler(BaseCallbackHandler):
    def __init__(self, status_container):
        self.status_container = status_container

    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name", "Tool")
        self.status_container.write(f"🔍 **{tool_name}**: Searching... {input_str}")

    def on_tool_end(self, output, **kwargs):
        self.status_container.write("✅ Analyzed search results.")


def safe_text(text):
    if not text:
        return ""
    
    import textwrap
    # Remove all non-ASCII/non-printable characters to prevent fpdf font crashes
    safe_chars = []
    for char in str(text):
        if 32 <= ord(char) <= 126 or char == '\n':
            safe_chars.append(char)
        elif char == '\t':
            safe_chars.append(' ')
    text = "".join(safe_chars)
    
    # Process line by line and forcefully wrap text at 70 characters
    lines = text.split('\n')
    wrapped_lines = []
    for line in lines:
        if line.strip():
            wrapped_lines.extend(textwrap.wrap(line, width=70, break_long_words=True, replace_whitespace=False))
        else:
            wrapped_lines.append("")
            
    text = "\n".join(wrapped_lines)
    return text.encode("latin-1", "replace").decode("latin-1")


def create_pdf(report):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=16, style="B")
    pdf.cell(0, 10, txt="Research Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Helvetica", size=14, style="B")
    pdf.cell(0, 10, txt="Executive Summary", ln=True)
    pdf.set_font("Helvetica", size=12)
    for line in safe_text(report.executive_summary).split('\n'):
        pdf.cell(0, 10, txt=line, ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", size=14, style="B")
    pdf.cell(0, 10, txt="Key Statistics", ln=True)
    pdf.set_font("Helvetica", size=12)
    for stat in report.key_statistics or []:
        for line in safe_text(f"- {stat}").split('\n'):
            pdf.cell(0, 10, txt=line, ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", size=14, style="B")
    pdf.cell(0, 10, txt="Sources / Entities", ln=True)
    pdf.set_font("Helvetica", size=12)
    for source in report.sources_used or []:
        for line in safe_text(f"- {source}").split('\n'):
            pdf.cell(0, 10, txt=line, ln=True)

    return bytes(pdf.output(dest="S"))


def copy_to_clipboard_html(text):
    import base64
    import streamlit.components.v1 as components

    # Base64 encode the text to avoid Javascript escaping issues
    text_b64 = base64.b64encode(text.encode("utf-8")).decode("utf-8")
    html_code = f"""
    <button id="copyBtn" onclick="copyFunction()" style="padding: 0.5rem 1rem; background-color: transparent; color: #007bff; border: 1px solid #ccc; border-radius: 0.5rem; cursor: pointer; font-family: sans-serif;">
        📋 Copy Markdown
    </button>
    <script>
        function copyFunction() {{
            // Decode base64 to get original string
            var textToCopy = decodeURIComponent(escape(window.atob('{text_b64}')));
            
            // Modern async clipboard API
            if (navigator.clipboard && window.isSecureContext) {{
                navigator.clipboard.writeText(textToCopy).then(function() {{
                    document.getElementById("copyBtn").innerText = "✅ Copied!";
                    setTimeout(() => document.getElementById("copyBtn").innerText = "📋 Copy Markdown", 2000);
                }});
            }} else {{
                // Fallback for older browsers or non-HTTPS
                let textArea = document.createElement("textarea");
                textArea.value = textToCopy;
                textArea.style.position = "fixed";
                textArea.style.left = "-999999px";
                textArea.style.top = "-999999px";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {{
                    document.execCommand('copy');
                    document.getElementById("copyBtn").innerText = "✅ Copied!";
                    setTimeout(() => document.getElementById("copyBtn").innerText = "📋 Copy Markdown", 2000);
                }} catch (err) {{
                    console.error('Fallback: Oops, unable to copy', err);
                }}
                document.body.removeChild(textArea);
            }}
        }}
    </script>
    """
    components.html(html_code, height=50)


def render_report_page():
    report = st.session_state.current_report

    markdown_report = (
        f"""# Executive Summary\n{report.executive_summary}\n\n## Key Statistics\n"""
    )
    markdown_report += "\n".join(["- " + stat for stat in report.key_statistics])
    markdown_report += """\n\n## Sources / Entities\n"""
    markdown_report += "\n".join(["- " + source for source in report.sources_used])

    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("📄 Final Research Report")
    with col2:
        st.write("")  # Padding to align vertically
        copy_to_clipboard_html(markdown_report)

    st.markdown(markdown_report)

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Go back to conversation"):
            st.session_state.page = "chat"
            st.rerun()

    with col2:
        pdf_bytes = create_pdf(report)
        st.download_button(
            label="📄 Create PDF",
            data=pdf_bytes,
            file_name="research_report.pdf",
            mime="application/pdf",
        )


def render_chat_page():
    st.title("🤖 Advanced Research Assistant")
    st.markdown("Equipped with **Memory**, **Web Search**, and **Document RAG**.")

    with st.sidebar:
        # i want header and get free button in a single line, with the button aligned to the right of the header
        col1, col2 = st.columns([1, 1])
        with col1:
            st.header("⚙️ API Key")
        with col2:
            st.link_button(
                "Get Free ✨ Key", url="https://aistudio.google.com/api-keys"
            )
        api_key = st.text_input("Gemini API Key", type="password")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key

        st.header("📄 Document RAG")
        uploaded_file = st.file_uploader("Upload a PDF to chat with it", type=["pdf"])

        if uploaded_file:
            if uploaded_file.size > 5 * 1024 * 1024:
                st.error("File size exceeds 5MB limit. Please upload a smaller PDF.")
            else:
                if (
                    "retriever_tool" not in st.session_state
                    or st.session_state.get("uploaded_file_name") != uploaded_file.name
                ):
                    if not os.getenv("GEMINI_API_KEY"):
                        st.error(
                            "Please enter Gemini API Key first to generate embeddings."
                        )
                    else:
                        with st.spinner("Processing PDF and building Vector Store..."):
                            with tempfile.NamedTemporaryFile(
                                delete=False, suffix=".pdf"
                            ) as tmp_file:
                                tmp_file.write(uploaded_file.read())
                                tmp_file_path = tmp_file.name

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
                with st.spinner(
                    "Synthesizing conversation into a structured report..."
                ):
                    chat_text = "\n".join(
                        [
                            f"{msg.type}: {msg.content}"
                            for msg in st.session_state.messages
                        ]
                    )
                    report = generate_structured_report(chat_text)

                    st.session_state.current_report = report
                    st.session_state.page = "report"
                    st.rerun()
            else:
                st.warning("Chat history is empty. Start a conversation first!")

    for message in st.session_state.messages:
        with st.chat_message(
            "user" if isinstance(message, HumanMessage) else "assistant"
        ):
            st.markdown(message.content)

    if prompt := st.chat_input("Ask me anything or ask about the uploaded PDF..."):
        if not os.getenv("GEMINI_API_KEY"):
            st.error("Please provide a Gemini API Key in the sidebar.")
        else:
            with st.chat_message("user"):
                st.markdown(prompt)

            st.session_state.messages.append(HumanMessage(content=prompt))

            with st.chat_message("assistant"):
                with st.status(
                    "Agent is thinking and using tools...", expanded=True
                ) as status:
                    try:
                        retriever_tool = st.session_state.get("retriever_tool")
                        agent_executor = get_agent_executor(retriever_tool)

                        history_for_agent = st.session_state.messages[:-1]

                        st_callback = SimpleStreamlitCallbackHandler(status)

                        result = agent_executor.invoke(
                            {"input": prompt, "chat_history": history_for_agent},
                            {"callbacks": [st_callback]},
                        )
                        status.update(
                            label="Response formulated!",
                            state="complete",
                            expanded=True,
                        )

                    except Exception as e:
                        status.update(
                            label="Error occurred", state="error", expanded=False
                        )
                        st.error(f"An error occurred: {e}")
                        result = None

                if result:
                    response_text = clean_agent_output(result["output"])
                    st.markdown(response_text)

                    st.session_state.messages.append(AIMessage(content=response_text))


if "page" not in st.session_state:
    st.session_state.page = "chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.page == "chat":
    render_chat_page()
elif st.session_state.page == "report":
    render_report_page()
