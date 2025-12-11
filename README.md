<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-instagram

_✨ 一个基于 RapidAPI 的 NoneBot2 Instagram 解析插件 ✨_

## 📖 介绍

一个基于 RapidAPI 的 NoneBot2 Instagram 解析插件，可以在群聊和私聊解析 instagram 链接发送相关图片或视频。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-instagram

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-instagram
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-instagram
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-instagram
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-instagram
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot-plugin-instagram"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| INSTAGRAM_RAPIDAPI_KEY | 是 | 无 | RapidAPI Key |
| INSTAGRAM_RAPIDAPI_HOST | 否 | instagram-looter2.p.rapidapi.com | 如果 API Host 不是 looter2，可以修改 |

### 获取 rapidapi 

注册账号：https://rapidapi.com/auth/sign-up

搜索"Instagram"，找到Instagram Looter，点击右侧"Subscribe to test"，选择"Start Free Plan" - "Subscribe"

部署后记录下"x-rapidapi-key"，填入`INSTAGRAM_RAPIDAPI_KEY`配置。

## 🎉 使用

在群里或者私聊发送 instagram 链接

