from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from src.services.books import BookService
from src.services.users import UserService

book_service = BookService()
user_service = UserService()

@tool(description="Devuelve el número de libros que hay en la plataforma")
def numberOfBooks():
    call_count = book_service.numberOfBooks()
    return f"El número de libros en la plataforma es: {call_count}"

@tool(description="Devuelve los libros nuevos recien agregados a la plataforma o los mas nuevos, filtrados automáticamente por el nivel de lectura del usuario.")
def getTheNewBooks(config: RunnableConfig, limit:int):
    """Obtiene libros nuevos filtrados por el nivel del usuario actual."""
    try:
        # Obtener userId del config
        configuration = config.get("configurable", {})
        user_id = configuration.get("userId")
        
        if not user_id:
            return "Error: No se pudo identificar al usuario. Por favor, intenta de nuevo."
        
        # Obtener el nivel de lectura del usuario
        user_level = user_service.getUserLevel(user_id)
        
        if not user_level:
            return "Error: No se pudo obtener el nivel de lectura del usuario. Verifica que el usuario esté registrado correctamente."
        
        # Buscar libros con el nivel del usuario
        newBooks = book_service.bookNew(user_level=user_level, limit=limit if limit is not None else 10)
        
        # Verificar si hay un error
        if isinstance(newBooks, dict) and newBooks.get("error"):
            return newBooks.get("message")
        
        if not newBooks or len(newBooks) == 0:
            return f"No se encontraron libros nuevos para tu nivel de lectura ({user_level})."
        
        books_formatted = []
        for book in newBooks:
            authors = ", ".join(book.get("author", []))
            
            subgenres = ", ".join(book.get("subgenre", []))
            themes = ", ".join(book.get("theme", []))
            
            book_str = f"""
        Título: {book.get("title", "Sin título")}
        Autores: {authors}
        Resumen: {book.get("summary", "Sin resumen")}
        Género: {book.get("genre", "No especificado")}
        Subgéneros: {subgenres}
        Temas: {themes}
        nivel de lectura: {book.get("level", "No especificado")}
        Formato: {book.get("format", "No especificado")}
        Año de creacion: {book.get("yearBook", "No especificado")}
        Páginas: {book.get("totalPages", "N/A")}
        fecha de publicacion en la plataforma: {book.get("createdAt", "No especificado")}
            """.strip()
            
            books_formatted.append(book_str)
        
        return books_formatted
        
    except Exception as e:
        return f"Error al obtener libros nuevos: {str(e)}"

@tool(description="Busca libros por título, autor, género, tema, sinopsis o resumen. Los resultados se filtran automáticamente por el nivel de lectura del usuario.")
def searchBooks(config: RunnableConfig, query: str, limit: int = 10):
    """Busca libros usando el nivel de lectura del usuario actual."""
    try:
        # Obtener userId del config
        configuration = config.get("configurable", {})
        user_id = configuration.get("userId")
        
        if not user_id:
            return "Error: No se pudo identificar al usuario. Por favor, intenta de nuevo."
        
        # Obtener el nivel de lectura del usuario
        user_level = user_service.getUserLevel(user_id)
        
        if not user_level:
            return "Error: No se pudo obtener el nivel de lectura del usuario. Verifica que el usuario esté registrado correctamente."
        
        # Buscar libros con el nivel del usuario
        search_results = book_service.getBookByQuery(query, user_level=user_level, limit=limit)
        
        # Verificar si hay un error
        if isinstance(search_results, dict) and search_results.get("error"):
            return search_results.get("message")
        
        if not search_results or len(search_results) == 0:
            return f"No se encontraron libros que coincidan con tu búsqueda para tu nivel de lectura ({user_level})."
        
        books_formatted = []
        for book in search_results:
            authors = ", ".join(book.get("author", []))
            
            subgenres = ", ".join(book.get("subgenre", []))
            themes = ", ".join(book.get("theme", []))
            
            match_score = book.get("matchScore", 0)
            score_info = f"Relevancia: {match_score:.2f}\n" if match_score > 0 else ""
            
            book_str = f"""
        {score_info}Título: {book.get("title", "Sin título")}
        Autores: {authors}
        Resumen: {book.get("summary", "Sin resumen")}
        Género: {book.get("genre", "No especificado")}
        Subgéneros: {subgenres}
        Temas: {themes}
        Nivel de lectura: {book.get("level", "No especificado")}
        Formato: {book.get("format", "No especificado")}
        Año de creación: {book.get("yearBook", "No especificado")}
        Páginas: {book.get("totalPages", "N/A")}
        Fecha de publicación en la plataforma: {book.get("createdAt", "No especificado")}
            """.strip()
            
            books_formatted.append(book_str)
        
        return books_formatted
        
    except Exception as e:
        return f"Error al buscar libros: {str(e)}"
