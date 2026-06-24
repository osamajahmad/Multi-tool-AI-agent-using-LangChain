# Multi-Tool AI Agent

A multi-tool AI assistant built with Python and LangChain.

The agent analyzes each request, automatically selects the appropriate tool, and can use multiple tools when a request requires more than one operation.

The project supports two interfaces:

* Command-line interface
* WhatsApp through the Twilio WhatsApp Sandbox

This project was developed for the **AI Intern – Week 3 Assignment**.

---

## Project Deliverables

### Source Code Repository

[GitHub Repository](https://github.com/osamajahmad/Multi-tool-AI-agent-using-LangChain)

### Architecture Diagram

![Multi-Tool AI Agent Architecture](docs/architecture_diagram.png)

### Demo Video

[Watch the Demo Video](https://youtu.be/nj5EwYUReVg)

---

## Main Features

The project includes:

* Automatic tool selection
* Multi-tool request handling
* Calculator Tool
* Web Search Tool
* PDF Summarizer Tool
* Conversation memory
* Tool usage history
* Tool execution timing
* Logging
* Error handling
* PDF Retrieval-Augmented Generation
* Command-line interface
* WhatsApp integration
* Background processing for slower requests

Example multi-tool request:

```text
Search for the latest AI news and calculate 10% growth on a budget of 5000 AED.
```

For this request, the agent:

1. Uses the Web Search Tool to retrieve current AI information.
2. Uses the Calculator Tool to calculate the budget growth.
3. Combines both results into one final response.

---

## Tools

### 1. Calculator Tool

The Calculator Tool handles common mathematical requests.

It supports:

* Addition
* Subtraction
* Multiplication
* Division
* Percentages
* VAT calculations
* Discounts
* Monthly-payment calculations
* Mathematical expressions
* Brackets
* Decimal values
* Negative values

Example questions:

```text
What is 125 * 42?
```

```text
Calculate 15% VAT on 250 AED.
```

```text
Calculate monthly payment for 5000 divided by 12.
```

```text
Calculate a 20% discount on 300 AED.
```

The tool also handles invalid expressions and division-by-zero errors.

---

### 2. Web Search Tool

The Web Search Tool uses DuckDuckGo to retrieve current information.

It returns:

* A concise summary
* Source titles
* Source links

Example questions:

```text
What is the latest AI news?
```

```text
What is LangChain?
```

```text
What are the recent developments in large language models?
```

The Web Search Tool is used when the request requires current information that may not exist in the language model’s built-in knowledge.

Internet access is required.

---

### 3. PDF Summarizer Tool

The PDF Summarizer Tool can:

* Extract text from a PDF
* Generate a document summary
* List key takeaways
* Answer questions about the document
* Search for specific information inside the document

The default PDF is stored at:

```text
data/AI_and_Future_Jobs_20_Page_Report.pdf
```

Example questions:

```text
Summarize this PDF.
```

```text
What are the key points?
```

```text
What does the document say about security?
```

```text
What does the document say about future jobs?
```

In the command-line interface, the user can enter:

```text
pdf
```

and provide the full path to another PDF file.

The PDF must contain selectable text. Scanned image-only PDFs are not supported because OCR is not included.

The WhatsApp interface currently answers questions using the PDF already configured in the project. It does not accept PDF attachments through WhatsApp.

---

## PDF RAG Workflow

The PDF tool uses Retrieval-Augmented Generation, also known as RAG.

The workflow is:

1. Extract text from the PDF using PyPDF.
2. Split the extracted text into smaller chunks.
3. Convert the chunks into embeddings.
4. Store the embeddings in a Chroma vector store.
5. Retrieve the chunks most relevant to the user’s question.
6. Send the relevant context to Gemini.
7. Generate an answer based on the document content.

For full-document requests such as summaries and key takeaways, the tool uses the complete extracted text.

For specific questions, the tool uses similarity search to retrieve the most relevant document sections.

The embedding model used is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

---

## Agent Logic

The LangChain agent understands the request and decides which tool should be used.

| User request                                    | Tool selected                   |
| ----------------------------------------------- | ------------------------------- |
| `What is 125 * 42?`                             | Calculator Tool                 |
| `What is the latest AI news?`                   | Web Search Tool                 |
| `Summarize this PDF.`                           | PDF Summarizer Tool             |
| `Search for AI news and calculate 10% of 5000.` | Web Search and Calculator Tools |

The agent can also answer general questions directly when no external tool is required.

The agent instructions help it:

* Select the correct tool
* Use multiple tools when needed
* Avoid unnecessary tool calls
* Return a clear final response
* Handle tool failures gracefully

---

## LLM Provider

The project uses:

```text
Google Gemini 2.5 Flash
```

The assignment originally mentions the OpenAI API. Gemini was used because it provides a suitable free-tier option for development and testing.

Gemini is connected through:

```text
langchain-google-genai
```

The model temperature is set to:

```text
0.3
```

This helps produce clear and consistent responses while allowing some flexibility.

The project structure allows the model provider to be changed later without rewriting the individual tools.

---

## WhatsApp Integration

The Task 3 agent is connected to WhatsApp through the Twilio WhatsApp Sandbox.

The same LangChain agent and tools used by the command-line application are reused by the WhatsApp interface.

### WhatsApp Flow

```text
WhatsApp User
      ↓
Twilio WhatsApp Sandbox
      ↓
ngrok HTTPS Tunnel
      ↓
Flask Webhook
whatsapp_app.py
      ↓
LangChain Agent
      ↓
Calculator / Web Search / PDF Summarizer
      ↓
Twilio REST API
      ↓
WhatsApp User
```

When a WhatsApp message arrives:

1. Twilio sends the message to the Flask webhook.
2. Flask reads the message and sender number.
3. The request is submitted to a background worker.
4. The user immediately receives an acknowledgement.
5. The agent selects and executes the required tool or tools.
6. The completed answer is sent through the Twilio REST API.

The immediate acknowledgement is:

```text
Your request is being processed. I will send the answer shortly.
```

Background processing prevents Twilio from waiting while Gemini, web search, or PDF processing completes.

The integration also provides:

* Separate conversation memory for each WhatsApp user
* Duplicate webhook protection
* Tool tracking and execution timing
* Error handling
* A maximum of two simultaneous background requests
* One final WhatsApp response limited to 1,500 characters

Additional requests wait in the background queue until a worker becomes available.

---

## Bonus Features

The assignment requires any two bonus features. This project includes three.

### 1. Conversation Memory

The application stores the latest five conversation messages.

This allows users to ask follow-up questions.

Example:

```text
Calculate 15% of 500.
```

Then:

```text
Add that result to the original amount.
```

The command-line memory resets when the application closes.

The WhatsApp interface maintains separate memory for each sender and resets when the Flask server restarts.

---

### 2. Tool Usage History

The command-line interface records the tools used during the current session.

Enter:

```text
history
```

to display the tool history.

Example output:

```text
Request 1
Question: What is 125 * 42?
Tool: calculator_tool
Status: Success
Execution time: 0.01 seconds
```

The history includes:

* User question
* Tool name
* Tool status
* Execution time

The WhatsApp interface records similar information in the terminal and log file.

---

### 3. Tool Execution Timing

LangChain callbacks measure how long each tool takes to complete.

Example:

```text
Tool: web_search_tool
Status: Success
Execution time: 2.41 seconds
```

This helps monitor performance and identify slow operations.

---

## Logging

Tool activity and application errors are stored in:

```text
tool_usage.log
```

The log may include:

* User questions
* Tool names
* Tool status
* Execution time
* Agent errors
* Application errors
* WhatsApp processing errors
* Twilio sending errors

The log file is created automatically when the application runs.

It should not be included in the repository or submission ZIP if it contains unnecessary local testing data.

---

## Project Structure

```text
Task 3/
│
├── agent/
│   └── agent.py
│
├── tools/
│   ├── calculator.py
│   ├── web_search.py
│   └── pdf_summarizer.py
│
├── data/
│   └── AI_and_Future_Jobs_20_Page_Report.pdf
│
├── docs/
│   └── architecture_diagram.png
│
├── app.py
├── whatsapp_app.py
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

---

## File Responsibilities

### `app.py`

The main command-line application.

It is responsible for:

* Reading user input
* Displaying agent responses
* Managing conversation memory
* Recording tool history
* Measuring tool execution time
* Writing activity to the log file
* Handling commands such as `history`, `pdf`, `exit`, and `quit`

It also contains shared components used by the WhatsApp interface:

* `ToolTracker`
* `extract_answer_text`
* `keep_last_five_messages`

---

### `whatsapp_app.py`

Connects the Task 3 agent to WhatsApp.

It is responsible for:

* Creating the Flask application
* Receiving Twilio webhook requests
* Reading incoming WhatsApp messages
* Reading the sender’s WhatsApp number
* Preventing duplicate message processing
* Maintaining separate user conversations
* Processing requests in background threads
* Returning an immediate acknowledgement
* Sending final answers through the Twilio REST API
* Logging tool activity and application errors

---

### `agent/agent.py`

Creates and configures the LangChain agent.

It is responsible for:

* Initializing Gemini
* Registering the tools
* Defining the agent instructions
* Creating the tool-calling agent
* Creating the `AgentExecutor`

---

### `tools/calculator.py`

Contains the calculator logic and Calculator LangChain tool.

---

### `tools/web_search.py`

Contains the DuckDuckGo search logic, result formatting, summaries, and source links.

---

### `tools/pdf_summarizer.py`

Contains:

* PDF text extraction
* Text splitting
* Embedding creation
* Chroma vector storage
* Similarity search
* PDF summarization
* PDF question answering

---

### `data/`

Contains the default PDF used by the project.

---

### `.env.example`

Shows the required environment-variable format without containing real credentials.

---

### `.gitignore`

Prevents private or unnecessary files from being uploaded.

Examples:

```text
.env
.venv/
__pycache__/
*.pyc
tool_usage.log
chroma_db/
```

---

## Requirements

The project requires:

* Python
* LangChain
* Google Gemini API
* DuckDuckGo Search
* PyPDF
* Chroma
* Hugging Face sentence-transformer embeddings
* Python Dotenv
* Flask
* Twilio Python SDK
* ngrok

A valid Gemini API key and internet connection are required.

The WhatsApp integration additionally requires:

* A Twilio account
* Access to the Twilio WhatsApp Sandbox
* A WhatsApp number joined to the Sandbox
* An active Flask server
* An active ngrok tunnel

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/osamajahmad/Multi-tool-AI-agent-using-LangChain
```

Open the project folder:

```bash
cd Multi-tool-AI-agent-using-LangChain
```

---

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

The first time the PDF tool runs, the Hugging Face embedding model may need to be downloaded.

---

### 4. Configure environment variables

Create a file named:

```text
.env
```

inside the project folder.

Add:

```env
GOOGLE_API_KEY=your_google_api_key_here

TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=your_twilio_whatsapp_number
```

The WhatsApp number must include the `whatsapp:` prefix.

Example:

```env
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

Use the number displayed in your Twilio Sandbox.

A fixed recipient variable is not required because the application reads the recipient automatically from the incoming message.

Do not upload the real `.env` file to GitHub or include it in the submission ZIP.

---

### 5. Check the default PDF

The default PDF should exist at:

```text
data/AI_and_Future_Jobs_20_Page_Report.pdf
```

---

## Running the Command-Line Interface

Run:

```bash
python app.py
```

The command-line interface displays:

* Available tools
* Available commands
* Example questions

Example:

```text
You: Calculate 15% VAT on 250 AED.
```

---

## Command-Line Commands

### View tool history

```text
history
```

### Select another PDF

```text
pdf
```

### Stop the application

```text
exit
```

or:

```text
quit
```

---

## Running the WhatsApp Interface

### 1. Join the Twilio Sandbox

In the Twilio Console:

1. Open **Messaging**.
2. Open **Try it out**.
3. Select **Send a WhatsApp message**.
4. Open the Sandbox page.
5. Send the displayed join message from your WhatsApp account.

Twilio should reply that your number has joined the Sandbox.

---

### 2. Start the Flask application

Run:

```bash
python whatsapp_app.py
```

The application runs locally at:

```text
http://127.0.0.1:5000
```

The health-check endpoint is:

```text
http://127.0.0.1:5000/
```

Expected response:

```json
{
  "status": "Task 3 WhatsApp agent is running"
}
```

---

### 3. Start ngrok

Open a second terminal:

```bash
ngrok http 5000
```

ngrok provides a public HTTPS URL similar to:

```text
https://example.ngrok-free.app
```

---

### 4. Configure the Twilio webhook

In the Twilio Sandbox settings, set **When a message comes in** to:

```text
https://example.ngrok-free.app/whatsapp
```

Use:

```text
HTTP POST
```

Then save the configuration.

The ngrok URL may change when ngrok restarts. If it changes, the webhook URL in Twilio must also be updated.

---

### 5. Send a WhatsApp message

Keep both processes running:

```bash
python whatsapp_app.py
```

```bash
ngrok http 5000
```

Then send a message to the Twilio Sandbox number.

Example:

```text
What is 125 * 42?
```

The user first receives the acknowledgement message, followed by the final answer.

---

## Suggested Test Cases

### Calculator

```text
What is 125 * 42?
```

Expected result:

```text
5250
```

```text
Calculate 15% VAT on 250 AED.
```

Expected VAT:

```text
37.5 AED
```

Expected total:

```text
287.5 AED
```

```text
Calculate 10 divided by 0.
```

Expected result:

```text
A clear division-by-zero error message
```

---

### Web Search

```text
What is LangChain?
```

```text
What is the latest AI news?
```

```text
What are the recent developments in LLMs?
```

The response should contain a concise summary and source links.

---

### PDF

```text
Summarize this PDF.
```

```text
What are the key points?
```

```text
What does the document say about security?
```

```text
What does the document say about future jobs?
```

The response should be based on the PDF content.

---

### Multi-Tool Request

```text
Search for the latest AI news and calculate 10% growth on a budget of 5000 AED.
```

The agent should use:

1. Web Search Tool
2. Calculator Tool

Expected calculation:

```text
10% of 5000 AED = 500 AED
```

---

### Conversation Memory

First ask:

```text
Calculate 15% of 500.
```

Then ask:

```text
Add that result to the original amount.
```

The agent should use the recent conversation context.

---

## Error Handling

The project handles common errors such as:

* Empty user input
* Invalid mathematical expressions
* Division by zero
* Missing Gemini API key
* Missing Twilio configuration
* Invalid PDF paths
* Missing PDF files
* PDFs with no extractable text
* Web-search failures
* Internet-connection problems
* Agent initialization failures
* Tool execution failures
* Duplicate Twilio webhook deliveries
* Twilio message-sending failures
* Gemini API quota exhaustion
* Unexpected application errors

The application returns clear error messages instead of stopping unexpectedly.

---

## Architecture Overview

```text
                         User
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
     Command-Line Interface        WhatsApp
             app.py                   │
              │                       ▼
              │              Twilio WhatsApp Sandbox
              │                       │
              │                       ▼
              │                ngrok HTTPS Tunnel
              │                       │
              │                       ▼
              │                whatsapp_app.py
              │                Flask Webhook
              │                Background Processing
              │                       │
              └───────────┬───────────┘
                          ▼
              LangChain Tool-Calling Agent
                    agent/agent.py
                          │
                          ▼
                   Gemini 2.5 Flash
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   Calculator Tool  Web Search Tool  PDF Summarizer
                          │               │
                          ▼               ▼
                     DuckDuckGo      PDF RAG Pipeline
```

The full architecture diagram is available at:

```markdown
![Multi-Tool AI Agent Architecture](docs/architecture_diagram.png)
```

---

## Challenges

### Tool Selection

The agent needed clear tool descriptions and instructions to select the correct tool for each request.

### Multi-Tool Requests

Some requests required more than one tool and a combined final response.

### PDF Processing

The PDF tool required text extraction, chunking, embeddings, vector storage, and similarity search.

### Current Information

The Web Search Tool was needed because the language model may not contain the latest information.

### Error Handling

The application needed to continue working when invalid input, API limits, missing files, or tool failures occurred.

### WhatsApp Integration

The existing agent had to be connected to WhatsApp without rewriting the original tools.

### Slow Responses

PDF and multi-tool requests sometimes took longer than Twilio’s webhook should remain open. Background processing was added so the application could acknowledge the request immediately and send the completed answer later.

### API Limits

The Gemini free tier sometimes reached its request limit during repeated testing.

---

## Lessons Learned

During this assignment, I learned how to:

* Create custom LangChain tools
* Connect several tools to one AI agent
* Improve automatic tool routing
* Handle multi-tool requests
* Use Gemini through LangChain
* Build a command-line AI application
* Add conversation memory
* Track tool usage
* Measure tool execution time
* Search the web for current information
* Return source links
* Extract and process PDF text
* Create embeddings
* Use Chroma vector storage
* Build a RAG workflow
* Handle API and tool errors
* Store credentials securely
* Connect a Python application to WhatsApp
* Use the Twilio WhatsApp Sandbox
* Create a Flask webhook
* Expose a local server using ngrok
* Process slower requests in background threads
* Maintain separate memory for different WhatsApp users
* Prevent duplicate webhook processing
* Reuse the same agent through multiple interfaces

---

## Security Notes

The real Gemini API key and Twilio credentials must only be stored in:

```text
.env
```

The following files and folders should not be uploaded:

```text
.env
.venv/
__pycache__/
*.pyc
tool_usage.log
chroma_db/
```

Only `.env.example` should be included in the repository.

Example:

```env
GOOGLE_API_KEY=your_google_api_key_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=your_twilio_whatsapp_number
```

Never expose real credentials in:

* GitHub commits
* Screenshots
* Demo videos
* Public messages
* Submission ZIP files

---

## WhatsApp Integration Limitations

The current integration is intended for development and internship demonstration.

Current limitations include:

* It uses the Twilio WhatsApp Sandbox
* Users must join the Sandbox before messaging
* Flask and ngrok must remain running
* The ngrok URL may change after restarting
* Conversation memory resets when Flask restarts
* Only two background agent requests run simultaneously
* Additional requests wait in a queue
* Only text messages are supported
* WhatsApp PDF attachments are not supported
* Long final answers are shortened to 1,500 characters
* Gemini free-tier limits may delay or reject requests
* Flask’s built-in server is not intended for production deployment

A production version would require:

* A permanent approved WhatsApp sender
* Deployment to an online server
* Persistent conversation storage
* Stronger webhook validation
* Production monitoring
* Scalable background job processing

---

## Demo Video

The demonstration video shows:

* Project structure
* Application startup
* Calculator Tool
* Web Search Tool
* PDF Summarizer Tool
* Multi-tool request
* Conversation memory
* Tool usage history
* Tool execution timing
* Error handling

[Watch the Demo Video](https://youtu.be/nj5EwYUReVg)

---

## Author

**Osama Jameel Ahmad**

AI Intern – Week 3 Assignment
