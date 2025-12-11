from pydantic import BaseModel
from typing import Optional

class Config(BaseModel):
    # RapidAPI Key (必填)
    instagram_rapidapi_key: str = ""
    
    # RapidAPI Host (默认为 instagram-looter2)
    instagram_rapidapi_host: str = "instagram-looter2.p.rapidapi.com"
    
    # 代理设置 (可选，通常 RapidAPI 不需要国内代理，除非你本地网络特殊)
    instagram_proxy: Optional[str] = None 

plugin_config = Config()