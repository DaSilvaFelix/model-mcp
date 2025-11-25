from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from src.services.users import UserService
from rich import print


user_service = UserService()

@tool(description="Devuelve información del usuario")
def whoIsHeIsUser(config: RunnableConfig) -> str:

    """Devuelve información del usuario actual desde la base de datos."""
    
    configuration = config.get("configurable", {})
    user_id = configuration.get("userId")
    session_id = configuration.get("sessionId")
    
    user, data = user_service.getUserById(user_id)
    print(f"Usuario encontrado: {data}")
    
    if user:
        return f"Usuario: {data}"
    else:
        return f"No se encontró usuario con ID: {user_id}"
    
