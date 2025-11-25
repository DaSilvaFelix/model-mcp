from src.configs.database.connection import connect
from bson import ObjectId

class UserService():
    
    db = connect()
    collectionUser = db["users"]
    collectionLevel = db["levels"]
    
    def getUserById(self, userId):
        try:
            if isinstance(userId, str):
                userId = ObjectId(userId)
            user_result = self.collectionUser.find_one(
                {"_id": userId},
                {
                "_id": 0,
                "__v": 0,
                "createdAt": 0,
                "updatedAt": 0,
                "password": 0,
                "name":0,
                "email":0,
                "name":0,
                "rol":0,
                "lastName":0,
                "imgLevel":0,
                "birthDate":0,
                "avatar":0,
                })
            

            level_result = self.collectionLevel.find_one(
                {"_id": ObjectId(user_result["level"])},
                {
                "_id": 0,
                "__v": 0,
                "img": 0,
                "level_string": 0,
                "maxPoint": 0,
                })
            
            data = f"""
            nombre de usuario: {user_result["userName"]}
            nivel de lectura del usuario: {user_result["nivel"]}
            nivel de juegos del usuario: {level_result["level"]}
            puntos de experiencia del usuario: {user_result["point"]}
            subgéneros favoritos del usuario: {", ".join(user_result["preference"]["category"])}
            formato favorito del usuario: {", ".join(user_result["preference"]["format"])}
            """
            user = {
                "nivel": user_result["nivel"],
                "preference": user_result["preference"]
            }
            return user, data
        except Exception as e:
            print(f"Error buscando usuario: {e}")
            return None, None
    
    def getUserLevel(self, userId):
        """
        Obtiene solo el nivel de lectura del usuario.
        Retorna el nivel como string o None si hay error.
        """
        try:
            if isinstance(userId, str):
                userId = ObjectId(userId)
            
            user_result = self.collectionUser.find_one(
                {"_id": userId},
                {"nivel": 1, "_id": 0}
            )
            
            if user_result and "nivel" in user_result:
                return user_result["nivel"]
            else:
                return None
                
        except Exception as e:
            print(f"Error obteniendo nivel de usuario: {e}")
            return None