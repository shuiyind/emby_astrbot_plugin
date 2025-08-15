from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig
import aiohttp
import jinja2
from PIL import Image, ImageDraw, ImageFont
import io

@register("emby_reporter", "shuiyind", "Emby 信息查询与报告插件，支持 Markdown 和图片输出", "1.0.0", "https://github.com/shuiyind/emby")
class EmbyReporterPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.jinja_env = jinja2.Environment()

    async def fetch_emby_data(self, base_url, api_key):
        headers = {
            'X-Emby-Token': api_key,
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{base_url}/System/Info", headers=headers, ssl=False) as resp:
                    system_info = await resp.json()
                async with session.get(f"{base_url}/Library/VirtualFolders", headers=headers, ssl=False) as resp:
                    raw_libraries = await resp.json()
                libraries = []
                for lib in raw_libraries:
                    items_url = f"{base_url}/Items?ParentId={lib.get('ItemId')}&Recursive=true&IncludeItemTypes=Movie,Series,MusicAlbum&Fields=ParentId"
                    async with session.get(items_url, headers=headers, ssl=False) as resp:
                        items = await resp.json()
                    libraries.append({
                        "Name": lib.get("Name"),
                        "TotalCount": items.get("TotalRecordCount", 0)
                    })
                return system_info, libraries
            except Exception as e:
                logger.error(f"Emby API error: {e}")
                return None, None

    def format_markdown(self, system_info, libraries):
        # Telegram MarkdownV2 语法，中文标题，表格用代码块包裹
        if not system_info or not libraries:
            return "```\n错误：无法获取 Emby 数据。\n```"
        md = "```\n"
        md += "【Emby 服务器状态】\n"
        md += f"服务器名称：{system_info.get('ServerName', 'N/A')}\n"
        md += f"版本：{system_info.get('Version', 'N/A')}\n"
        md += f"操作系统：{system_info.get('OperatingSystemDisplayName', 'N/A')}\n\n"
        md += "【媒体库统计】\n"
        md += f"{'媒体库名称':<18}| {'条目数量':<10}\n"
        md += f"{'-'*18}|{'-'*10}\n"
        for lib in libraries:
            name = lib.get('Name', 'N/A')
            count = lib.get('TotalCount', 0)
            md += f"{name:<18}| {str(count):<10}\n"
        md += "```"
        return md

    def format_image(self, system_info, libraries):
        # 生成 1280x1024 的图片，内容为报告（中文标题）
        width, height = 1280, 1024
        bg_color = (255, 255, 255)
        font_color = (0, 0, 0)
        font_size = 32
        font_path = None
        try:
            font_path = "arial.ttf"
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        y = 40
        lines = [
            "【Emby 服务器状态】",
            f"服务器名称：{system_info.get('ServerName', 'N/A')}",
            f"版本：{system_info.get('Version', 'N/A')}",
            f"操作系统：{system_info.get('OperatingSystemDisplayName', 'N/A')}",
            "",
            "【媒体库统计】",
            f"{'媒体库名称':<18}| {'条目数量':<10}",
            f"{'-'*18}|{'-'*10}"
        ]
        for lib in libraries:
            name = lib.get('Name', 'N/A')
            count = lib.get('TotalCount', 0)
            lines.append(f"{name:<18}| {str(count):<10}")
        for line in lines:
            draw.text((40, y), line, font=font, fill=font_color)
            y += font_size + 10
        # 限制图片大小 < 2MB
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        if buf.tell() > 2 * 1024 * 1024:
            img = img.resize((width//2, height//2))
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
        buf.seek(0)
        return buf

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def auto_emby_report(self, event: AstrMessageEvent):
        """自动检测问题句式并触发 Emby 信息查询"""
        msg = event.message_str.strip()
        trigger_phrases = [
            "我的 emby 服务器状态",
            "emby 影视库有多少内容",
            "emby 现在有多少电影",
            "emby 现在有多少电视剧",
            "emby 媒体库统计",
            "emby 服务器信息",
            "emby 统计",
            "emby 有多少音乐",
            "查询 emby 媒体库"
        ]
        if not any(phrase in msg for phrase in trigger_phrases):
            return
        url = self.config.get("url", "")
        api_key = self.config.get("api_key", "")
        output_type = self.config.get("output_type", "markdown")
        if not url or not api_key:
            yield event.plain_result("请先在插件配置中填写 Emby 服务器地址和 API 密钥！")
            return
        system_info, libraries = await self.fetch_emby_data(url, api_key)
        if output_type == "image":
            buf = self.format_image(system_info, libraries)
            yield event.image_result(buf)
        else:
            md = self.format_markdown(system_info, libraries)
            yield event.plain_result(md)

    @filter.command("emby_report", alias={"emby", "emby状态", "emby统计", "emby服务器", "embyreport", "emby_report", "embyinfo", "emby_info"})
    async def cmd_emby_report(self, event: AstrMessageEvent):
        """指令触发 Emby 信息查询，支持多种表达"""
        url = self.config.get("url", "")
        api_key = self.config.get("api_key", "")
        output_type = self.config.get("output_type", "markdown")
        if not url or not api_key:
            yield event.plain_result("请先在插件配置中填写 Emby 服务器地址和 API 密钥！")
            return
        system_info, libraries = await self.fetch_emby_data(url, api_key)
        if output_type == "image":
            buf = self.format_image(system_info, libraries)
            yield event.image_result(buf)
        else:
            md = self.format_markdown(system_info, libraries)
            yield event.plain_result(md)
