import os
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI


try:
    from langchain_core.tools import tool
except ImportError:
    def tool(function):
        return function


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_PDF_FILE = (
    PROJECT_ROOT
    / "data"
    / "AI_and_Future_Jobs_20_Page_Report.pdf"
)

current_pdf_file = DEFAULT_PDF_FILE
vector_store = None


def select_pdf(pdf_path):

    global current_pdf_file
    global vector_store

    cleaned_path = pdf_path.strip().strip('"')
    selected_file = Path(cleaned_path).expanduser()

    if not selected_file.exists():
        return "PDF error: The selected file does not exist."

    if not selected_file.is_file():
        return "PDF error: The selected path is not a file."

    if selected_file.suffix.lower() != ".pdf":
        return "PDF error: Please select a PDF file."

    current_pdf_file = selected_file.resolve()

    # Reset the vector store because a different PDF was selected.
    vector_store = None

    return "PDF selected successfully: " + current_pdf_file.name


def get_selected_pdf_name():

    return current_pdf_file.name

# Read text from data/sample.pdf.
def read_pdf_text():

    if not current_pdf_file.exists():
        return "PDF error: The selected PDF file was not found."

    try:
        reader = PdfReader(str(current_pdf_file))

        full_text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                full_text = full_text + page_text + "\n"

        if full_text.strip() == "":
            return "PDF error: No text could be extracted from this PDF."

        return full_text

    except Exception as error:
        return "PDF error: " + str(error)


# Split the PDF text into smaller chunks.
def split_text(text):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_text(text)

    return chunks

# Build a Chroma vector store from the PDF chunks.
def build_vector_store():

    global vector_store

    if vector_store is not None:
        return vector_store

    text = read_pdf_text()

    if text.startswith("PDF error:"):
        return text

    chunks = split_text(text)

    documents = []

    for chunk in chunks:
        document = Document(page_content=chunk)
        documents.append(document)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings
    )

    return vector_store

# Search the PDF and return the most relevant chunks.
def search_pdf(question):

    store = build_vector_store()

    if isinstance(store, str):
        return store

    results = store.similarity_search(question, k=4)

    context = ""

    for result in results:
        context = context + result.page_content + "\n\n"

    return context

# Ask Gemini to answer using the PDF context.
def ask_gemini(user_question, context):

    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        return "Gemini error: GOOGLE_API_KEY was not found in the .env file."

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3
        )

        prompt = f"""
You are a helpful PDF assistant.

Use only the PDF context below to answer the user.

PDF context:
{context}

User question:
{user_question}

Give a clear and simple answer.
If the user asks for a summary, summarize the document.
If the user asks for key points, list the key points.
If the answer is not found in the PDF context, say that you could not find it in the PDF.
"""

        response = llm.invoke(prompt)

        return response.content

    except Exception as error:
        return "Gemini error: " + str(error)

# Main PDF tool function.
def pdf_summarizer(user_question):

    question_lower = user_question.lower()

    summary_keywords = [
        "summarize",
        "summary",
        "key points",
        "key takeaways",
        "main points",
        "overview"
    ]

    is_full_document_request = any(
        keyword in question_lower
        for keyword in summary_keywords
    )

    if is_full_document_request:
        # Use the complete document for summaries and key points.
        context = read_pdf_text()
    else:
        # Use RAG retrieval for specific document questions.
        context = search_pdf(user_question)

    if context.startswith("PDF error:"):
        return context

    if context.strip() == "":
        return "PDF error: No relevant PDF content was found."

    return ask_gemini(user_question, context)

@tool
def pdf_summarizer_tool(user_question: str) -> str:
    """
    Use this tool to summarize the PDF, list its key points,
    or answer questions about the PDF document.
    """
    return pdf_summarizer(user_question)


if __name__ == "__main__":
    test_questions = [
        "Summarize this PDF",
        "What are the key points?",
        "What does the document say about security?",
    ]

    for question in test_questions:
        print("Question:", question)
        print(pdf_summarizer(question))
        print("-" * 50)