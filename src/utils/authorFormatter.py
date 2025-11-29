def format_author_list(authors):
    if not authors:
        return "No se encontraron autores con esa búsqueda."

    formatted_texts = []

    for author in authors:
        # 1. Manejo seguro de listas (ej: Géneros)
        genres = author.get('writingGenre', [])
        genres_str = ", ".join(genres) if isinstance(genres, list) else str(genres)

        # 2. Manejo de fechas (birthdate)
        birthdate_raw = author.get('birthdate')
        birthdate_str = "No especificada"
        if birthdate_raw:
            if isinstance(birthdate_raw, dict) and '$date' in birthdate_raw:
                # Caso: Formato extendido JSON { "$date": "..." }
                birthdate_str = birthdate_raw['$date'].split('T')[0]
            elif hasattr(birthdate_raw, 'strftime'):
                # Caso: Objeto datetime de Python (PyMongo estándar)
                birthdate_str = birthdate_raw.strftime('%Y-%m-%d')
            else:
                # Caso: String u otro
                birthdate_str = str(birthdate_raw).split('T')[0]

        # 3. Construcción del bloque de texto
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
    return "\n".join(formatted_texts)

def format_author_names_list(names):
    if not names:
        return "No se encontraron nombres de autores."
    
    return "Autores disponibles:\n" + "\n".join([f"- {name}" for name in names])