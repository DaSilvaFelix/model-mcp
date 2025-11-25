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
                    
                    if "createdAt" in book and book["createdAt"]:
                        book["createdAt"] = book["createdAt"].strftime("%Y-%m-%d")
            
                return data_list
            else:
                return []
                
        except Exception as e:
            return {
                "error": True,
                "message": f"Error al buscar libros: {str(e)}. Verifica que hayas usado 'whoIsHeIsUser' para obtener el nivel de lectura del usuario primero."
            }

    def getBookByQuery(self, query, user_level=None, limit=10):
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
            
            allowed_levels = self.get_allowed_levels(user_level)
            
            if not allowed_levels:
                return {
                    "error": True,
                    "message": f"El nivel '{user_level}' no es válido. Niveles válidos: Inicial, Secundario, Joven Adulto, Adulto Mayor. Verifica el nivel de lectura del usuario usando 'whoIsHeIsUser'."
                }
            
            match_text = {"$text": {"$search": search_text}}
            match_text["level"] = {"$in": allowed_levels}
        
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
                        "createdAt": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$createdAt"
                            }
                        },
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
                ordered_books = []
        
            if len(ordered_books) == 0:
                words = search_text.split()
                regex_pattern = "|".join(words)
                regex = re.compile(regex_pattern, re.IGNORECASE)
                
                regex_match = {}
                if allowed_levels:
                    regex_match["level"] = {"$in": allowed_levels}
                
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
                            "createdAt": {
                                "$dateToString": {
                                    "format": "%Y-%m-%d",
                                    "date": "$createdAt"
                                }
                            },
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
            
            if ordered_books and len(ordered_books) > 0:
                for book in ordered_books:
                    if "author" in book and isinstance(book["author"], list):
                        author_names = [a.get("fullName", "") for a in book["author"] if "fullName" in a]
                        book["author"] = author_names
            
            return ordered_books
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Error al buscar libros: {str(e)}. Verifica que hayas usado 'whoIsHeIsUser' para obtener el nivel de lectura del usuario primero."
            }

    def getRecommendation(self, user, limit=10):
        try:
            if not user or "nivel" not in user:
                return {
                    "error": True,
                    "message": "INSTRUCCIÓN: Primero debes usar la herramienta 'whoIsHeIsUser' para obtener los datos del usuario incluyendo su nivel de lectura y preferencias."
                }
            
            if "preference" not in user or not user["preference"]:
                return {
                    "error": True,
                    "message": "El usuario no tiene preferencias configuradas. Necesita tener categorías y formatos preferidos."
                }
            
            user_categories = user.get("preference", {}).get("category", [])
            user_formats = user.get("preference", {}).get("format", [])
            user_level = user.get("nivel", "")
            
            pipeline = [
                {
                    "$match": {
                        "level": user_level
                    }
                },
                {
                    "$addFields": {
                        "subgenreScore": {
                            "$size": {
                                "$setIntersection": ["$subgenre", user_categories]
                            }
                        },
                        "formatScore": {
                            "$cond": [
                                {"$in": ["$format", user_formats]},
                                1,
                                0
                            ]
                        }
                    }
                },
                {
                    "$addFields": {
                        "totalScore": {
                            "$add": ["$subgenreScore", "$formatScore"]
                        }
                    }
                },
                {
                    "$lookup": {
                        "from": "authormodels",
                        "localField": "author",
                        "foreignField": "_id",
                        "as": "authorData"
                    }
                },
                {
                    "$sort": {"totalScore": -1, "stock": -1}
                },
                {
                    "$limit": limit
                },
                {
                    "$project": {
                        "_id": 1,
                        "title": 1,
                        "summary": 1,
                        "synopsis": 1,
                        "subgenre": 1,
                        "theme": 1,
                        "genre": 1,
                        "yearBook": 1,
                        "language": 1,
                        "available": 1,
                        "level": 1,
                        "format": 1,
                        "fileExtension": 1,
                        "totalPages": 1,
                        "createdAt": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$createdAt"
                            }
                        },
                        "updatedAt": 1,
                        "contentBook": 1,
                        "bookCoverImage": 1,
                        "totalScore": 1,
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
                }
            ]
            
            recommendations = list(self.collectionBooks.aggregate(pipeline))

            for book in recommendations:
                if "author" in book and isinstance(book["author"], list):
                    author_names = [a.get("fullName", "") for a in book["author"] if "fullName" in a]
                    book["author"] = author_names

            return recommendations
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Error al obtener recomendaciones: {str(e)}. Verifica que hayas usado 'whoIsHeIsUser' para obtener los datos del usuario primero."
            }

    def getBooksByGenre(self, genre: str, user_level: str = None, limit: int = 10):
        try:
            if not user_level or user_level.strip() == "":
                return {
                    "error": True,
                    "message": "INSTRUCCIÓN: Primero debes usar la herramienta 'whoIsHeIsUser' para obtener el nivel de lectura del usuario."
                }
            
            allowed_levels = self.get_allowed_levels(user_level)
            
            if not allowed_levels:
                return {
                    "error": True,
                    "message": f"El nivel '{user_level}' no es válido."
                }
            
            books = list(self.collectionBooks.find(
                {
                    "genre": {"$regex": genre, "$options": "i"},
                    "level": {"$in": allowed_levels}
                },
                {
                    "_id": 0,
                    "contentBook": 0,
                    "bookCoverImage": 0,
                    "__v": 0,
                    "available": 0,
                    "updatedAt": 0
                }
            ).limit(limit))
            
            for book in books:
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
                
                if "createdAt" in book and book["createdAt"]:
                    book["createdAt"] = book["createdAt"].strftime("%Y-%m-%d")
            
            return books
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Error al buscar libros por género: {str(e)}"
            }

    def getBooksByAuthor(self, author_name: str, user_level: str = None, limit: int = 10):
        """Obtiene libros de un autor específico filtrados por nivel de usuario."""
        try:
            if not user_level or user_level.strip() == "":
                return {
                    "error": True,
                    "message": "INSTRUCCIÓN: Primero debes usar la herramienta 'whoIsHeIsUser' para obtener el nivel de lectura del usuario."
                }
            
            allowed_levels = self.get_allowed_levels(user_level)
            
            if not allowed_levels:
                return {
                    "error": True,
                    "message": f"El nivel '{user_level}' no es válido."
                }
            
            # Buscar autores que coincidan
            authors = list(self.collectionAuthors.find(
                {"fullName": {"$regex": author_name, "$options": "i"}},
                {"_id": 1}
            ))
            
            if not authors:
                return []
            
            author_ids = [author["_id"] for author in authors]
            
            # Buscar libros de esos autores
            books = list(self.collectionBooks.find(
                {
                    "author": {"$in": author_ids},
                    "level": {"$in": allowed_levels}
                },
                {
                    "_id": 0,
                    "contentBook": 0,
                    "bookCoverImage": 0,
                    "__v": 0,
                    "available": 0,
                    "updatedAt": 0
                }
            ).limit(limit))
            
            for book in books:
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
                
                if "createdAt" in book and book["createdAt"]:
                    book["createdAt"] = book["createdAt"].strftime("%Y-%m-%d")
            
            return books
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Error al buscar libros por autor: {str(e)}"
            }

    def getAvailableGenres(self, user_level: str = None):
        """Obtiene la lista de géneros disponibles para el nivel del usuario."""
        try:
            if not user_level or user_level.strip() == "":
                return {
                    "error": True,
                    "message": "INSTRUCCIÓN: Primero debes usar la herramienta 'whoIsHeIsUser' para obtener el nivel de lectura del usuario."
                }
            
            allowed_levels = self.get_allowed_levels(user_level)
            
            if not allowed_levels:
                return {
                    "error": True,
                    "message": f"El nivel '{user_level}' no es válido."
                }
            
            genres = self.collectionBooks.distinct("genre", {"level": {"$in": allowed_levels}})
            return list(genres)
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Error al obtener géneros: {str(e)}"
            }

    def getPopularAuthors(self, user_level: str = None, limit: int = 10):
        """Obtiene los autores más populares (con más libros) para el nivel del usuario."""
        try:
            if not user_level or user_level.strip() == "":
                return {
                    "error": True,
                    "message": "INSTRUCCIÓN: Primero debes usar la herramienta 'whoIsHeIsUser' para obtener el nivel de lectura del usuario."
                }
            
            allowed_levels = self.get_allowed_levels(user_level)
            
            if not allowed_levels:
                return {
                    "error": True,
                    "message": f"El nivel '{user_level}' no es válido."
                }
            
            pipeline = [
                {"$match": {"level": {"$in": allowed_levels}}},
                {"$unwind": "$author"},
                {"$group": {
                    "_id": "$author",
                    "bookCount": {"$sum": 1}
                }},
                {"$sort": {"bookCount": -1}},
                {"$limit": limit},
                {"$lookup": {
                    "from": "authormodels",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "authorData"
                }},
                {"$unwind": "$authorData"},
                {"$project": {
                    "_id": 0,
                    "author": "$authorData.fullName",
                    "bookCount": 1
                }}
            ]
            
            authors = list(self.collectionBooks.aggregate(pipeline))
            return authors
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Error al obtener autores populares: {str(e)}"
            }

    def getBooksByFormat(self, format_type: str, user_level: str = None, limit: int = 10):
        """Obtiene libros filtrados por formato (ebook, físico, etc.) y nivel de usuario."""
        try:
            if not user_level or user_level.strip() == "":
                return {
                    "error": True,
                    "message": "INSTRUCCIÓN: Primero debes usar la herramienta 'whoIsHeIsUser' para obtener el nivel de lectura del usuario."
                }
            
            allowed_levels = self.get_allowed_levels(user_level)
            
            if not allowed_levels:
                return {
                    "error": True,
                    "message": f"El nivel '{user_level}' no es válido."
                }
            
            books = list(self.collectionBooks.find(
                {
                    "format": {"$regex": format_type, "$options": "i"},
                    "level": {"$in": allowed_levels}
                },
                {
                    "_id": 0,
                    "contentBook": 0,
                    "bookCoverImage": 0,
                    "__v": 0,
                    "available": 0,
                    "updatedAt": 0
                }
            ).limit(limit))
            
            for book in books:
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
                
                if "createdAt" in book and book["createdAt"]:
                    book["createdAt"] = book["createdAt"].strftime("%Y-%m-%d")
            
            return books
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Error al buscar libros por formato: {str(e)}"
            }

    def getAvailableSubGenres(self, user_level: str = None):
        try:
            if not user_level or user_level.strip() == "":
                return {
                    "error": True,
                    "message": "INSTRUCCIÓN: Primero debes usar la herramienta 'whoIsHeIsUser' para obtener el nivel de lectura del usuario."
                }
            
            allowed_levels = self.get_allowed_levels(user_level)
            
            if not allowed_levels:
                return {
                    "error": True,
                    "message": f"El nivel '{user_level}' no es válido."
                }
            
            subgenres = self.collectionBooks.distinct("subgenre", {"level": {"$in": allowed_levels}})
            return list(subgenres)
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Error al obtener subgéneros: {str(e)}"
            }
