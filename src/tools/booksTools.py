from langchain_core.tools import tool
from typing import Literal
from langchain_core.runnables import RunnableConfig
from src.services.books import BookService
from src.services.users import UserService
from src.utils.bookFormatter import format_books_list

book_service = BookService()
user_service = UserService()

@tool(description="Devuelve el número de libros que hay en la plataforma")
def numberOfBooks():
    call_count = book_service.numberOfBooks()
    return f"El número de libros en la plataforma es: {call_count}"

@tool(description="Devuelve los libros nuevos recién agregados a la plataforma o los mas nuevos, filtrados automáticamente por el nivel de lectura del usuario.")
def getTheNewBooks(config: RunnableConfig, limit: int = 5, page: int = 1):
    try:
        configuration = config.get("configurable", {})
        user_id = configuration.get("userId")
        
        if not user_id:
            return "Error: No se pudo identificar al usuario. Por favor, intenta de nuevo."
        
        user_level = user_service.getUserLevel(user_id)
        
        if not user_level:
            return "Error: No se pudo obtener el nivel de lectura del usuario. Verifica que el usuario esté registrado correctamente."
        
        newBooks = book_service.bookNew(user_level=user_level, limit=limit, page=page)
        
        if isinstance(newBooks, dict) and newBooks.get("error"):
            return newBooks.get("message")
        
        if not newBooks or len(newBooks) == 0:
            return f"No se encontraron libros nuevos para tu nivel de lectura ({user_level})."
        
        return format_books_list(newBooks, include_score=False, page=page, limit=limit)
        
    except Exception as e:
        return f"Error al obtener libros nuevos: {str(e)}"

@tool(description="Busca libros por título, autor, género, tema, sinopsis o resumen. Los resultados se filtran automáticamente por el nivel de lectura del usuario.")
def searchBooks(config: RunnableConfig, query: list[str] | str, limit: int = 5, page: int = 1):
    try:
        configuration = config.get("configurable", {})
        user_id = configuration.get("userId")
        
        if not user_id:
            return "Error: No se pudo identificar al usuario. Por favor, intenta de nuevo."
        
        user_level = user_service.getUserLevel(user_id)
        
        if not user_level:
            return "Error: No se pudo obtener el nivel de lectura del usuario. Verifica que el usuario esté registrado correctamente."
        
        search_results = book_service.getBookByQuery(query, user_level=user_level, limit=limit, page=page)
        
        if isinstance(search_results, dict) and search_results.get("error"):
            return search_results.get("message")
        
        if not search_results or len(search_results) == 0:
            return f"No se encontraron libros que coincidan con tu búsqueda para tu nivel de lectura ({user_level})."
        
        return format_books_list(search_results, include_score=True, page=page, limit=limit)
        
    except Exception as e:
        return f"Error al buscar libros: {str(e)}"

@tool(description="Devuelve recomendaciones personalizadas de libros basadas en las preferencias del usuario actual.")
def getRecommendation(config: RunnableConfig, limit: int = 5, page: int = 1):
    try:
        configuration = config.get("configurable", {})
        user_id = configuration.get("userId")
        
        if not user_id:
            return "Error: No se pudo identificar al usuario. Por favor, intenta de nuevo."
        
        user, data = user_service.getUserById(user_id)
        
        if not user:
            return "Error: No se pudo obtener los datos del usuario. Verifica que el usuario esté registrado correctamente."
        
        recommendations = book_service.getRecommendation(user, limit=limit, page=page)
        
        if isinstance(recommendations, dict) and recommendations.get("error"):
            return recommendations.get("message")
        
        if not recommendations or len(recommendations) == 0:
            return f"No se encontraron recomendaciones para las preferencias del usuario."
        
        return format_books_list(recommendations, include_score=False, page=page, limit=limit)
        
    except Exception as e:
        return f"Error al obtener recomendaciones: {str(e)}"

