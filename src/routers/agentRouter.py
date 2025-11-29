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
        
        self.router.post("/agent")(self.chatWithAgent)
    
    
    async def chatWithAgent(self, body:MsgReqValidations):
        
        memory = self.memoryService.getMemoryByUserIdAndSessionId(body.userId, body.sessionId,15)
        
        messages = convertMemoryToMessages(memory)
        
        response = await self.agentService.chat(body, messages)
        
        content = response.content
        
        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                elif isinstance(part, str):
                    text_parts.append(part)
            content = "".join(text_parts)
        
        # Si ya es string, usarlo directamente
        elif not isinstance(content, str):
            content = str(content)
        
        self.memoryService.saveMemory(body.userId, body.sessionId, body.msg, content)
        
        print(content)

        return JSONResponse(content={"response":content}, status_code=200)