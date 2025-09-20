import pymongo 
import datetime

class SessionMemory:
    def __init__(self, app_name, url="mongodb://localhost:27017/"):
        self.client = pymongo.MongoClient(url)
        self.app_name = app_name
        self.db = app_name
        

    def save_session(self, session_id:str, user_id:str, seq:int, state:dict, source:str="", **kwargs):
        _id = SessionMemory.get_id(session_id, seq)
        data_state = {
            "_id": _id,
            "session_id": session_id,
            "user_id": user_id,
            "app_name": self.app_name,
            "state": state,
            "source": source,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data_state.update(kwargs)

        self.client.get_database(self.db).get_collection(user_id).insert_one(data_state)

    def get_session(self, session_id:str, user_id:str, seq:int):
        _id = SessionMemory.get_id(session_id, seq)
        return self.client.get_database(self.db).get_collection(user_id).find_one({"_id": _id})

    def get_full_session(self, session_id:str, user_id:str):
        return list(self.client.get_database(self.db).get_collection(user_id).find({"session_id": session_id}))

    def get_user(self, user_id:str):
        return list(self.client.get_database(self.db).get_collection(user_id).find({}))
    
    @staticmethod
    def get_id(session_id:str, seq:int):
        return f"{session_id}_{seq}"
    

def record_session(app_name:str, session_id:str, user_id:str, seq:int, state:dict, source:str="", **kwargs):
    memory = SessionMemory(app_name)
    memory.save_session(session_id, user_id, seq, state, source, **kwargs)

def purge_all_memory(app_name:str):
    memory = SessionMemory(app_name)
    memory.client.drop_database(app_name)

