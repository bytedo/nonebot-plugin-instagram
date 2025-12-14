from pydantic import BaseModel
from typing import Optional

class Config(BaseModel):
    # RapidAPI Key
    instagram_rapidapi_key: Optional[str] = None
    # RapidAPI Host
    instagram_rapidapi_host: str = "instagram-looter2.p.rapidapi.com"
    # 代理
    instagram_proxy: Optional[str] = None