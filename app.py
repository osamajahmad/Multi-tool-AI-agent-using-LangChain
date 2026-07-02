import logging
import time

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, AIMessage

from agent.agent import create_agent

from tools.pdf_summarizer import (
    select_pdf,
    get_selected_pdf_name
)

# Save tool usage information in a log file
logging.basicConfig(
    filename="tool_usage.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# Extract only the readable text from the agent response.
def extract_answer_text(content):

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        answer_text = ""

        for block in content:
            if isinstance(block, dict):
                if "text" in block:
                    answer_text = answer_text + block["text"]

            elif isinstance(block, str):
                answer_text = answer_text + block

        return answer_text.strip()

    return str(content)

# Track which tools the agent uses and how long each tool takes.
class ToolTracker(BaseCallbackHandler):

    def __init__(self):
        self.start_times = {} # Stores the start time for each running tool
        self.tool_records = [] # Stores final records for tools that were used

    # This method runs automatically when a tool starts
    def on_tool_start(
        self,
        serialized,
        input_str,
        *,
        run_id,
        **kwargs
    ):
        # Run automatically when a tool starts.
        if serialized and "name" in serialized:
            tool_name = serialized["name"]
        else:
            tool_name = "Unknown tool"

        # Save the tool name and the current start time. Later, when the tool finishes, we use this to calculate duration
        self.start_times[run_id] = {
            "name": tool_name,
            "start_time": time.time()
        }

    # This method runs automatically when a tool ends
    def on_tool_end(
        self,
        output,
        *,
        run_id,
        **kwargs
    ):
        # Run automatically when a tool finishes successfully.
        if run_id not in self.start_times:
            return

        tool_information = self.start_times.pop(run_id)

        tool_name = tool_information["name"]
        start_time = tool_information["start_time"]

        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        # Save the tool usage record as successful
        self.tool_records.append(
            {
                "name": tool_name,
                "duration": duration,
                "status": "Success"
            }
        )

    # This method runs automatically when a tool fails
    def on_tool_error(
        self,
        error,
        *,
        run_id,
        **kwargs
    ):
        # Run automatically when a tool fails.
        if run_id not in self.start_times:
            return

        tool_information = self.start_times.pop(run_id)

        tool_name = tool_information["name"]
        start_time = tool_information["start_time"]

        end_time = time.time()
        duration = round(end_time - start_time, 2)

        self.tool_records.append(
            {
                "name": tool_name,
                "duration": duration,
                "status": "Failed"
            }
        )

# Keep only the latest five conversation messages.
def keep_last_five_messages(chat_history):

    if len(chat_history) > 5:
        chat_history = chat_history[-5:]

    return chat_history

# Display the tool usage history for the current session.
def show_tool_history(tool_usage_history):

    if len(tool_usage_history) == 0:
        print("\nNo tools have been used yet.")
        return

    print("\n" + "=" * 60)
    print("Tool Usage History")
    print("=" * 60)

    number = 1

    for history_item in tool_usage_history:
        print("\nRequest " + str(number))
        print("Question: " + history_item["question"])

        tools = history_item["tools"]

        if len(tools) == 0:
            print("Tools used: No tool was used.")
        else:
            for tool in tools:
                print("Tool: " + tool["name"])
                print("Status: " + tool["status"])
                print(
                    "Execution time: "
                    + str(tool["duration"])
                    + " seconds"
                )

        number = number + 1

    print("\n" + "=" * 60)

# Display the application instructions.
def show_intro():

    print("=" * 60)
    print("Multi-Tool AI Agent")
    print("=" * 60)

    print("Available tools:")
    print("1. Calculator Tool")
    print("2. Web Search Tool")
    print("3. PDF Summarizer Tool")

    print("\nCommands:")
    print("- Type 'pdf' to select a PDF file.")
    print("- Type 'history' to view tool usage history.")
    print("- Type 'exit' or 'quit' to stop the application.")

    print("\nCurrent PDF:")
    print(get_selected_pdf_name())

    print("\nExample questions:")
    print("- Calculate 15% VAT on 250 AED")
    print("- What is the latest AI news?")
    print("- Summarize this PDF")
    print(
        "- Search for the latest AI news and "
        "calculate 10% growth on 5000 AED"
    )

    print("=" * 60)

# Start the command-line chatbot.
def main():

    # Show the welcome screen and instructions
    show_intro()

    try:
        agent_executor = create_agent()

    except Exception as error:
        print("Error while starting the agent: " + str(error))
        return

    # Bonus 1: Conversation memory
    chat_history = []

    # Bonus 2: Tool usage history
    tool_usage_history = []

    # Keep the chatbot running until the user types quit or exit
    while True:
        user_input = input("\nYou: ")

        user_input = user_input.strip()

        if user_input.lower() == "quit" or user_input.lower() == "exit":
            print("\nGoodbye!")
            break

        if user_input.lower() == "pdf":

            pdf_path = input(
            "Enter the full path of the PDF file: "
        )
    
            result = select_pdf(pdf_path)

            print("\n" + result)
            continue

        if user_input.lower() == "history":
            show_tool_history(tool_usage_history)
            continue

        # Bonus 3: Tool execution timing
        tracker = ToolTracker()

        try:
            response = agent_executor.invoke(
                {
                    "input": user_input,
                    "chat_history": chat_history
                },
                config={
                    "callbacks": [tracker] # The tracker callback records tool usage automatically
                }
            )

            raw_answer = response["output"] # Get the raw response from the agent
            answer = extract_answer_text(raw_answer) # Convert the answer into clean readable text

            print("\nAssistant:")
            print(answer)

            print("\nTool execution details:")

            if len(tracker.tool_records) == 0:
                print("No tool was used.")

            else:
                for tool in tracker.tool_records:
                    print("Tool: " + tool["name"])
                    print("Status: " + tool["status"])
                    print(
                        "Execution time: "
                        + str(tool["duration"])
                        + " seconds"
                    )

            # Save conversation memory
            chat_history.append(
                HumanMessage(content=user_input)
            )

            chat_history.append(
                AIMessage(content=answer)
            )

            chat_history = keep_last_five_messages(
                chat_history
            )

            # Save tool usage history
            tool_usage_history.append(
                {
                    "question": user_input,
                    "tools": tracker.tool_records.copy()
                }
            )

            # Save tool usage to the log file
            logging.info("Question: " + user_input)

            if len(tracker.tool_records) == 0:
                logging.info("No tool was used.")

            else:
                for tool in tracker.tool_records:
                    logging.info(
                        "Tool: "
                        + tool["name"]
                        + " | Status: "
                        + tool["status"]
                        + " | Execution time: "
                        + str(tool["duration"])
                        + " seconds"
                    )

            logging.info("-" * 50)

        except Exception as error:
            print("\nApplication error: " + str(error))

            logging.error(
                "Question: "
                + user_input
                + " | Error: "
                + str(error)
            )


if __name__ == "__main__":
    main()