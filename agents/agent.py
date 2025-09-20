from google.adk.agents import LlmAgent
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import AgentTool, BaseTool, ToolContext
from google.adk.agents.callback_context import CallbackContext
from sub_agents.info_gather_agent import agent
import logging
from typing import Optional, Dict, Any
from google.genai import types
import memory 

NAME = "root_agent"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', filemode='a', filename=f'{NAME}.log')




prompt = """ you are a stock analyst who can use other agents to suppliment the analysis by gathering information.
History: {history?}"""

MODEL = "gemini-2.5-flash"

def  update_sequence(state:dict)-> int:
    seq = state.get("seq", 0)
    seq += 1
    state["seq"] = seq
    return seq

def callback_before_tool_call(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext)-> Optional[types.Content]:
    logging.info("---- Before tool call hook executed.")
    logging.info(f"Tool: {tool.name}, \nArgs: {args}, \nToolContext: {tool_context.state}")
    memory.record_session(app_name=tool_context.state.get("app_name","default_app",),
                          user_id=tool_context.state.get("user_id","default_user"),
                          session_id=tool_context.state.get("session_id","default_session"),
                          seq= tool_context.state.get("seq",0),
                          state=tool_context.state.get("history",""),
                          source=f"{NAME}_before_tool_call")
    update_sequence(tool_context.state)
    


def callback_after_tool_call(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict)-> Optional[types.Content]:
    logging.info("---- After tool call hook executed.")
    logging.info(f"Tool: {tool.name}, \nArgs: {args}, \nToolContext: {tool_context.state}, \nOutput: {tool_response}")
    memory.record_session(app_name=tool_context.state.get("app_name","default_app",),
                          user_id=tool_context.state.get("user_id","default_user"),
                          session_id=tool_context.state.get("session_id","default_session"),
                          seq= tool_context.state.get("seq",0),
                          state=tool_context.state.get("history",""),
                          source=f"{NAME}_after_tool_call")
    update_sequence(tool_context.state)
    

def callback_before_agent_call(callback_context: CallbackContext)-> Optional[types.Content]:
    logging.info("-- Before agent call hook executed.")
    logging.info(f"CallbackContext: {callback_context.invocation_id, callback_context.state.to_dict(), callback_context.user_content}")
    memory.record_session(app_name=callback_context.state.get("app_name","default_app",),
                          user_id=callback_context.state.get("user_id","default_user"),
                          session_id=callback_context.state.get("session_id","default_session"),
                          seq= callback_context.state.get("seq",0),
                          state=callback_context.state.get("history",""),
                          source=f"{NAME}_before_agent_call")
    update_sequence(callback_context.state)

def callback_after_agent_call(callback_context: CallbackContext)-> Optional[types.Content]:
    logging.info("-- After agent call hook executed.")
    logging.info(f"CallbackContext: {callback_context.invocation_id, callback_context.state.to_dict(), callback_context.user_content}")
    memory.record_session(app_name=callback_context.state.get("app_name","default_app",),
                          user_id=callback_context.state.get("user_id","default_user"),
                          session_id=callback_context.state.get("session_id","default_session"),
                          seq= callback_context.state.get("seq",0),
                          state=callback_context.state.get("history",""),
                          source=f"{NAME}_after_agent_call")
    update_sequence(callback_context.state) 

def callback_before_model_call(callback_context: CallbackContext, llm_request: LlmRequest)-> Optional[types.Content]:
    logging.info("------ Before model call hook executed.")
    logging.info(f"CallbackContext: {callback_context.state.to_dict()}, \nLLM_Request: {llm_request}")
    memory.record_session(app_name=callback_context.state.get("app_name","default_app",),
                          user_id=callback_context.state.get("user_id","default_user"),
                          session_id=callback_context.state.get("session_id","default_session"),
                          seq= callback_context.state.get("seq",0),
                          state=callback_context.state.get("history",""),
                          source=f"{NAME}_before_model_call")
    update_sequence(callback_context.state)

def callback_after_model_call(callback_context: CallbackContext, llm_response: LlmResponse)-> Optional[types.Content]:
    logging.info("------ After model call hook executed.")
    logging.info(f"CallbackContext: {callback_context.state.to_dict()}, \nLLM_Response: {llm_response}")

    memory.record_session(app_name=callback_context.state.get("app_name","default_app",),
                          user_id=callback_context.state.get("user_id","default_user"), 
                          session_id=callback_context.state.get("session_id","default_session"),
                          seq= callback_context.state.get("seq",0),
                          state=callback_context.state.get("history",""),
                          source=f"{NAME}_after_model_call")
    update_sequence(callback_context.state)

agent = LlmAgent(name = NAME,
                 model=MODEL,
                 description=("Root agent to coordinate stock analysis"),
                 instruction=prompt,
                 tools=[AgentTool(agent.info_gather_agent)],
                 output_key="result",
                 before_tool_callback=callback_before_tool_call,
                 after_tool_callback=callback_after_tool_call,
                 before_agent_callback=callback_before_agent_call,
                 after_agent_callback=callback_after_agent_call,
                 before_model_callback=callback_before_model_call,
                 after_model_callback=callback_after_model_call)

root_agent = agent