from google.adk.agents import LlmAgent
from google.adk.models import LlmRequest, LlmResponse
import yfinance
import pandas  as pd
from google.adk.tools import AgentTool, BaseTool, ToolContext
from google.adk.agents.callback_context import CallbackContext
import logging 
import google.genai.types as types
from typing import Optional, Dict, Any
import memory


NAME = "info_gather_agent"

log_fh = logging.FileHandler(f"{NAME}.log")
info_gather_logger = logging.getLogger(__name__)
info_gather_logger.addHandler(log_fh)
info_gather_logger.setLevel(logging.INFO)

MODEL = "gemini-2.5-flash"

prompt = """you can gather information about stocks using yfinance api, 
you can reflect upon the result and provide comprehensive details using data. Previous agent output: {history?}"""

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
    info_gather_logger.info("-- Before tool call hook executed.")
    info_gather_logger.info(f"Tool: {tool.name}, \nArgs: {args}, \nToolContext: {tool_context.state}")
    memory.record_session(app_name=tool_context.state.get("app_name","default_app",),
                          user_id=tool_context.state.get("user_id","default_user"),
                          session_id=tool_context.state.get("session_id","default_session"),
                          state=tool_context.state.get("history",""),
                          source=f"{NAME}_before_tool_call")
   

def callback_after_tool_call(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict)-> Optional[types.Content]:
    info_gather_logger.info("-- After tool call hook executed.")
    info_gather_logger.info(f"Tool: {tool.name}, \nArgs: {args}, \nToolContext: {tool_context.state}, \nOutput: {tool_response}")
    memory.record_session(app_name=tool_context.state.get("app_name","default_app",),
                          user_id=tool_context.state.get("user_id","default_user"),
                          session_id=tool_context.state.get("session_id","default_session"),
                          state=tool_context.state.get("history",""),
                          source=f"{NAME}_after_tool_call")


def callback_before_agent_call(callback_context: CallbackContext)-> Optional[types.Content]:
    info_gather_logger.info("-- Before agent call hook executed.")
    info_gather_logger.info(f"CallbackContext: {callback_context.state.to_dict()}")
    calling_agent = callback_context.state.get("caller_agent", "")
    info_gather_logger.info(f"Calling Agent: {calling_agent}")

    if calling_agent == "":

        memory.record_session(app_name=callback_context.state.get("app_name","default_app",),
                          user_id=callback_context.state.get("user_id","default_user"),
                          session_id=callback_context.state.get("session_id","default_session"),
                          state=callback_context.state.get("history",""),
                          source=f"{NAME}_before_agent_call",
                          interaction_start=True,
                          user_content=callback_context.user_content.parts[0].text if callback_context.user_content and callback_context.user_content.parts else "")
    else:
        memory.record_session(app_name=callback_context.state.get("app_name","default_app",),
                          user_id=callback_context.state.get("user_id","default_user"),
                          session_id=callback_context.state.get("session_id","default_session"),
                          state=callback_context.state.get("history",""),
                          source=f"{NAME}_before_agent_call",
                          interaction_start=True,
                          calling_agent=calling_agent,
                          agent_content=callback_context.user_content.parts[0].text if callback_context.user_content and callback_context.user_content.parts else "")

    


def callback_after_agent_call(callback_context: CallbackContext)-> Optional[types.Content]:
    info_gather_logger.info("-- After agent call hook executed.")
    info_gather_logger.info(f"CallbackContext: {callback_context.state.to_dict()}")
    memory.record_session(app_name=callback_context.state.get("app_name","default_app",),
                          user_id=callback_context.state.get("user_id","default_user"),
                          session_id=callback_context.state.get("session_id","default_session"),
                          state=callback_context.state.get("history",""),
                          source=f"{NAME}_after_agent_call",
                          interaction_end=True,
                          agent_response=callback_context.state.get("result",""))


def callback_before_model_call(callback_context: CallbackContext, llm_request: LlmRequest)-> Optional[types.Content]:
    info_gather_logger.info("-- Before model call hook executed.")
    info_gather_logger.info(f"CallbackContext: {callback_context.state.to_dict()}, \nLLM_Request: {llm_request}")

    memory.record_session(app_name=callback_context.state.get("app_name","default_app",),
                          user_id=callback_context.state.get("user_id","default_user"),
                          session_id=callback_context.state.get("session_id","default_session"),
                          state=callback_context.state.get("history",""),
                          source=f"{NAME}_before_model_call")


def callback_after_model_call(callback_context: CallbackContext, llm_response: LlmResponse)-> Optional[types.Content]:
    info_gather_logger.info("-- After model call hook executed.")
    info_gather_logger.info(f"CallbackContext: {callback_context.state.to_dict()}, \nLLM_Response: {llm_response}")

    memory.record_session(app_name=callback_context.state.get("app_name","default_app",),
                          user_id=callback_context.state.get("user_id","default_user"), 
                          session_id=callback_context.state.get("session_id","default_session"),
                          state=callback_context.state.get("history",""),
                          source=f"{NAME}_after_model_call")


info_gather_agent = LlmAgent(name = NAME,
                 model=MODEL, 
                 description=("analyse provided ticker symbol"),
                 instruction=prompt, 
                 tools=[extract_stock_info],
                 output_key="result",
                 before_tool_callback=callback_before_tool_call,
                 after_tool_callback=callback_after_tool_call,
                 before_agent_callback=callback_before_agent_call,
                 after_agent_callback=callback_after_agent_call,
                 before_model_callback=callback_before_model_call,
                 after_model_callback=callback_after_model_call)



