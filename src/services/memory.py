from src.configs.database.connection import connect

class MemoryService():
    db = connect()
    collection = db["vectorMemorys"]
    
    def getMemoryByUserIdAndSessionId(self, user_id, session_id, limit=10):
        data = self.collection.find(
            {"userId": user_id, "sessionId": session_id},
            {"content": {"$slice": -limit}, "_id": 0}
        )
        
        data_list = list(data)
        if data_list and len(data_list) > 0 and "content" in data_list[0]:
             result = list(data_list[0]["content"])
             return result
        return []

    def saveMemory(self, user_id, session_id, user_message, ai_message):
        # Check if session exists
        existing_session = self.collection.find_one({"userId": user_id, "sessionId": session_id})
        
        new_messages = [
            {"role": "user", "text": user_message},
            {"role": "ai", "text": ai_message}
        ]

        if existing_session:
            self.collection.update_one(
                {"userId": user_id, "sessionId": session_id},
                {"$push": {"content": {"$each": new_messages}}}
            )
        else:
            self.collection.insert_one({
                "userId": user_id,
                "sessionId": session_id,
                "content": new_messages
            })