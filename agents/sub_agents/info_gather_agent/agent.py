from google.adk.agents import LlmAgent
import yfinance
import pandas  as pd
from google.adk.tools import AgentTool, BaseTool, ToolContext
import logging 
import google.genai.types as types
from typing import Optional, Dict, Any
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

MODEL = "gemini-2.5-flash"

prompt = """you can gather information about stocks using yfinance api, 
you can reflect upon the result and provide comprehensive details using data. Previous agent output: {result?}"""

def extract_stock_info(ticker: str) -> dict:
    """
    Extract stock information for a given ticker symbol.
    ticker - string ticker symbol for the stock
    """
    stock = yfinance.Ticker(ticker)
    return stock.info

def extract_stock_data(ticker: str, duration_days: int) -> pd.DataFrame:
    """
    Extract stock historical data for a given ticker symbol.
    ticker - string ticker symbol for the stock
    duration_days - integer number of days to look back for historical data
    """
    stock = yfinance.Ticker(ticker)
    return stock.history(period=f"{duration_days}d")

def callback_before_tool_call(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext)-> Optional[types.Content]:
    logging.info("Before tool call hook executed. Tool Agent")
    logging.info(f"Tool: {tool.name}, \nArgs: {args}, \nToolContext: {tool_context.state}")


info_gather_agent = LlmAgent(name = "info_gather_agent",
                 model=MODEL, 
                 description=("analyse provided ticker symbol"),
                 instruction=prompt, 
                 tools=[extract_stock_info],
                 output_key="result",
                 before_tool_callback=callback_before_tool_call)



