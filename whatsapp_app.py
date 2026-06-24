import logging # Used to save information
import os # Used keep sensitive info in the env
from collections import defaultdict # Creates a default value when missing key
from concurrent.futures import ThreadPoolExecutor 
from threading import Lock # Locks threads from working on the same data

# External Library
from dotenv import load_dotenv # Read values from .env
from flask import Flask, request # Flask recieves the twilio requests and request contains info about the HTTP request
from langchain_core.messages import AIMessage, HumanMessage # Differntiates between the AI and human messages
from twilio.rest import Client # The final respond
from twilio.twiml.messaging_response import MessagingResponse #The imidiate responed through the XML 

# Imports from Task 3
from agent.agent import create_agent # Import the function that creates the LangChain agent
from app import (
    ToolTracker,
    extract_answer_text,
    keep_last_five_messages,
)

load_dotenv()

# Create the Flask application
server = Flask(__name__)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

required_environment_variables = {
    "TWILIO_ACCOUNT_SID": TWILIO_ACCOUNT_SID,
    "TWILIO_AUTH_TOKEN": TWILIO_AUTH_TOKEN,
    "TWILIO_WHATSAPP_NUMBER": TWILIO_WHATSAPP_NUMBER,
}

missing_environment_variables = [
    variable_name
    for variable_name, variable_value
    in required_environment_variables.items()
    if not variable_value
]

# Tells the developer that the Flask application won't start unless the required enviroment variables are available in .env
if missing_environment_variables:
    raise ValueError(
        "Missing environment variables: "
        + ", ".join(missing_environment_variables)
    )

# Creating an authenticated Twilio client
twilio_client = Client(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
)

# Conversation and background-processing storage

# Each WhatsApp number receives its own conversation history
chat_histories = defaultdict(list)

# Prevent two messages from the same user changing memory simultaneously
chat_locks = defaultdict(Lock)

# Only two users will have there question processed at the same time
background_pool = ThreadPoolExecutor(max_workers=2)

# Prevent Twilio webhook retries from running the same message more than once
processed_message_sids = set()
processed_message_lock = Lock()

# Sends the whatsapp message with answer to the recipient
def send_whatsapp_message(recipient, answer):
    """
    Send the completed agent answer as one WhatsApp message.
    """

    # Convers the answer to string type and remove spaces
    message_text = str(answer).strip()

    # If the answer is empty then return this string 
    if not message_text:
        message_text = "Sorry, the agent did not return an answer."

    # Keep the answer below Twilio's message character limit
    if len(message_text) > 1500:
        message_text = (
            message_text[:1497].rstrip()
            + "..."
        )

    # Create and send a new message
    twilio_client.messages.create(
        body=message_text,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=recipient,
    )

# Runs the Task 3 agent in background thread pool
def process_agent_request(sender, incoming_message):
    """
    Run the Task 3 agent in the background and send its final
    answer through the Twilio REST API.
    """

    tracker = ToolTracker()

    try:
        # Create the LangChain agent for this request
        agent_executor = create_agent()

        # Process messages from the same user in order
        with chat_locks[sender]:
            chat_history = chat_histories[sender]

            result = agent_executor.invoke(
                {
                    "input": incoming_message,
                    "chat_history": chat_history,
                },
                config={
                    # Record and watch what happens if tools are used
                    "callbacks": [tracker]
                },
            )

            raw_answer = result["output"]
            answer = extract_answer_text(raw_answer)

            # If empty return this string
            if not answer.strip():
                answer = (
                    "Sorry, the agent did not return an answer."
                )

            # Update this WhatsApp user's conversation memory
            chat_history.append(
                HumanMessage(content=incoming_message)
            )
            
            # Update memory with the AI response
            chat_history.append(
                AIMessage(content=answer)
            )

            chat_histories[sender] = keep_last_five_messages(
                chat_history
            )

        print("\n" + "=" * 60) # Adds a line like this (=========) to make it easier to read
        print("Background request completed") 
        print("Sender:", sender)
        print("Question:", incoming_message)
        print("Answer:", answer)

        # Checking if a tool was used
        if not tracker.tool_records:
            print("Tool used: No tool was used.")

        # If a tool was used add its information
        for tool_record in tracker.tool_records:
            print("Tool:", tool_record["name"])
            print("Status:", tool_record["status"])
            print(
                "Execution time:",
                tool_record["duration"],
                "seconds",
            )
            
            # Records the tool information using Python logging
            logging.info(
                "WhatsApp sender: %s | Tool: %s | "
                "Status: %s | Execution time: %s seconds",
                sender,
                tool_record["name"],
                tool_record["status"],
                tool_record["duration"],
            )

        # Sends the final result
        send_whatsapp_message(
            recipient=sender,
            answer=answer,
        )

        print("WhatsApp answer sent successfully.")

    except Exception as error:
        print("Background agent error:", str(error))

        logging.exception(
            "WhatsApp agent error for sender %s",
            sender,
        )

        try:
            send_whatsapp_message(
                recipient=sender,
                answer=(
                    "Sorry, the Task 3 agent could not process "
                    "your request. Please try again."
                ),
            )

        except Exception as sending_error:
            print(
                "Could not send the error message:",
                str(sending_error),
            )

            # Logs the information separately for review
            logging.exception(
                "Twilio sending error for sender %s",
                sender,
            )


# Flask routes
@server.route("/", methods=["GET"])
def health_check():
    return {
        "status": "Task 3 WhatsApp agent is running"
    }, 200


# Twilio sends incoming WhatsApp message details to this Flask webhook as form data using an HTTP POST request
@server.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_message = request.form.get(
        "Body",
        "",
    ).strip()

    sender = request.form.get(
        "From",
        "",
    ).strip()

    message_sid = request.form.get(
        "MessageSid",
        "",
    ).strip()

    twilio_response = MessagingResponse()

    # Some Error Handeling
    if not incoming_message:
        twilio_response.message(
            "Please send a text question."
        )

        return (
            str(twilio_response),
            200,
            {"Content-Type": "application/xml"},
        )

    if not sender:
        return (
            "Missing sender",
            400,
        )

    # Ignore duplicate webhook deliveries.
    if message_sid:
        with processed_message_lock:
            if message_sid in processed_message_sids:
                return (
                    str(twilio_response),
                    200,
                    {"Content-Type": "application/xml"},
                )

            processed_message_sids.add(message_sid)

    print("\nWhatsApp message received")
    print("Sender:", sender)
    print("Question:", incoming_message)

    # Start the agent without making Twilio wait
    background_pool.submit(
        process_agent_request,
        sender,
        incoming_message,
    )

    # Return immediately to Twilio
    twilio_response.message(
        "Your request is being processed. "
        "I will send the answer shortly."
    )

    return (
        str(twilio_response),
        200,
        {"Content-Type": "application/xml"},
    )


if __name__ == "__main__":
    server.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )