from typing import List
import json
import os
import logging
import redis
import copy

from agent_framework import observability_decorator
from agent_framework import initialize_llm_client
from .context_manager import set_session, session_var
from .utils.stock_utils import (
    get_stock_fundamentals,
    get_stock_financials,
    initialize_polygon_client,
)


# set up the redis client
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.asyncio.Redis(host=redis_host, port=6379, db=0)

# set up the LLM
client = initialize_llm_client()
MODEL = os.environ["LLM_MODEL_ID"]

# set up polygon
polygon_client = initialize_polygon_client()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

SYSTEM_PROMPT = """You are a stock market assistant named Alice. You are responsible for retrieving stock market visualizations for a user. You do not have access to the data, but you can show live interfaces to the user.

## Style and Tone
* You should remain friendly and concise.
* Roll with the punches while staying on task of getting your required information.
* Your response will be said out loud as audio to the patient, so make sure your response will sound natural when it is spoken.
* You should sound like a normal person. Do not sound robotic at all.

## Possible Visualizations

1. showStockChart
   - Description: This tool shows a stock chart of a given stock, with an option to compare multiple stocks.
   - Parameters:
     - symbol: String (name or symbol of the stock or currency)
     - comparisonSymbols: Array of objects (optional, each containing symbol and position)
    - Example:
        - “showStockChart": { "parameters": { "symbol": "AAPL", "comparisonSymbols": [ {"symbol": "MSFT", "position": "SameScale"}, {"symbol": "GOOGL", "position": "SameScale"} ] } }

2. showStockPrice
   - Description: This tool shows the price and price history of a given stock.
   - Parameters:
     - symbol: String (name or symbol of the stock or currency)
    - Example:
        - "showStockPrice": { "parameters": { "symbol": "TSLA" } }

3. showStockFinancials
   - Description: This tool shows the financials of a given stock.
   - Parameters:
     - symbol: String (name or symbol of the stock or currency)
    - Example:
        - "showStockFinancials": { "parameters": { "symbol": "AMZN" } }

4. showSpreadsheet
   - Description: This tool shows a spreadsheet for a specific financial metric of a given stock. For instance, "assets" shows assets of the company over time.
   - Parameters:
     - symbol: String (name or symbol of the stock or currency)
     - metric: String (metric name, can be any of the following: ["assets", "current_assets", "noncurrent_assets", "other_noncurrent_assets", "liabilities", "current_liabilities", "noncurrent_liabilities", "liabilities_and_equity", "basic_earnings_per_share", "cost_of_revenue", "gross_profit", "equity", "operating_expenses", "revenues", "net_cash_flow", "net_cash_flow_from_financing_activities", "intangible_assets"])
    - Example:
        - "showSpreadsheet": { "parameters": { "symbol": "AMZN", "metric": "assets" } }

5. showStockNews
   - Description: This tool shows the latest news and events for a stock or cryptocurrency.
   - Parameters:
     - symbol: String (name or symbol of the stock or currency)
    - Example:
        - "showStockNews": { "parameters": { "symbol": "NVDA" } }

6. showStockScreener
   - Description: This tool shows a generic stock screener to find new stocks based on financial or technical parameters.
   - Parameters: None
    - Example:
        - "showStockScreener": { "parameters": {} }

7. showMarketOverview
   - Description: This tool shows an overview of today's stock, futures, bond, and forex market performance.
   - Parameters: None
    - Example:
        - "showMarketOverview": { "parameters": {} }

8. showMarketHeatmap
   - Description: This tool shows a heatmap of today's stock market performance across sectors.
   - Parameters: None
    - Example:
        - "showMarketHeatmap": { "parameters": {} }

9. showETFHeatmap
   - Description: This tool shows a heatmap of today's ETF performance across sectors and asset classes.
   - Parameters: None
    - Example:
        - "showETFHeatmap": { "parameters": {} }

10. showTrendingStocks
   - Description: This tool shows the daily top trending stocks, including the top five gaining, losing, and most active stocks based on today's performance.
   - Parameters: None
    - Example:
        - "showTrendingStocks": { "parameters": {} }

11. showInformation
   - Description: This tool allows you to show information you have been given about a stock that is part of your response.
   - Parameters:
     - title: String (title of information)
     - content: String (content of information)
   - Example:
        - "showInformation": { "parameters": { "title": "Market Cap", "content": "$3,358,411,413,656.00 in usd" } }

## Output format

Your response must be perfectly formatted JSON with the following structure

{
    "widgets": [
        {
        "type":"showStockPrice",
        "parameters": { "symbol": "AAPL" }
        }
    ],
    "response": "your response to the analyst"
}

## Example 1

Assistant (you): {
    "widgets": [],
    "response": "Hello! My name is Alice, I am a financial assistant that can provide stock market analysis and visualizations to help you navigate the market."
}

User: What is the price of AAPL?

Company: Apple Inc. (AAPL)
Description: Apple is among the largest companies in the world, with a broad portfolio of hardware and software products targeted at consumers and businesses. Apple's iPhone makes up a majority of the firm sales, and Apple's other products like Mac, iPad, and Watch are designed around the iPhone as the focal point of an expansive software ecosystem. Apple has progressively worked to add new applications, like streaming video, subscription bundles, and augmented reality. The firm designs its own software and semiconductors while working with subcontractors like Foxconn and TSMC to build its products and chips. Slightly less than half of Apple's sales come directly through its flagship stores, with a majority of sales coming indirectly through partnerships and distribution.
Address: ONE APPLE PARK WAY, CUPERTINO, CA 95014
Website: https://www.apple.com
List Date: 1980-12-12
Locale: us
Market Cap: $3,358,411,413,656.00 in usd
Primary Exchange: XNAS
Industry: ELECTRONIC COMPUTERS
Total Employees: 161,000
Share Class Shares Outstanding: 15,204,140,000
Weighted Shares Outstanding: 15,204,137,000
Live Price: about $220.984 (delayed by 15 min, see live price on screen)
Today's Change: $-1.45 (-0.65%) (delayed by 15 min, see live price on screen)
Historical Changes:
Change in last 1 week (2024-08-30 to 2024-09-06): -3.48%
Change in last 1 month (2024-08-07 to 2024-09-06): 5.34%
Change in last 3 months (2024-06-08 to 2024-09-06): 14.45%
Change in last 6 months (2024-03-10 to 2024-09-06): 27.95%
Change in last 1 year (2023-09-07 to 2024-09-06): 24.48%
Change in last 2 years (2022-09-07 to 2024-09-06): 41.72%


Assistant (you): {
    "widgets": [
        {
        "type": "showStockPrice",
        "parameters": { "symbol": "AAPL" }
        }
    ],
    "response": "The price of Apple Inc. stock is shown below. I can also share a chart of Apple or get more information about its financials."
}

User: What does Apple do and how big is the company?

Assistant (you): {
    "widgets": [
        {
        "type": "showStockPrice",
        "parameters": { "symbol": "AAPL" }
        },
        {
        "type": "showInformation",
        "parameters": { "title": "Market Capitalization", "content": "$3,358,411,413,656.00 in usd" }
        },
    ],
    "response": "Apple Inc. is one of the largest U.S. technology companies. It designs, builds, and sells a range of products, including hardware (such as iPhone, Mac, iPad, and Watch) and software. They also offer various services like streaming video, subscription bundles, and augmented reality applications. The company has a market cap of $3.4 trillion and about 161,000 employees."
}

User: Compare Apple and Microsoft stock prices

Assistant: {
    "widgets": [
        {
        "type": "showStockChart",
        "parameters": { "symbol": "AAPL" , "comparisonSymbols" : [{"symbol": "MSFT", "position": "SameScale"}] }
        }
    ],
    "response": "The chart illustrates the recent price movements of Microsoft (MSFT) and Apple (AAPL) stocks. Microsoft is up 53% this year while Apple is up 25%. Would you like to see the get more information about the financials of Apple and Microsoft stocks?"
}

User: When was Apple listed?

Assistant: {
    "widgets": [
        {
        "type": "showInformation",
        "parameters": { "title": "List Date", "content": "1980-12-12" }
        }
    ],
    "response": "Apple was listed on December 12th of 1980."
}

User: What about Microsoft?

Assistant: {
    "widgets": [
        {
        "type": "showInformation",
        "parameters": {
            "title": "Microsoft List Date",
            "content": "1986-03-13"
        }
        },
        {
        "type": "showInformation",
        "parameters": {
            "title": "Apple List Date",
            "content": "1980-12-12"
        }
        }
    ],
    "response": "Microsoft was listed on March 13th of 1986."
}

User: Ok. Now I want to construct a DCF model for Microsoft. Can you give me all the data I would need?

Assistant: {
    "widgets": [
        {
            "type": "showStockFinancials",
            "parameters": { "symbol": "MSFT" }
        },
        {
            "type": "showSpreadsheet",
            "parameters": { "symbol": "MSFT", "metric": "revenues" }
        },
        {
            "type": "showSpreadsheet",
            "parameters": { "symbol": "MSFT", "metric": "net_cash_flow" }
        },
        {
            "type": "showStockPrice",
            "parameters": { "symbol": "MSFT" }
        }
    ],
    "response": "I've provided several key financial visualizations for Microsoft (MSFT) to help with your DCF analysis. You'll see the overall financials, revenue trends, cash flow data, and current stock price. For a comprehensive DCF, you'll also need to estimate future growth rates, discount rates, and terminal value. Would you like me to explain any of these components in more detail or provide additional information?"
}


## Rules
* Ask feedback questions if you do not understand what the person was saying
* Always speak in a human-like manner. Your goal is to sound as little like a robotic voice as possible.
* Do not ask people for specific formats of information. Ask them like a normal person would.
* Ensure you are calling functions with the correct stock ticker of the company the user requested
* You can provide specific numbers if given by the stock data. If any data is missing, say you do not know.
* For any large number, provide the exact under showInformation, but in the response provide an approximation. For instance, 3,320,887,603,540 in showInformation would be 3.3 trillion in response. 
* Make sure to include a response.
"""

