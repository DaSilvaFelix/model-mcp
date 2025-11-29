from src.configs.database.connection import connect

class AuthorService():
    def __init__(self):
        self.db = connect()
        self.collection = self.db["authormodels"]
        
    def getAuthorDetailsByName(self, keywords: list[str]):
        try:
            if not keywords:
                return []

            search_string = " ".join(keywords)  

            query = { 
                "$text": { 
                    "$search": search_string 
                } 
            }

            projection = { "score": { "$meta": "textScore" } }
            sort_order = [("score", { "$meta": "textScore" })]
            
            # Limit to 1 as requested by user to get the most similar one
            authors = list(self.collection.find(query, projection).sort(sort_order).limit(1))
            
            return authors
        except Exception as e:
            print(f"Error in getAuthorDetailsByName: {e}")
            return []

    def getAllAuthorNames(self):
        try:
            authors = list(self.collection.distinct("fullName"))
            return authors
        except Exception as e:
            print(f"Error in getAllAuthorNames: {e}")
            return []

    def countTotalAuthors(self):
        try:
            count = self.collection.count_documents({})
            return count
        except Exception as e:
            print(f"Error in countTotalAuthors: {e}")
            return 0