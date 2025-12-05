from langchain_core.tools import tool
from src.services.platform import PlatformService

platform_service = PlatformService()

@tool(description="Provee información general, misión y características de la plataforma Tintas Formoseñas.")
def getPlatformInfo():
    """
    Utiliza esta herramienta cuando el usuario pregunte qué es Tintas Formoseñas, 
    cuál es su objetivo, o qué características tiene la plataforma en general.
    """
    return platform_service.get_platform_info()

@tool(description="Provee información sobre los concursos literarios 'Letras del Viento Norte'.")
def getContestsInfo():
    """
    Utiliza esta herramienta cuando el usuario pregunte sobre concursos literarios, 
    participación de empleados públicos, o 'Letras del Viento Norte'.
    """
    return platform_service.get_contests_info()

@tool(description="Provee información sobre las antologías y la Biblioteca Interactiva Digital.")
def getAnthologiesInfo():
    """
    Utiliza esta herramienta cuando el usuario pregunte sobre antologías (2022, 2023, etc.), 
    recopilación de obras, o la Biblioteca Interactiva Digital.
    """
    return platform_service.get_anthologies_info()
