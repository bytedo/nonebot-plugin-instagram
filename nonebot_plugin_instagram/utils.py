import httpx
from nonebot import get_plugin_config, logger
from .config import Config

conf = get_plugin_config(Config)

async def get_instagram_content(url: str) -> dict:
    """
    请求 RapidAPI 获取 Ins 帖子信息 (文案+媒体链接)
    """
    if not conf.instagram_rapidapi_key:
        return {"status": "error", "text": "未配置 RAPIDAPI_KEY"}

    api_url = f"https://{conf.instagram_rapidapi_host}/post"
    querystring = {"url": url}
    headers = {
        "x-rapidapi-key": conf.instagram_rapidapi_key,
        "x-rapidapi-host": conf.instagram_rapidapi_host
    }
    
    current_proxy = conf.instagram_proxy

    async with httpx.AsyncClient(proxy=current_proxy, timeout=60.0) as client:
        try:
            resp = await client.get(api_url, headers=headers, params=querystring)
            if resp.status_code != 200:
                return {"status": "error", "text": f"API Error {resp.status_code}"}
            
            return _parse_response(resp.json())
        except Exception as e:
            return {"status": "error", "text": str(e)}

async def download_media(url: str) -> bytes | None:
    """
    下载媒体文件为二进制数据 (bytes)
    """
    current_proxy = conf.instagram_proxy
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Referer": "https://www.instagram.com/" 
    }

    logger.debug(f"正在下载资源: {url}")

    async with httpx.AsyncClient(proxy=current_proxy, timeout=120.0, verify=False) as client:
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.content
            else:
                logger.error(f"下载失败 {resp.status_code}: {url}")
                return None
        except Exception as e:
            logger.error(f"下载异常: {e}")
            return None

def _parse_response(data: dict) -> dict:
    """
    解析 API 返回，提取 文案 + 媒体
    """
    logger.debug(f"RapidAPI Raw: {data}")

    caption = ""
    try:
        if "caption" in data and data["caption"]:
            caption = data["caption"]
        elif "edge_media_to_caption" in data:
            edges = data["edge_media_to_caption"].get("edges", [])
            if edges:
                caption = edges[0].get("node", {}).get("text", "")
    except Exception:
        pass

    result = {
        "status": "success",
        "caption": caption,
        "items": [] 
    }

    try:
        if "edge_sidecar_to_children" in data:
            edges = data["edge_sidecar_to_children"].get("edges", [])
            for edge in edges:
                node = edge.get("node", {})
                if node.get("is_video"):
                    result["items"].append({"type": "video", "url": node.get("video_url")})
                else:
                    result["items"].append({"type": "image", "url": node.get("display_url")})
            return result

        if data.get("video_url"):
            result["items"].append({"type": "video", "url": data["video_url"]})
            return result
        
        if data.get("display_url"):
            result["items"].append({"type": "image", "url": data["display_url"]})
            return result

        return {"status": "error", "text": "未找到媒体链接"}

    except Exception as e:
        return {"status": "error", "text": f"解析异常: {e}"}