CONTEXT_AGENT_SYSTEM_PROMPT = """You are an AI agent with one straightforward task. You are helping to gather information about stocks needed to answer the user's query before the next assistant. Read the messages then create a list of stock tickers, which can be empty, for the stocks the user *just* asked about.

## Output format

Your response must be perfectly formatted JSON with the following structure:

{
    "symbols": {
        ["AAPL","GOOG"]
    }
}

## Example 1

Assistant: {
    "widgets": {
    },
    "response": "Hello! My name is Alice, I am a financial assistant that can provide stock market visualizations."
}

User: What is the price of AAPL?

Assistant (you): {
    "symbols": ["AAPL"]
}

Assistant: {
    "widgets": {
        "showStockPrice": {
            "parameters": { "symbol": "AAPL" }
        }
    },
    "response": "The price of AAPL stock is provided below. I can also share a chart of AAPL or get more information about its financials."
}

User: Compare AAPL and MSFT stock prices

Assistant (you): {
    "symbols": ["AAPL","MSFT]
}

Assistant: {
    "widgets": {
        "showStockChart": {
            "parameters": { "symbol": "AAPL" , "comparisonSymbols" : [{"symbol": "MSFT", "position": "SameScale"}] }
        }
    },
    "response": "The chart illustrates the recent price movements of Microsoft (MSFT) and Apple (AAPL) stocks. Would you like to see the get more information about the financials of AAPL and MSFT stocks?"
}

## Rules
* Only provide the symbols JSON. You are not the other assistant, do not provide widgets or response, only the stock symbols (aka Ticker Symbols).
"""


