from pydantic import BaseModel  

class MsgReqValidations(BaseModel):    
    userId: str
    sessionId: str
    msg: str
