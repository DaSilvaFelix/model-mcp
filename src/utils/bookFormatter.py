def format_books_list(books: list, include_score: bool = False, page: int = 1, limit: int = 5) -> str:
    if not books:
        return "No se encontraron libros."
    
    formatted_books = [format_book_for_display(book, include_score) for book in books]
    result = "\n\n".join(formatted_books)
    
    if len(books) >= limit:
        result += f"\n\n--- Página {page} ---\n(Para ver más resultados, solicita la página {page + 1})"
    else:
        result += f"\n\n--- Página {page} (Fin de los resultados) ---"
        
    return result

def format_book_for_display(book: dict, include_score: bool = False) -> str:
    authors = book.get("author", [])
    if isinstance(authors, list):
        authors_str = ", ".join(authors) if authors else "No especificado"
    else:
        authors_str = str(authors)
    
    subgenres = book.get("subgenre", [])
    subgenres_str = ", ".join(subgenres) if isinstance(subgenres, list) and subgenres else "No especificado"
    
    themes = book.get("theme", [])
    themes_str = ", ".join(themes) if isinstance(themes, list) and themes else "No especificado"
    
    score_info = ""
    if include_score and "matchScore" in book:
        match_score = book.get("matchScore", 0)
        if match_score > 0:
            score_info = f"Relevancia: {match_score:.2f}\n"
    
    book_str = f"""
    {score_info}
    Título: {book.get("title", "Sin título")}
    Autores: {authors_str}
    Sinopsis: {book.get("synopsis", "Sin sinopsis")}
    Género: {book.get("genre", "No especificado")}
    Subgéneros: {subgenres_str}
    Temas: {themes_str}
    Nivel de lectura: {book.get("level", "No especificado")}
    Formato: {book.get("format", "No especificado")}
    Año de creación: {book.get("yearBook", "No especificado")}
    Páginas: {book.get("totalPages", "N/A")}
    Idioma: {book.get("language", "No especificado")}
    Fecha de publicación: {book.get("createdAt", "No especificado")}
    """.strip()
    
    return book_str

def sanitize_book_data(book: dict) -> dict:
    safe_fields = [
        "title", "author", "summary", "synopsis",
        "genre", "subgenre", "theme",
        "level", "format", "fileExtension",
        "yearBook", "totalPages", "language",
        "createdAt", "matchScore", "totalScore"
    ]
    
    safe_book = {}
    for field in safe_fields:
        if field in book:
            safe_book[field] = book[field]
    
    return safe_book


def sanitize_books_list(books: list) -> list:
    if not books:
        return []
    
    return [sanitize_book_data(book) for book in books]
