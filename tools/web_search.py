from ddgs import DDGS

try:
    from langchain_core.tools import tool
except ImportError:
    def tool(function):
        return function


# Search the web using DuckDuckGo and return a short summary with sources.
def search_web(query):
    try:
        query = query.strip()

        if query == "":
            
            return "Web search error: Please enter a search question."

        ddgs = DDGS() # Creates the DuckDuckGo search object
        results = ddgs.text(query, max_results=3) # Gets the results of the search from the query and the max results allowed and stores it in results
        results = list(results) # Converts results into a list

        # If there is nothing in results then return to the user that no results have been found
        if len(results) == 0:
            return "Web search error: No results found."

        answer = "Summary:\n"

        number = 1

        for result in results:
            # If body exists in result store it in variable body
            if "body" in result:
                body = result["body"]
            else:
                # else store no summary available
                body = "No summary available."

            # Stores the answer for summary in correct format inside answer
            answer = answer + str(number) + ". " + body + "\n"
            # Increments by 1 so you have 1 2 3
            number = number + 1

        answer = answer + "\nSources:\n"

        number = 1

        for result in results:
            # If title exists in result store it in variable title
            if "title" in result:
                title = result["title"]
            else:
                # else store no title available
                title = "No title available."

            # Checks if there is a link in two ways both href and url
            if "href" in result:
                link = result["href"]
            elif "url" in result:
                link = result["url"]
            else:
                link = "No link"

            # Stores the answer for sources in correct format inside answer
            answer = answer + str(number) + ". " + title + " - " + link + "\n"

            number = number + 1

        return answer

    except Exception as error:
        return "Web search error: " + str(error)


    
@tool
def web_search_tool(query: str) -> str:
    """
    Use this tool to search the web for current information,
    recent developments, and latest news.
    """
    return search_web(query)


if __name__ == "__main__":
    test_questions = [
        "Latest AI news",
        "What is LangChain?",
        "Recent developments in LLMs",
    ]

    for question in test_questions:
        print("Question:", question)
        print(search_web(question))
        print("-" * 50)