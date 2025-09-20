from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.events import Event
from google.adk.sessions import Session, InMemorySessionService, DatabaseSessionService
import google.genai.types as types
import asyncio
import flask
import agent 
import logging
import memory
from flask_cors import CORS

#use debug to get detailed tracing.
log_fh = logging.FileHandler('app.log')
logger = logging.getLogger(__name__)
logger.addHandler(log_fh)
logger.setLevel(logging.INFO)


#DB_URL = "sqlite:///./agent.db"
HISTORY = "history"
APP_NAME = "stock_analysis_app"
session_service = InMemorySessionService() #DatabaseSessionService(db_url=DB_URL)
session_state_store = {}


async def call_agent(runner: Runner, current_session: Session, agent: LlmAgent, session_id:str, user_id:str, app_name:str,query_json:str):
    logger.debug(f"Calling agent with query: {query_json}, session_id: {session_id}, user_id: {user_id}, agent: {agent.name}")

    #Prepare user content and call the agen t asynchronously (before - after model callbacks used).
    user_content = types.Content(role="user", parts=[types.Part(text=query_json)])
    final_response = "Nothing received"

    #Execute the primary agent run loop asynchronously.
    async for response in runner.run_async(
        session_id=session_id,
        user_id=user_id,
        new_message=user_content
    ):
        if response.is_final_response() and response.content and response.content.parts:
            logger.debug(f"Received response: {response}")
            final_response = response.content.parts[0].text

    #Agent has finished running - final response stored in final_response variable.
    #Get current session to presist state across calls while server is running in state_store variable.
    current_session = await session_service.get_session(app_name=app_name, session_id=session_id, user_id=user_id)
    print("Agent responds: ", final_response)
    logger.debug("-------------------- Session State --------------------")
    logger.debug(current_session.state)
    logger.debug("-------------------------------------------------------")
    current_state = current_session.state.get(agent.output_key, "No result found")

    seq = current_session.state.get("seq", 0)
    print(seq)
    history = session_state_store.get((user_id, session_id),{}).get(HISTORY, "")
    history += f"\nUser: {query_json}\nAgent: {current_state}"

    session_state_store[(user_id, session_id)] = {HISTORY: history, "session_id": session_id, "user_id": user_id, "app_name": app_name, "seq": seq}
    
    return final_response

async def main(app_name:str, session_id:str, user_id:str, query_json:str):
    
    runner = Runner(app_name=app_name, agent=agent.root_agent, session_service=session_service)
    #Create session with initial state from the state store (persists across calls while server is running).
    current_session = await session_service.create_session(app_name=app_name, session_id=session_id, user_id=user_id, state=session_state_store.get((user_id, session_id),{}))
    
    #Call the agent with the current session and return response (before - after agent callbacks used).
    await call_agent(runner, current_session, agent.root_agent, session_id, user_id, app_name, query_json)

app = flask.Flask(APP_NAME)
CORS(app)

@app.route('/agent_endpoint', methods=['POST'])
def agent_endpoint():
    
    data = flask.request.json
    query_json = data.get('query', '')
    session_id = data.get('session_id', 'default_session')
    user_id = data.get('user_id', 'test_user')

    if not session_state_store.get((user_id, session_id), None):
        session_state_store[(user_id, session_id)] = {"session_id": session_id, "user_id": user_id, "app_name": APP_NAME, "seq": session_state_store.get((user_id, session_id), {}).get("seq", 0)}
        logger.debug(f"Initialized state for user_id: {user_id}, session_id: {session_id}, app_name: {APP_NAME}, state: {session_state_store[(user_id, session_id)]}")

    logger.info(f"Received request with query: {query_json}, session_id: {session_id}, user_id: {user_id}")
   
    asyncio.run(main(APP_NAME, session_id, user_id, query_json))
    
    current_session = asyncio.run(session_service.get_session(app_name=APP_NAME, session_id=session_id, user_id=user_id))
    
    result =current_session.state.get(agent.root_agent.output_key, "No result found")
    
    return flask.jsonify({"result": result})
    

if __name__ == "__main__":
    #Purge all memory on restart for clean testing.
    memory.purge_all_memory(APP_NAME)
    print("Test Mode: Starting Agent Server... all memory purged.")
    
    
    app.run(debug=True)

    
    
    
    
