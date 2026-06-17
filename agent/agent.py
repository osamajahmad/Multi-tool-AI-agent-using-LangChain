import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))


from tools.calculator import calculator_tool
from tools.web_search import web_search_tool
from tools.pdf_summarizer import pdf_summarizer_tool

# Create the multi-tool AI agent.
def create_agent():

    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY was not found in the .env file.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    tools = [
        calculator_tool,
        web_search_tool,
        pdf_summarizer_tool
    ]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a helpful multi-tool AI agent.

You have access to these tools:

1. calculator_tool
Use this for math questions, percentages, VAT, discounts, addition, subtraction, multiplication, and division.

2. web_search_tool
Use this for latest news, current information, recent developments, or anything that needs internet search.

3. pdf_summarizer_tool
Use this for PDF summaries, PDF key points, and questions about the uploaded PDF.

Rules:
- Choose the best tool based on the user's question.
- Use more than one tool when the request requires multiple actions.
- Return only the final answer.
- Do not mention the tool name because the application displays it separately.
- Use plain text suitable for a terminal.
- Do not use Markdown symbols such as **, ##, or backticks.
- For web search answers, provide a concise summary followed by source titles and links.
- Only use source links returned by the web search tool.
- If a tool returns an error, explain it clearly.
- Keep answers clear and concise.
"""
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        handle_parsing_errors=True
    )

    return agent_executor

# Ask the agent a question.
def ask_agent(user_question, chat_history=None):

    if chat_history is None:
        chat_history = []

    agent_executor = create_agent()

    response = agent_executor.invoke(
        {
            "input": user_question,
            "chat_history": chat_history
        }
    )

    return response["output"]


if __name__ == "__main__":
    test_questions = [
        "What is 125 * 42?",
        "Calculate 15% VAT on 250 AED",
        "Summarize this PDF",
        "What is the latest AI news?"
    ]

    for question in test_questions:
        print("Question:", question)
        print("Answer:", ask_agent(question))
        print("-" * 50)