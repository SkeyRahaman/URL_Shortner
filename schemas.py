from pydantic import BaseModel

class UserDetailsUpdatable(BaseModel):
    email : str = None
    password : str = None

class UserDetails(UserDetailsUpdatable):
    user_name : str
    

class UrlData(BaseModel):
    long_url :str
    description :str

class UrlDisplay(UrlData):
    short_url :str