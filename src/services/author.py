from src.configs.database.connection import connect

class AuthorService():
    def __init__(self):
        self.db = connect()
        self.collection = self.db["authormodels"]
        
    def getAuthorDetailsByName(self, keywords: list[str], limit: int = 5, page: int = 1):
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
            
            authors = list(self.collection.find(query, projection).sort(sort_order).skip((page - 1) * limit).limit(limit))
            
            return authors
        except Exception as e:
            print(f"Error in getAuthorDetailsByName: {e}")
            return []

    def getAllAuthorNames(self, limit: int = 5, page: int = 1):
        try:
            authors = list(self.collection.distinct("fullName"))
            
            # Pagination for list
            start = (page - 1) * limit
            end = start + limit
            return authors[start:end]
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