## 指令触发说明

插件支持多种指令触发方式，常用指令如下：

# emby_astrbot_plugin

Emby 信息查询与报告插件，支持 Markdown 和图片输出，自动触发，Telegram 兼容，字体可配置，美化图片，自动清理临时文件。

## 功能简介

- 支持 Emby 服务器状态、媒体库统计查询
- 支持 Markdown 和图片报告输出
- 自动检测问题句式触发 emby 查询
- 多别名指令注册
- 中文报告，Telegram MarkdownV2 兼容
- 字体可配置，自动检测本地/系统字体
- 图片报告美化（标题加粗、分隔线、表格居中、颜色区分）
- 自动清理临时图片文件

## 安装方法

1. 在 AstrBot 管理面板插件市场搜索 `emby_astrbot_plugin`，一键安装。
2. 或手动下载本仓库，放入 AstrBot 插件目录。

## 依赖

插件自动安装依赖，无需手动操作。

## 配置示例

```json
{
	"url": "http://你的emby地址:8096",
	"api_key": "你的Emby API密钥",
	"output_type": "image", // 可选 markdown 或 image
	"font_file": "NotoSansSC-Regular.ttf" // 可选，支持自定义字体
}
```

## 指令与自动触发

- 指令触发：`/emby_report` 或 `/emby` 等多种别名
- 自动触发：发送完整问题句式自动响应 emby 状态/统计

## 图片报告美化

- emby 风格黑绿渐变背景，标题加粗，表格居中，颜色区分
- 支持自定义字体，中文无方块字

## 兼容性

- 支持 AstrBot 最新版本，Telegram MarkdownV2

## 开源协议

AGPLv3
 - emby 有多少音乐
 - 查询 emby 媒体库

根据配置，报告将以 Markdown 或图片格式返回。

## 许可证

本插件采用 AGPLv3 开源协议，详情请见 LICENSE 文件。

## 作者

shuiyind

GitHub: https://github.com/shuiyind/emby_astrbot_plugin
