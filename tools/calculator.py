import re

try:
    from langchain_core.tools import tool
except ImportError:
    def tool(function):
        return function

# Show 37.0 as 37, but keep 37.5 as 37.5.
def clean_number(number):

    if float(number).is_integer():
        return str(int(number))

    return str(round(number, 4))

# Detect simple currency words from the user question.
def detect_currency(user_text):

    text = user_text.lower()

    if "aed" in text:
        return " AED"

    if "usd" in text or "$" in text:
        return " USD"

    if "eur" in text or "€" in text:
        return " EUR"

    return ""

# Handle percentage questions like:
# Calculate 15% VAT on 250 AED
# Calculate 15% discount on 759
# What is 20% of 500?
def calculate_percentage(user_text):

    text = user_text.lower()
    currency = detect_currency(user_text)

    percent_match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)

    if not percent_match:
        return None

    percent = float(percent_match.group(1))

    numbers = re.findall(r"\d+(?:\.\d+)?", text)

    if len(numbers) < 2:
        return "I found a percentage, but I could not find the main amount."

    amount = None

    for number in numbers:
        if float(number) != percent:
            amount = float(number)
            break

    if amount is None:
        return "I could not find the amount."

    percentage_value = amount * percent / 100

    if "vat" in text or "tax" in text:
        total = amount + percentage_value

        return (
            f"{clean_number(percent)}% of {clean_number(amount)}{currency} is "
            f"{clean_number(percentage_value)}{currency}. "
            f"Total with VAT is {clean_number(total)}{currency}."
        )

    if "discount" in text:
        final_price = amount - percentage_value

        return (
            f"{clean_number(percent)}% of {clean_number(amount)}{currency} is "
            f"{clean_number(percentage_value)}{currency}. "
            f"Final price after discount is {clean_number(final_price)}{currency}."
        )

    return (
        f"{clean_number(percent)}% of {clean_number(amount)}{currency} is "
        f"{clean_number(percentage_value)}{currency}."
    )

# Convert user text into a simple math expression.
def prepare_expression(user_text):

    expression = user_text.lower()

    expression = expression.replace("what is", "")
    expression = expression.replace("calculate", "")
    expression = expression.replace("monthly payment for", "")
    expression = expression.replace("divided by", "/")
    expression = expression.replace("divide by", "/")
    expression = expression.replace("multiply by", "*")
    expression = expression.replace("multiplied by", "*")
    expression = expression.replace("times", "*")
    expression = expression.replace("plus", "+")
    expression = expression.replace("minus", "-")
    expression = expression.replace("x", "*")
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("?", "")

    # Keep only numbers and math symbols
    expression = re.sub(r"[^0-9+\-*/(). ]", "", expression)

    return expression.strip()

# Main calculator function.
def calculate(user_question):

    try:
        percentage_answer = calculate_percentage(user_question)

        if percentage_answer:
            return percentage_answer

        expression = prepare_expression(user_question)

        if expression == "":
            return "I could not find a math expression to calculate."

        result = eval(expression)

        return f"The answer is {clean_number(result)}."

    except ZeroDivisionError:
        return "Calculator error: Cannot divide by zero."

    except Exception:
        return "Calculator error: Sorry, I could not calculate that."

@tool
def calculator_tool(user_question: str) -> str:
    """
    Use this tool for addition, subtraction, multiplication, division,
    percentages, VAT, discounts, and simple mathematical expressions.
    """
    return calculate(user_question)


if __name__ == "__main__":
    test_questions = [
        "Calculate 15% VAT on 250 AED",
        "What is 125 * 42?",
        "Calculate monthly payment for 5000 divided by 12",
        "What is 20% of 500?",
        "Calculate 15% discount on 759",
        "What is 10 + 5 * 2?",
        "What is 10 divided by 0?",
    ]

    for question in test_questions:
        print("Question:", question)
        print("Answer:", calculate(question))
        print("-" * 50)