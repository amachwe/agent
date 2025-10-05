import pymongo 
import datetime

class SessionMemory:
    def __init__(self, app_name, url="mongodb://localhost:27017/"):
        self.client = pymongo.MongoClient(url)
        self.app_name = app_name
        self.db = app_name
        

    def save_session(self, session_id:str, user_id:str, state:dict, source:str="", **kwargs):
        ts_time = datetime.datetime.now()
        _id = f"{session_id}_{ts_time.strftime('%Y%m%d%H%M%S%f')}"

        data_state = {
            "_id": _id,
            "session_id": session_id,
            "user_id": user_id,
            "app_name": self.app_name,
            "state": state,
            "source": source,
            "timestamp": ts_time
        }

        data_state.update(kwargs)

        self.client.get_database(self.db).get_collection(user_id).insert_one(data_state)

    def get_session(self, session_instance_id:str, user_id:str ):
       return self.client.get_database(self.db).get_collection(user_id).find_one({"_id": session_instance_id})

    def get_full_session(self, session_id:str, user_id:str):
        return list(self.client.get_database(self.db).get_collection(user_id).find({"session_id": session_id}))

    def get_user(self, user_id:str):
        return list(self.client.get_database(self.db).get_collection(user_id).find({}))
    
    def get_all_users(self):
        return self.client.get_database(self.db).list_collection_names()
    
    def get_sessions_for_user(self, user_id:str):
        sessions = self.client.get_database(self.db).get_collection(user_id).distinct("session_id")
        return sessions
     

def record_session(app_name:str, session_id:str, user_id:str,  state:dict, source:str="", **kwargs):
    memory = SessionMemory(app_name)
    memory.save_session(session_id, user_id, state, source, **kwargs)
    

def purge_all_memory(app_name:str):
    memory = SessionMemory(app_name)
    memory.client.drop_database(app_name)

def build_long_term_memory(app_name:str):
    memory = SessionMemory(app_name)
    users = memory.get_all_users()
    data = {}
    for user in  users:
        sessions = memory.get_sessions_for_user(user)
        data[user] = {}
        for session in sessions:
            records = memory.get_full_session(session, user)
            record = records[-1]
            if record.get('interaction_end', False):
                long_term_memory = f"{record.get('state','')}"

            data[user][session]= long_term_memory
    return data
            


    

if __name__ == "__main__":

    from gen_ai_web_server import llm_client

    client = llm_client.Client()
    client = llm_client.GeminiClient()

    app_name = "stock_agents_app"

    data = build_long_term_memory(app_name)

    def save_to_file(filename, content):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)


    for user, sessions in data.items():
        print(f"User: {user}", len(sessions), "sessions")
        for session_id, memory in sessions.items():

            response = client.send_request(prompt=[{"role": "user", "content":f"Extract a knowledge graph and present it as RDF triples with facts and relationships from the memory:\n{memory}. Only give RDF code nothing else."}], run_config={"max_new_tokens": 1000, "model": "gemini-2.0-flash"})
            print(response)
            triple = client.extract_response(response)
            save_to_file(f"long_term_memory_{user}_{session_id}.ttl", triple)

