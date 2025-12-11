import re
from nonebot import on_command, on_regex, logger
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg, RegexStr
from nonebot.exception import FinishedException
from .config import Config

# 引入 OneBot V11 特有的事件和类
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
    MessageSegment
)

# 导入工具函数
from .utils import get_instagram_content, download_media

__plugin_meta__ = PluginMetadata(
    name="Instagram RapidAPI 解析",
    description="基于 RapidAPI 的 Instagram 图文/视频解析插件 (支持合并转发)",
    usage="发送 ins <链接> 或直接发送包含 instagram.com 的链接",
    type="application",  # 类型：application (应用) 或 library (库)
    homepage="https://github.com/bytedo/nonebot-plugin-instagram",
    config=Config,
    supported_adapters={"~onebot.v11"},
    
    extra={
        "author": "bytedo",
        "version": "0.1.0",
    }
)

ins_cmd = on_command("ins", aliases={"instagram"}, priority=5, block=True)
ins_regex = on_regex(
    r"(https?:\/\/(?:www\.)?instagram\.com\/(?:p|reel|stories)\/[\w\-]+\/?)", 
    priority=10, 
    block=False 
)

@ins_cmd.handle()
async def handle_cmd(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    url = args.extract_plain_text().strip()
    if url:
        await process_request(bot, event, url)

@ins_regex.handle()
async def handle_regex(bot: Bot, event: MessageEvent, url_match: str = RegexStr()):
    match = re.search(r"(https?:\/\/(?:www\.)?instagram\.com\/(?:p|reel|stories)\/[\w\-]+\/?)", url_match)
    if match:
        await process_request(bot, event, match.group(1))

async def process_request(bot: Bot, event: MessageEvent, url: str):
    # 1. 获取帖子信息
    data = await get_instagram_content(url)
    
    if data.get("status") == "error":
        # 仅在解析失败时提示，其他情况静默
        await bot.send(event, f"Ins解析失败: {data.get('text')}")
        return

    # 2. 构建合并转发节点
    nodes = []
    
    # -- 添加文案 --
    caption = data.get("caption", "Instagram Share")
    # 截断过长文案
    if len(caption) > 100:
        display_caption = caption[:100] + "..."
    else:
        display_caption = caption

    nodes.append(
        MessageSegment.node_custom(
            user_id=int(bot.self_id),
            nickname="Instagram",
            content=display_caption
        )
    )

    # -- 下载并添加媒体 --
    items = data.get("items", [])
    

    for item in items:
        media_url = item.get("url")
        media_type = item.get("type")
        
        # 下载二进制数据
        file_bytes = await download_media(media_url)
        
        if not file_bytes:
            continue 

        content = None
        if media_type == "video":
            content = MessageSegment.video(file_bytes)
        else:
            content = MessageSegment.image(file_bytes)
        
        if content:
            nodes.append(
                MessageSegment.node_custom(
                    user_id=int(bot.self_id),
                    nickname="Instagram",
                    content=content
                )
            )

    if len(nodes) <= 1:
        # 只有文案节点，说明媒体全挂了
        await bot.send(event, "媒体下载失败或为空，无法发送。")
        return

    # 3. 发送合并消息
    try:
        if isinstance(event, GroupMessageEvent):
            await bot.call_api(
                "send_group_forward_msg",
                group_id=event.group_id,
                messages=nodes
            )
        elif isinstance(event, PrivateMessageEvent):
            await bot.call_api(
                "send_private_forward_msg",
                user_id=event.user_id,
                messages=nodes
            )
    except FinishedException:
        pass
    except Exception as e:
        logger.error(f"合并转发发送失败: {e}")
        # 静默失败，或者你可以选择打印个简单的Log，不打扰用户