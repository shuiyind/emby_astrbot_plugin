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

    def get_chinese_font(self, font_size):
        import os
        font_file = self.config.get("font_file", "NotoSansSC-Regular.ttf")
        plugin_dir = os.path.dirname(__file__)
        font_path = os.path.join(plugin_dir, font_file)
        if os.path.exists(font_path):
            try:
                from PIL import ImageFont
                return ImageFont.truetype(font_path, font_size)
            except:
                pass
        # 兼容系统字体
        system_fonts = [
            "msyh.ttc", "simhei.ttf", "simsun.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/arphic/ukai.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
        ]
        for path in system_fonts:
            if os.path.exists(path):
                try:
                    from PIL import ImageFont
                    return ImageFont.truetype(path, font_size)
                except:
                    continue
        from PIL import ImageFont
        return ImageFont.load_default()

    def format_image(self, system_info, libraries):
        # 美化图片报告样式，标题加粗、分隔线、表格居中、颜色区分
        import tempfile, os
        width, height = 1280, 1024
        bg_color = (245, 248, 255)
        title_color = (40, 80, 180)
        label_color = (60, 60, 60)
        value_color = (20, 120, 60)
        table_header_bg = (220, 230, 250)
        table_line_color = (200, 200, 200)
        font_size = 32
        font_bold_size = 40
        font = self.get_chinese_font(font_size)
        font_bold = self.get_chinese_font(font_bold_size)
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        y = 50
        # 标题
        title = "Emby 服务器状态报告"
        w_title, h_title = draw.textsize(title, font=font_bold)
        draw.text(((width-w_title)//2, y), title, font=font_bold, fill=title_color)
        y += font_bold_size + 10
        # 分隔线
        draw.line([(80, y), (width-80, y)], fill=table_line_color, width=3)
        y += 20
        # 服务器信息
        info_labels = ["服务器名称：", "版本：", "操作系统："]
        info_values = [str(system_info.get('ServerName', 'N/A')), str(system_info.get('Version', 'N/A')), str(system_info.get('OperatingSystemDisplayName', 'N/A'))]
        for label, value in zip(info_labels, info_values):
            w_label, _ = draw.textsize(label, font=font)
            draw.text((120, y), label, font=font, fill=label_color)
            draw.text((120+w_label+20, y), value, font=font, fill=value_color)
            y += font_size + 8
        y += 10
        # 媒体库统计标题
        stat_title = "媒体库统计"
        w_stat, h_stat = draw.textsize(stat_title, font=font_bold)
        draw.text(((width-w_stat)//2, y), stat_title, font=font_bold, fill=title_color)
        y += font_bold_size + 10
        # 表头背景
        draw.rectangle([(120, y), (width-120, y+font_size+10)], fill=table_header_bg)
        draw.text((140, y), "媒体库名称", font=font, fill=label_color)
        draw.text((540, y), "条目数量", font=font, fill=label_color)
        y += font_size + 18
        # 表格内容
        for lib in libraries:
            draw.text((140, y), str(lib.get('Name', 'N/A')), font=font, fill=value_color)
            draw.text((540, y), str(lib.get('TotalCount', 0)), font=font, fill=value_color)
            y += font_size + 8
            # 分隔线
            draw.line([(130, y), (width-130, y)], fill=table_line_color, width=1)
            y += 2
        # 限制图片大小 < 2MB
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        if buf.tell() > 2 * 1024 * 1024:
            img = img.resize((width//2, height//2))
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
        buf.seek(0)
        # 保存为临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(buf.read())
            tmp_path = tmp.name
        return tmp_path

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
            img_path = self.format_image(system_info, libraries)
            yield event.image_result(img_path)
            # 自动清理临时文件
            import os
            try:
                os.remove(img_path)
            except Exception as e:
                logger.error(f"临时图片文件清理失败: {e}")
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
