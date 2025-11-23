from src.configs.database.connection import connect
from bson import ObjectId
import re

class BookService():
    db = connect()
    collectionBooks = db["books"]
    collectionAuthors = db["authormodels"]
    
    level_hierarchy = {
        "Inicial": ["Inicial"],
        "Secundario": ["Secundario", "Inicial"],
        "Joven Adulto": ["Joven Adulto", "Secundario", "Inicial"],
        "Adulto Mayor": ["Adulto Mayor", "Joven Adulto", "Secundario", "Inicial"]
    }
    
    def get_allowed_levels(self, user_level):
        if not user_level:
            return None
        
        normalized_level = user_level.title()
        
        return self.level_hierarchy.get(normalized_level, [normalized_level])
    
    def numberOfBooks(self):
        return self.collectionBooks.count_documents({})

    def bookNew(self, user_level:str, limit=10):
        try:
            if not user_level or user_level.strip() == "":
                return {
                    "error": True,
                    "message": "INSTRUCCIÓN: Primero debes usar la herramienta 'whoIsHeIsUser' para obtener el nivel de lectura del usuario. Una vez que tengas el 'nivel de lectura del usuario', vuelve a llamar a esta herramienta con el parámetro 'user_level' correcto."
                }
            
            allowed_levels = self.get_allowed_levels(user_level)
            
            if not allowed_levels:
                return {
                    "error": True,
                    "message": f"El nivel '{user_level}' no es válido. Niveles válidos: Inicial, Secundario, Joven Adulto, Adulto Mayor. Verifica el nivel de lectura del usuario usando 'whoIsHeIsUser'."
                }
        
            level_filter = {"level": {"$in": allowed_levels}}
        
            bookNew = self.collectionBooks.find(
                level_filter,
                {
                    "_id": 0,
                    "language": 0,
                    "available": 0,
                    "fileExtension": 0,
                    "anthology": 0,
                    "contentBook": 0,
                    "bookCoverImage": 0,
                    "__v": 0,
                }
            ).sort("createdAt", -1).limit(limit)

            data_list = list(bookNew)
        
            if data_list and len(data_list) > 0:
                for book in data_list:
                    if "author" in book and isinstance(book["author"], list):
                        author_names = []
                        for author_id in book["author"]:
                            author = self.collectionAuthors.find_one(
                                {"_id": author_id},
                                {"fullName": 1, "_id": 0}
                            )
                            if author and "fullName" in author:
                                author_names.append(author["fullName"])
                        book["author"] = author_names
            
                return data_list
            else:
                return []
                
        except Exception as e:
            return {
                "error": True,
                "message": f"Error al buscar libros: {str(e)}. Verifica que hayas usado 'whoIsHeIsUser' para obtener el nivel de lectura del usuario primero."
            }

    def getBookByQuery(self, query, user_level=None, limit=10):
        """
        Búsqueda inteligente de libros usando text search con fallback a regex.
        Filtra por nivel del usuario y niveles inferiores según jerarquía.
        """
        try:
            if not user_level or user_level.strip() == "":
                return {
                    "error": True,
                    "message": "INSTRUCCIÓN: Primero debes usar la herramienta 'whoIsHeIsUser' para obtener el nivel de lectura del usuario. Una vez que tengas el 'nivel de lectura del usuario', vuelve a llamar a esta herramienta con el parámetro 'user_level' correcto."
                }
            
            if isinstance(query, list):
                search_text = " ".join(query)
            else:
                search_text = query
            
            # Obtener los niveles permitidos según la jerarquía
            allowed_levels = self.get_allowed_levels(user_level)
            
            if not allowed_levels:
                return {
                    "error": True,
                    "message": f"El nivel '{user_level}' no es válido. Niveles válidos: Inicial, Secundario, Joven Adulto, Adulto Mayor. Verifica el nivel de lectura del usuario usando 'whoIsHeIsUser'."
                }
            
            # Construir el match para text search
            match_text = {"$text": {"$search": search_text}}
            match_text["level"] = {"$in": allowed_levels}
        
            # Pipeline de agregación con text search
            pipeline = [
                {"$match": match_text},
                {
                    "$lookup": {
                        "from": "authormodels",
                        "localField": "author",
                        "foreignField": "_id",
                        "as": "authorData"
                    }
                },
                {"$addFields": {"matchScore": {"$meta": "textScore"}}},
                {"$sort": {"matchScore": -1, "createdAt": -1}},
                {
                    "$project": {
                        "_id": 0,
                        "title": 1,
                        "summary": 1,
                        "synopsis": 1,
                        "subgenre": 1,
                        "theme": 1,
                        "genre": 1,
                        "yearBook": 1,
                        "level": 1,
                        "format": 1,
                        "totalPages": 1,
                        "createdAt": 1,
                        "matchScore": 1,
                        "author": {
                            "$map": {
                                "input": "$authorData",
                                "as": "a",
                                "in": {
                                    "_id": "$$a._id",
                                    "fullName": "$$a.fullName"
                                }
                            }
                        }
                    }
                },
                {"$limit": limit}
            ]
            
            try:
                ordered_books = list(self.collectionBooks.aggregate(pipeline))
            except Exception as e:
                # Si falla el text search (ej: no hay índice de texto), usar lista vacía
                ordered_books = []
        
            # Si no hay resultados, usar búsqueda por regex (fallback)
            if len(ordered_books) == 0:
                # Crear regex pattern con todas las palabras
                words = search_text.split()
                regex_pattern = "|".join(words)
                regex = re.compile(regex_pattern, re.IGNORECASE)
                
                # Construir match para regex
                regex_match = {}
                if allowed_levels:
                    regex_match["level"] = {"$in": allowed_levels}
                
                # Pipeline con regex
                pipeline_regex = [
                    {
                        "$lookup": {
                            "from": "authormodels",
                            "localField": "author",
                            "foreignField": "_id",
                            "as": "authorData"
                        }
                    },
                    {
                        "$match": {
                            **regex_match,
                            "$or": [
                                {"title": {"$regex": regex}},
                                {"summary": {"$regex": regex}},
                                {"synopsis": {"$regex": regex}},
                                {"genre": {"$regex": regex}},
                                {"theme": {"$regex": regex}},
                                {"subgenre": {"$regex": regex}},
                                {"authorData.fullName": {"$regex": regex}}
                            ]
                        }
                    },
                    {"$addFields": {"matchScore": 0.1}},
                    {
                        "$project": {
                            "_id": 0,
                            "title": 1,
                            "summary": 1,
                            "synopsis": 1,
                            "subgenre": 1,
                            "theme": 1,
                            "genre": 1,
                            "yearBook": 1,
                            "level": 1,
                            "format": 1,
                            "totalPages": 1,
                            "createdAt": 1,
                            "matchScore": 1,
                            "author": {
                                "$map": {
                                    "input": "$authorData",
                                    "as": "a",
                                    "in": {
                                        "_id": "$$a._id",
                                        "fullName": "$$a.fullName"
                                    }
                                }
                            }
                        }
                    },
                    {"$sort": {"createdAt": -1}},
                    {"$limit": limit}
                ]
                
                ordered_books = list(self.collectionBooks.aggregate(pipeline_regex))
            
            # Formatear los autores de ObjectId a nombres
            if ordered_books and len(ordered_books) > 0:
                for book in ordered_books:
                    if "author" in book and isinstance(book["author"], list):
                        # Extraer solo los nombres de los autores
                        author_names = [a.get("fullName", "") for a in book["author"] if "fullName" in a]
                        book["author"] = author_names
            
            return ordered_books
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Error al buscar libros: {str(e)}. Verifica que hayas usado 'whoIsHeIsUser' para obtener el nivel de lectura del usuario primero."
            }


