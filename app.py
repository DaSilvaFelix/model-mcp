import uvicorn
from src.configs.environment.var import getVar

if(__name__=="__main__"):
	uvicorn.run("src.main:app",port=int(getVar("PORT")),reload=True)