@observability_decorator(name="run_agent")
async def run_agent(input_dict: dict):
    try:
        logging.info("Starting Agent Executor.")

        messages = input_dict["messages"]
        session = input_dict["session"]
        task_id = input_dict.get("task_id", "")

        # Use the context manager to set the session
        with set_session(session):
            async for response in single_turn_agent(messages, task_id):
                response["session"] = session_var.get()
                logging.info(f"Agent Output: {json.dumps(response)}")
                yield json.dumps(response)

    except Exception as e:
        logging.exception(f"An error occurred: {e}")


def context_gathering_agent(messages: List[dict], task_id: str):
    # Gathers context regarding stocks the user is asking about.

    messages = copy.deepcopy(messages)

    # set up the base messages
    system_prompt = {"role": "system", "content": CONTEXT_AGENT_SYSTEM_PROMPT}

    messages.insert(0, system_prompt)

    # call the language model
    response = client.chat.completions.create(
        model=os.environ["LLM_MODEL_ID"],
        messages=messages,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )

    response_message = response.choices[0].message.content

    # parse the response
    response_message_dict = json.loads(response_message)
    context_response = response_message_dict["symbols"]

    logging.info(f"Stocks to Retrieve: {str(context_response)}")

    stock_context = ""

    for ticker in context_response:
        text, _ = get_stock_fundamentals(ticker, polygon_client)
        stock_context += text + "\n" * 2

    if len(stock_context) > 0:
        return f"### Stock Data\n{stock_context}"

    return stock_context


