from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.validations.msgReqValidations import MsgReqValidations
from rich import print  
from src.services.memory import MemoryService
from src.services.agent import AgentService
from src.utils.memory import convertMemoryToMessages

class AgentRouter():

    memoryService = MemoryService()
    agentService = AgentService()
    

    def __init__(self):
        self.router = APIRouter()
        self.router.post("/agent")(self.getAgentById)
    
    
    async def getAgentById(self, body:MsgReqValidations):
        
        memory = self.memoryService.getMemoryByUserIdAndSessionId(body.userId, body.sessionId,10)
        
        messages = convertMemoryToMessages(memory)
        
        response = await self.agentService.chat(body, messages)
        
        self.memoryService.saveMemory(body.userId, body.sessionId, body.msg, response.content)
        
        print(response.content)

        return JSONResponse(content={"response":response.content}, status_code=200)