@tool(description="Busca libros de un autor específico por su nombre. Los resultados se filtran automáticamente por el nivel de lectura del usuario.")
def getBooksByAuthor(config: RunnableConfig, author_name: str, limit: int = 5, page: int = 1):
    try:
        configuration = config.get("configurable", {})
        user_id = configuration.get("userId")
        
        if not user_id:
            return "Error: No se pudo identificar al usuario."
        
        user_level = user_service.getUserLevel(user_id)
        
        if not user_level:
            return "Error: No se pudo obtener el nivel de lectura del usuario."
        
        books = book_service.getBooksByAuthor(author_name, user_level=user_level, limit=limit, page=page)
        
        if isinstance(books, dict) and books.get("error"):
            return books.get("message")
        
        if not books or len(books) == 0:
            return f"No se encontraron libros del autor '{author_name}' para tu nivel de lectura ({user_level})."
        
        return format_books_list(books, include_score=False, page=page, limit=limit)
        
    except Exception as e:
        return f"Error al buscar libros por autor: {str(e)}"

@tool(description="Obtiene la lista de géneros literarios disponibles en la plataforma para el nivel de lectura del usuario.")
def getAvailableGenres(config: RunnableConfig, limit: int = 5, page: int = 1):
    try:
        configuration = config.get("configurable", {})
        user_id = configuration.get("userId")
        
        if not user_id:
            return "Error: No se pudo identificar al usuario."
        
        user_level = user_service.getUserLevel(user_id)
        
        if not user_level:
            return "Error: No se pudo obtener el nivel de lectura del usuario."
        
        genres = book_service.getAvailableGenres(user_level=user_level, limit=limit, page=page)
        
        if isinstance(genres, dict) and genres.get("error"):
            return genres.get("message")
        
        if not genres or len(genres) == 0:
            return "No se encontraron géneros disponibles."
        
        result = f"Géneros disponibles para tu nivel de lectura ({user_level}): {', '.join(genres)}"
        if len(genres) >= limit:
            result += f"\n\n--- Página {page} ---\n(Para ver más resultados, solicita la página {page + 1})"
        else:
            result += f"\n\n--- Página {page} (Fin de los resultados) ---"
        return result
        
    except Exception as e:
        return f"Error al obtener géneros: {str(e)}"

@tool(description="Obtiene los subgéneros literarios disponibles en la plataforma para el nivel de lectura del usuario.")
def getAvailableSubGenres(config: RunnableConfig, limit: int = 5, page: int = 1):
    try:
        configuration = config.get("configurable", {})
        user_id = configuration.get("userId")
        
        if not user_id:
            return "Error: No se pudo identificar al usuario."
        
        user_level = user_service.getUserLevel(user_id)
        
        if not user_level:
            return "Error: No se pudo obtener el nivel de lectura del usuario."
        
        subgenres = book_service.getAvailableSubGenres(user_level=user_level, limit=limit, page=page)
        
        if isinstance(subgenres, dict) and subgenres.get("error"):
            return subgenres.get("message")
        
        if not subgenres or len(subgenres) == 0:
            return "No se encontraron subgéneros disponibles."
        
        result = f"Subgéneros disponibles para tu nivel de lectura ({user_level}): {', '.join(subgenres)}"
        if len(subgenres) >= limit:
            result += f"\n\n--- Página {page} ---\n(Para ver más resultados, solicita la página {page + 1})"
        else:
            result += f"\n\n--- Página {page} (Fin de los resultados) ---"
        return result
        
    except Exception as e:
        return f"Error al obtener subgéneros: {str(e)}"

