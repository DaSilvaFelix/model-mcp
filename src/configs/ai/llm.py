from langchain_google_genai import ChatGoogleGenerativeAI
from src.configs.environment.var import getVar
from src.tools.main import mainTools

def initModel():
    gemini = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=getVar("KEY"),
        temperature=0.7,
        
    )
    return gemini.bind_tools(mainTools)