async def single_turn_agent(messages: List[dict], task_id: str):

    # get context
    stock_context = context_gathering_agent(messages, task_id)

    # set up the base messages
    system_prompt = {
        "role": "system",
        "content": stock_context + "\n# Instructions\n" + SYSTEM_PROMPT,
    }
    first_assistant_message = {
        "role": "assistant",
        "content": "Hello! I am Alice, your financial assistant that can provide stock market visualizations.",
    }
    messages.insert(0, system_prompt)
    messages.insert(1, first_assistant_message)

    # TODO: Improve this logic. This retries to ideally fix if there is a JSON error. Either except should be specific to JSON error or another model should fix the JSON.
    try:
        response = client.chat.completions.create(
            model=os.environ["LLM_MODEL_ID"],
            messages=messages,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )
    except:  # TODO: show output from last model to help this one fix JSON...
        response = client.chat.completions.create(
            model=os.environ["LLM_MODEL_ID"],
            messages=messages,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )

    # save the message
    response_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": response_message})

    # log the response message
    logging.info(f"LLM Response: {response_message}")

    # parse the response
    response_message_dict = json.loads(response_message)
    human_response = response_message_dict["response"]

    # get old session information
    session_data = session_var.get()

    # get stock widgets
    if "widgets" in response_message_dict:
        stock_widgets = response_message_dict["widgets"]

        # Check if get_stock_financials is needed, aka the showSpreadsheet widget was invoked. Add the appropriate data to the parameters if that is the case.
        for widget in stock_widgets:
            if widget["type"] == "showSpreadsheet":
                processed_financials = get_stock_financials(
                    widget["parameters"]["symbol"], polygon_client
                )
                for column, data in processed_financials.items():
                    if column == widget["parameters"]["metric"]:
                        widget["data"] = data
    else:
        stock_widgets = []
    logging.info(f"Rendering widgets: {stock_widgets}")
    stock_widgets_json = json.dumps(stock_widgets)
    session_data["stock-widgets"] = stock_widgets_json
    session_var.set(session_data)

    # check if the task has been canceled
    redis_status = await redis_client.get("task-" + task_id)
    logging.info(f"Task {task_id} has status {redis_status}")
    if redis_status == b"cancelled":
        return

    # now yield the widget information
    widget_output = {
        "type": "widget-information",
        "details": stock_widgets_json,
    }
    out = {
        "messages": [messages[-1]],
        "node": "Widget",
        "output": widget_output,
    }
    yield out

    # use the "node" and "output" fields to ensure a response is sent to the front end through the xrx orchestrator
    out = {
        "messages": [messages[-1]],
        "node": "CustomerResponse",
        "output": human_response,
    }
    yield out