@tool(description="Obtiene los autores más populares (con más libros publicados) en la plataforma para el nivel de lectura del usuario.")
def getPopularAuthors(config: RunnableConfig, limit: int = 5, page: int = 1):
    try:
        configuration = config.get("configurable", {})
        user_id = configuration.get("userId")
        
        if not user_id:
            return "Error: No se pudo identificar al usuario."
        
        user_level = user_service.getUserLevel(user_id)
        
        if not user_level:
            return "Error: No se pudo obtener el nivel de lectura del usuario."
        
        authors = book_service.getPopularAuthors(user_level=user_level, limit=limit, page=page)
        
        if isinstance(authors, dict) and authors.get("error"):
            return authors.get("message")
        
        if not authors or len(authors) == 0:
            return "No se encontraron autores."
        
        authors_formatted = []
        for author in authors:
            authors_formatted.append(f"{author.get('author', 'Desconocido')} - {author.get('bookCount', 0)} libros")
        
        result = f"Autores más populares para tu nivel de lectura ({user_level}):\n" + "\n".join(authors_formatted)
        if len(authors) >= limit:
            result += f"\n\n--- Página {page} ---\n(Para ver más resultados, solicita la página {page + 1})"
        else:
            result += f"\n\n--- Página {page} (Fin de los resultados) ---"
        return result
        
    except Exception as e:
        return f"Error al obtener autores populares: {str(e)}"

@tool(description="Busca libros por formato (ebook, videobook, audiobook). Los resultados se filtran automáticamente por el nivel de lectura del usuario.")
def getBooksByFormat(config: RunnableConfig, format_type: Literal["ebook", "videobook", "audiobook"] = "ebook", limit: int = 5, page: int = 1):
    try:
        configuration = config.get("configurable", {})
        user_id = configuration.get("userId")
        
        if not user_id:
            return "Error: No se pudo identificar al usuario."
        
        user_level = user_service.getUserLevel(user_id)
        
        if not user_level:
            return "Error: No se pudo obtener el nivel de lectura del usuario."
        
        books = book_service.getBooksByFormat(format_type, user_level=user_level, limit=limit, page=page)
        
        if isinstance(books, dict) and books.get("error"):
            return books.get("message")
        
        if not books or len(books) == 0:
            return f"No se encontraron libros en formato '{format_type}' para tu nivel de lectura ({user_level})."
        
        return format_books_list(books, include_score=False, page=page, limit=limit)
        
    except Exception as e:
        return f"Error al buscar libros por formato: {str(e)}"

@tool(description="Devuelve un libro aleatorio de la plataforma, adecuado para el nivel de lectura del usuario.")
def getRandomBook(config: RunnableConfig):
    try:
        configuration = config.get("configurable", {})
        user_id = configuration.get("userId")
        
        if not user_id:
            return "Error: No se pudo identificar al usuario."
        
        user_level = user_service.getUserLevel(user_id)
        
        if not user_level:
            return "Error: No se pudo obtener el nivel de lectura del usuario."
        
        book = book_service.getRandomBook(user_level=user_level)
        
        if isinstance(book, dict) and book.get("error"):
            return book.get("message")
        
        if not book:
            return "No se pudo encontrar un libro aleatorio."
        
        authors = ", ".join(book.get("author", []))
        return f"¡Aquí tienes un libro sorpresa!\n\nTítulo: {book.get('title')}\nAutor: {authors}\nGénero: {book.get('genre')}\nResumen: {book.get('summary')}"
        
    except Exception as e:
        return f"Error al obtener libro aleatorio: {str(e)}"

@tool(description="Devuelve estadísticas generales de la plataforma (total de libros, autores, géneros).")
def getPlatformStats():
    try:
        stats = book_service.getPlatformStats()
        
        if isinstance(stats, dict) and stats.get("error"):
            return stats.get("message")
        
        return (f"Estadísticas de Tintas Formoseñas:\n"
                f"- Total de libros: {stats.get('total_books')}\n"
                f"- Total de autores: {stats.get('total_authors')}\n"
                f"- Variedad de géneros: {stats.get('total_genres')}")
        
    except Exception as e:
        return f"Error al obtener estadísticas: {str(e)}"
