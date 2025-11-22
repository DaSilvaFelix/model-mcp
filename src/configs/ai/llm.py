from langchain_google_genai import ChatGoogleGenerativeAI
from src.configs.environment.var import getVar
from src.tools.math import toolList

def initModel():
    gemini = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=getVar("KEY"),
        temperature=0
    )
    # Retorna el modelo con las herramientas ya conectadas
    return gemini.bind_tools(toolList)