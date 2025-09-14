import langchain_core
from langgraph import graph, checkpoint
import langchain_google_genai as g
import os
from langchain_core import prompts,stores, chat_history, tools
from langchain_core.messages import HumanMessage, AIMessage
import yfinance

API_KEY = os.environ["GOOGLE_API_KEY"]

private_state = {
    "memory": chat_history.InMemoryChatMessageHistory(),
    "continue": True
}

@tools.tool
def get_stock_info(symbol: str)->dict:
    """
    Get the stock information given a stock symbol including moving averages, price, company info, stock volumes.
    symbol: str -  the stock symbol
    """
    stock = yfinance.Ticker(symbol)
    #private_state["memory"].add_user_message(f"stock info for {symbol} \n {stock.info}")
    return stock.info

@tools.tool
def seek_user_input(ai_question: str):
    """
    Seek user input.
    ai_question: str - question asked by model.
    """
    user_input = input(f"{ai_question}\n> ")
    private_state["memory"].add_user_message(user_input)
    if user_input.lower() == "exit":
        exit()
    return user_input

@tools.tool 
def reason(input: str) -> str:
    """
    Reason about the input.
    """
    return f"Reasoning about {input}"


def router(response:dict)->str:
    """
    Route the response to the appropriate tools and collect responses.
    """
    tool_responses = {}
    if response.tool_calls:
        print("Tool Responses:", len(response.tool_calls))
       
        for tool_call in response.tool_calls:
            if tool_call["type"] != "tool_call":
                continue 

            tool_name = tool_call["name"]
            tool_input = tool_call["args"]
            print(f"Calling tool: {tool_name}")

            if tool_name == "get_stock_info":
                tool_response = get_stock_info(tool_input)
                tool_responses[tool_name] = tool_response

            elif tool_name == "seek_user_input":
                tool_responses[tool_name] = seek_user_input(tool_input)

            elif tool_name == "reason":
                tool_responses[tool_name] = reason(tool_input)
    else:
        return response
 
    return tool_responses

def build_history(messages:list)-> str:
    """
    Build the chat history from the messages.
    """
    history = ""
    print(messages)
    for message in messages:
        if type(message) == HumanMessage:
            history += f"User: {message.content}\n"
        elif type(message) == AIMessage:
            history += f"AI: {message.content}\n"
    return history

if __name__ == "__main__":
    # Example usage of the get_info function
    symbol = "AAPL"
    question = f"What is the stock price of {symbol}?"

    model = g.ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=API_KEY)
    model = model.bind_tools([get_stock_info, seek_user_input, reason])

    human_prompt = prompts.PromptTemplate(input_variables=["question", "history"], template="You are a stock analysis agent that can reason and act. You have access to tools. Users will ask a set of questions. " \
    "Reason and answer. Be precise. {question}. \n History of user messages: {history}")

    tool_prompt = prompts.PromptTemplate(input_variables=["tool_response", "history"], template="You are a stock analysis agent that can reason and act. " \
    "You have access to tools. Users will ask a set of questions. Reason and answer. Be precise. Response from tool calls: {tool_response}.\n History of user messages: {history}")



    human_chain = (human_prompt | model )
    tool_chain = (tool_prompt | model)

    user_input = seek_user_input.invoke(">>")
    
    while user_input.lower() != "exit":
        

   
        history = build_history(private_state["memory"].messages)
        tool_response = router(human_chain.invoke({"question": user_input, "history": history}))
        
        if tool_response:
            while tool_response:
                
                response = tool_chain.invoke({"tool_response": tool_response, "history": history})
                tool_response = None
                if response.tool_calls:
                    print(response.tool_calls)
                    tool_response = response.tool_calls[0]
                
      
        content = response.content
        print("AI:", content)
        private_state["memory"].add_ai_message(content) 
            

        print("No tool responses.")
        user_input = seek_user_input.invoke(">>")


        print("------")
        print(private_state["memory"].messages)
        input("---")