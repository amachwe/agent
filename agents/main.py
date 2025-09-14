from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.events import Event
from google.adk.sessions import Session, InMemorySessionService, DatabaseSessionService
import google.genai.types as types
import asyncio
import flask
import agent 
import datetime
import uuid

APP_NAME = "stock_analysis_app"
session_service = InMemorySessionService()
state_store = {}

def build_event(author: str, content: str) -> Event:
    ts = datetime.datetime.now().timestamp()
    return Event(invocation_id=str(uuid.uuid4()), author=author, id=str(ts), timestamp=ts, content=types.Content(role=author, parts=[types.Part(text=content)]))

async def call_agent(runner: Runner, current_session: Session, agent: LlmAgent, session_id:str, user_id:str, app_name:str,query_json:str):
    print("Calling agent with query:", query_json, "session_id:", session_id, "user_id:", user_id, "agent:", agent.name)
    ts = datetime.datetime.now().timestamp()
  
    await session_service.append_event(current_session, build_event("user", query_json))
    user_content = types.Content(role="user", parts=[types.Part(text=query_json)])
    print(">>>>",len(current_session.events))
    final_response = "Nothing received"

    async for response in runner.run_async(
        session_id=session_id,
        user_id=user_id,
        new_message=user_content
    ):
        if response.is_final_response() and response.content and response.content.parts:
            print("Received response:", response)
            final_response = response.content.parts[0].text
            await session_service.append_event(current_session, build_event(agent.name, final_response))
    

    current_session = await session_service.get_session(app_name=app_name, session_id=session_id, user_id=user_id)
    print("Final response:", final_response)
    print("-------------------- Session State --------------------")
    print(">>",len(current_session.events))
    print(current_session.state)
    print("-------------------------------------------------------")
    result = current_session.state.get(agent.output_key, "No result found")
    history = state_store.get((user_id, session_id),{}).get(agent.output_key, "")
    history += f"\nUser: {query_json}\nAgent: {result}"
    state_store[(user_id, session_id)] = {agent.output_key: history}
    return result

async def main(app_name:str, session_id:str, user_id:str, query_json:str):
    
    runner = Runner(app_name=app_name, agent=agent.root_agent, session_service=session_service)
    print(await session_service.list_sessions(app_name=app_name, user_id=user_id))
    current_session = await session_service.create_session(app_name=app_name, session_id=session_id, user_id=user_id, state=state_store.get((user_id, session_id),{}))
    print("Current session:", current_session)
    await call_agent(runner, current_session, agent.root_agent, session_id, user_id, app_name, query_json)


app = flask.Flask(APP_NAME)

@app.route('/agent_endpoint', methods=['POST'])
def agent_endpoint():
    
    data = flask.request.json
    query_json = data.get('query', '')
    session_id = data.get('session_id', 'default_session')
    user_id = data.get('user_id', 'test_user')

    if state_store.get((user_id, session_id), None):
        print("TRUE",state_store[(user_id, session_id)])
    else:
        print("FALSE","-------")
    print("Received request with query:", query_json, "session_id:", session_id, "user_id:", user_id) 
    asyncio.run(main(APP_NAME, session_id, user_id, query_json))
    current_session = asyncio.run(session_service.get_session(app_name=APP_NAME, session_id=session_id, user_id=user_id))
    result =current_session.state.get(agent.root_agent.output_key, "No result found")
    return flask.jsonify({"result": result})
    

if __name__ == "__main__":
    app.run(debug=True)

    
    
    
    
