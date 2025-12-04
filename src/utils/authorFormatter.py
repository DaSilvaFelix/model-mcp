def format_author_list(authors, page: int = 1, limit: int = 5):
    if not authors:
        return "No se encontraron autores con esa búsqueda."

    formatted_texts = []

    for author in authors:
        genres = author.get('writingGenre', [])
        genres_str = ", ".join(genres) if isinstance(genres, list) else str(genres)
        birthdate_raw = author.get('birthdate')
        birthdate_str = "No especificada"
        if birthdate_raw:
            if isinstance(birthdate_raw, dict) and '$date' in birthdate_raw:
                birthdate_str = birthdate_raw['$date'].split('T')[0]
            elif hasattr(birthdate_raw, 'strftime'):
                birthdate_str = birthdate_raw.strftime('%Y-%m-%d')
            else:
                birthdate_str = str(birthdate_raw).split('T')[0]

        author_block = (
            f"Nombre: {author.get('fullName', 'Desconocido')}\n"
            f"Profesión: {author.get('profession', 'No especificada')}\n"
            f"Nacionalidad: {author.get('nationality', 'No especificada')}\n"
            f"Lugar de nacimiento: {author.get('birthplace', 'No especificado')}\n"
            f"Fecha de nacimiento: {birthdate_str}\n"
            f"Géneros literarios: {genres_str}\n"
            f"Biografía: {author.get('biography', 'Sin biografía disponible')}\n"
        )
        
        formatted_texts.append(author_block)

    # Unimos todos los bloques con un salto de línea extra
    result = "\n".join(formatted_texts)
    
    if len(authors) >= limit:
        result += f"\n\n--- Página {page} ---\n(Para ver más resultados, solicita la página {page + 1})"
    else:
        result += f"\n\n--- Página {page} (Fin de los resultados) ---"
        
    return result

def format_author_names_list(names, page: int = 1, limit: int = 5):
    if not names:
        return "No se encontraron nombres de autores."
    
    result = "Autores disponibles:\n" + "\n".join([f"- {name}" for name in names])
    
    if len(names) >= limit:
        result += f"\n\n--- Página {page} ---\n(Para ver más resultados, solicita la página {page + 1})"
    else:
        result += f"\n\n--- Página {page} (Fin de los resultados) ---"
        
    return result