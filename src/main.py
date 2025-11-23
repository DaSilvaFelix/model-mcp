from fastapi import FastAPI 
from src.configs.database.connection import connect
from rich import print
from src.routers.agentRouter import AgentRouter

app = FastAPI()

app.include_router(AgentRouter().router)

try:
	connect()
	print("\n✅ conexión de la base de datos realizadas correctamente \n")
except Exception as e:
	print(e)