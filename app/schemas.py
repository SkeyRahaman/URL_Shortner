from pydantic import BaseModel, Field, ConfigDict

class UserDetailsUpdatable(BaseModel):
    email : str = None
    password : str = None

class UserDetails(UserDetailsUpdatable):
    user_name : str

class UserDisplay(BaseModel):
    id :int
    user_name : str
    email : str = None
    model_config = ConfigDict(populate_by_name=True)

class UrlData(BaseModel):
    long_url: str  # Ensures valid URLs
    description: str = Field(max_length=200)  # Limit description length

class UrlDisplay(UrlData):
    id :int
    short_url :str
    model_config = ConfigDict(populate_by_name=True)

class UrlDataUpdate(UrlData):
    short_url: str 