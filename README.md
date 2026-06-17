# Multi-Tool AI Agent

A command-line AI assistant built with Python and LangChain. The agent decides which tool to use based on the user’s request and can use more than one tool when necessary.

## Tools

The project includes three tools:

### Calculator

Supports:

* Addition, subtraction, multiplication, and division
* Percentages
* VAT calculations
* Discounts
* Simple mathematical expressions

Example questions:

* `What is 125 * 42?`
* `Calculate 15% VAT on 250 AED`
* `Calculate monthly payment for 5000 divided by 12`

### Web Search

Uses DuckDuckGo to search for current information.

The tool returns:

* A short summary of the search results
* Source titles
* Source links

Example questions:

* `Latest AI news`
* `What is LangChain?`
* `Recent developments in LLMs`

### PDF Summarizer

Reads the PDF stored at `data/sample.pdf`.

The PDF tool can:

* Extract text
* Generate a summary
* List key takeaways
* Answer questions about the document

It uses a RAG workflow:

1. Extract text from the PDF
2. Split the text into chunks
3. Create embeddings
4. Store the chunks in Chroma
5. Retrieve the most relevant chunks
6. Send the retrieved context to Gemini

Example questions:

* `Summarize this PDF`
* `What are the key points?`
* `What does the document say about security?`

## Agent Behaviour

The agent automatically chooses the correct tool.

Examples:

* A math question uses the Calculator Tool.
* A question about current information uses the Web Search Tool.
* A question about the local PDF uses the PDF Summarizer Tool.

The agent can also use multiple tools in one request.

Example:

`Search for the latest AI news and calculate 10% growth on a budget of 5000 AED.`

For this request, the agent should use both the Web Search Tool and the Calculator Tool, then combine the results.

## LLM Provider

The project uses **Google Gemini 2.5 Flash**.

The assignment mentions the OpenAI API, but Gemini was used based on the previous recommendation to use a free-tier model provider. The LLM can be changed later without changing the individual tools.

## Bonus Features

The project includes three bonus features.

### Conversation Memory

The application keeps the most recent conversation messages so the user can ask follow-up questions.

### Tool Usage History

The application records which tools were used during the current session.

Type:

```text
history
```

to display the tool usage history.

Tool activity is also written to `tool_usage.log`.

### Tool Execution Timing

The application measures how long each tool takes to finish.

Example:

```text
Tool: web_search_tool
Status: Success
Execution time: 2.41 seconds
```

## Project Structure

```text
Task 3 - Multi Tool Agent/
│
├── tools/
│   ├── calculator.py
│   ├── web_search.py
│   └── pdf_summarizer.py
│
├── agent/
│   └── agent.py
│
├── data/
│   └── sample.pdf
│
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

## Setup

### 1. Open the project folder

```bash
cd "Task 3 - Multi Tool Agent"
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install the requirements

```bash
pip install -r requirements.txt
```

If `requirements.txt` has not been created yet, install the packages manually:

```bash
pip install -U langchain langchain-google-genai python-dotenv pypdf duckduckgo-search ddgs langchain-text-splitters langchain-huggingface langchain-chroma sentence-transformers
```

Then generate the requirements file:

```bash
pip freeze > requirements.txt
```

### 4. Add the Gemini API key

Create a `.env` file in the main project folder:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

The `.env.example` file should contain:

```env
GOOGLE_API_KEY=your_api_key_here
```

Do not upload the real `.env` file to GitHub.

### 5. Add a PDF

Place a PDF inside the `data` folder and name it:

```text
sample.pdf
```

The full path should be:

```text
data/sample.pdf
```

The PDF should contain selectable text. Scanned image-only PDFs may not work because OCR is not included.

## Running the Application

Run the main file:

```bash
python app.py
```

The application will start a command-line chat.

Example:

```text
You: Calculate 15% VAT on 250 AED
```

Available commands:

```text
history
```

Shows the tool usage history.

```text
exit
```

Stops the application.

```text
quit
```

Also stops the application.

## Suggested Tests

### Calculator

```text
What is 125 * 42?
```

```text
Calculate 15% VAT on 250 AED
```

```text
Calculate monthly payment for 5000 divided by 12
```

### Web Search

```text
What is the latest AI news?
```

```text
What is LangChain?
```

### PDF

```text
Summarize this PDF
```

```text
What are the key points?
```

```text
What does the document say about security?
```

### Multiple Tools

```text
Search for the latest AI news and calculate 10% growth on a budget of 5000 AED.
```

### Conversation Memory

First ask:

```text
Calculate 15% of 500.
```

Then ask:

```text
Add that result to the original amount.
```

## Error Handling

The project handles common errors such as:

* Empty user input
* Invalid mathematical expressions
* Division by zero
* Missing Gemini API key
* Missing PDF file
* PDFs with no extractable text
* Web search errors
* Tool execution errors

## Logging

Tool activity is stored in:

```text
tool_usage.log
```

Each record can include:

* User question
* Tool name
* Tool status
* Execution time
* Application errors

## Challenges

### Tool Routing

The descriptions of the tools and the agent prompt needed to be clear enough for the agent to choose the correct tool.

### PDF Question Answering

Sending the entire PDF to the model for every question would be inefficient. Text splitting, embeddings, Chroma, and similarity search were used to retrieve only the relevant sections.

### Current Information

The language model may not have recent information, so DuckDuckGo search was added to provide current results and source links.

### Memory Management

Conversation memory was limited so the history would not continue growing during a long session.

### Tool Tracking

LangChain callbacks were used to record which tool was called and how long it took.

## Lessons Learned

This project helped me practise:

* Creating custom LangChain tools
* Building a tool-calling agent
* Routing requests to the correct tool
* Using more than one tool for a single request
* Handling tool and API errors
* Managing environment variables
* Adding conversation memory
* Logging tool usage
* Measuring tool execution time
* Extracting text from PDFs
* Splitting text into chunks
* Creating embeddings
* Using Chroma for vector search
* Building a basic RAG workflow
* Organizing a Python project into separate modules

## Limitations

* The current version reads one PDF named `sample.pdf`.
* It does not include a graphical interface.
* Scanned PDFs are not supported without OCR.
* Conversation memory resets when the application closes.
* Web search depends on internet access and DuckDuckGo availability.
* Gemini requires a valid API key and internet connection.

## Possible Improvements

Future versions could include:

* A Streamlit interface
* PDF uploads
* Support for multiple PDFs
* Persistent conversation memory
* Response caching
* Unit tests
* A persistent Chroma database
* Support for other LLM providers
