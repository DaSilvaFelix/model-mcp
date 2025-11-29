from langchain_core.tools import tool
from src.services.author import AuthorService
from src.utils.authorFormatter import format_author_list, format_author_names_list

author_service = AuthorService()

@tool(description="Devuelve el número total de autores registrados en la plataforma.")
def countAuthors():
    count = author_service.countTotalAuthors()
    return f"Total de autores registrados: {count}"

@tool(description="Busca y devuelve los detalles de un autor específico por su nombre o palabras clave.")
def getAuthorDetails(names: list[str]):
    authors = author_service.getAuthorDetailsByName(names)
    return format_author_list(authors)

@tool(description="Devuelve la lista de todos los nombres de autores disponibles en la plataforma.")
def getAllAuthorNames():
    authors = author_service.getAllAuthorNames()
    return format_author_names_list(authors)


