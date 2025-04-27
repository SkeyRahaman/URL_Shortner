from pydantic import BaseModel

class UserDetailsUpdatable(BaseModel):
    email : str = None
    password : str = None

class UserDetails(UserDetailsUpdatable):
    user_name : str

class UserDisplay(BaseModel):
    ser_name : str
    email : str = None
    class Config():   #to convert the model to this
        from_attributes = True
    

class UrlData(BaseModel):
    long_url :str
    description :str

class UrlDisplay(UrlData):
    short_url :str
    class Config():   #to convert the model to this
        from_attributes = True