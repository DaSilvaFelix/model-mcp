from src.configs.ai.llm import initModel
from src.tools.main import mainTools
from src.validations.msgReqValidations import MsgReqValidations
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from src.prompts.instructions import sysMsg
from rich import print

class AgentService():

    def __init__(self):
        self.model = initModel()
        self.tools = {t.name: t for t in mainTools}
    
    async def chat(self, body:MsgReqValidations, memory):
        messages =  memory + [HumanMessage(content=body.msg)] + [SystemMessage(content=sysMsg)]
        config = {"configurable": {"userId": body.userId, "sessionId": body.sessionId}}
        
        response = await self.model.ainvoke(messages, config=config)
        
        while response.tool_calls:
            messages.append(response)
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                print(f"\n herramienta utilizada:{tool_name}\n")
                tool_args = tool_call["args"]
                print(f"\n argumentos de la herramienta:{tool_args}\n")
                tool_result = self.tools[tool_name].invoke(tool_args, config=config)
                print(f"\n resultado de la herramienta:{tool_result}\n")
                messages.append(ToolMessage(tool_call_id=tool_call["id"], content=str(tool_result)))
            
            response = await self.model.ainvoke(messages, config=config)
        return response
