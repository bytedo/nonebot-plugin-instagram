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
    type="application",
    homepage="https://github.com/bytedo/nonebot-plugin-instagram", 
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={
        "author": "bytedo", 
        "version": "0.3.0",
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
        # 仅在解析失败时提示
        await bot.send(event, f"Ins解析失败: {data.get('text')}")
        return

    caption = data.get("caption", "")
    if caption:
        await bot.send(event, caption)
    else:
        await bot.send(event, "Instagram Share")

    # 2. 下载所有媒体资源
    # 先将资源下载到内存中，方便后续根据数量决定发送方式
    items = data.get("items", [])
    media_resources = [] # 格式:List[(type, bytes)]

    for item in items:
        media_url = item.get("url")
        media_type = item.get("type")
        
        file_bytes = await download_media(media_url)
        if file_bytes:
            media_resources.append((media_type, file_bytes))

    if not media_resources:
        await bot.send(event, "媒体文件下载失败或为空。")
        return

    count = len(media_resources)

    # 资源超过3个合并转发
    if count > 3:
        nodes = []
        for m_type, m_bytes in media_resources:
            content = MessageSegment.video(m_bytes) if m_type == "video" else MessageSegment.image(m_bytes)
            # 构建自定义节点
            nodes.append(
                MessageSegment.node_custom(
                    user_id=int(bot.self_id),
                    nickname="Instagram",
                    content=content
                )
            )
        
        try:
            if isinstance(event, GroupMessageEvent):
                await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=nodes)
            elif isinstance(event, PrivateMessageEvent):
                await bot.call_api("send_private_forward_msg", user_id=event.user_id, messages=nodes)
        except Exception as e:
            logger.error(f"合并转发失败: {e}")
            await bot.send(event, "合并转发失败，可能是文件过大或被风控。")

    # 资源少于等于3个直接发送
    else:
        msg = Message()
        for m_type, m_bytes in media_resources:
            if m_type == "video":
                msg.append(MessageSegment.video(m_bytes))
            else:
                msg.append(MessageSegment.image(m_bytes))
        
        try:
            await bot.send(event, msg)
        except Exception as e:
            logger.error(f"直接发送失败: {e}")
            await bot.send(event, "发送媒体失败，请查看后台日志。")