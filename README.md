# Emby AstrBot 插件

## 简介

本插件用于在 AstrBot 聊天机器人平台中查询 Emby 服务器状态和媒体库信息，支持 Markdown 和图片（1280x1024，自动压缩至2MB以内）两种输出方式。

- 支持通过指令获取 Emby 服务器名称、版本、操作系统等信息。
- 支持统计各媒体库的内容数量。
- 支持将报告以 Markdown 或图片格式输出。
- 插件配置可在 AstrBot 管理面板中可视化设置。

## 安装方法

1. 将本插件目录（emby_astrbot_plugin）放入 AstrBot 的 `data/plugins` 目录下。
2. 在 AstrBot 管理面板中启用插件，并填写 Emby 服务器地址、API 密钥和输出方式。
3. 安装依赖（AstrBot 会自动安装 requirements.txt 中的依赖）。

## 配置说明

插件支持以下配置项（可在管理面板可视化设置）：
- `url`：Emby 服务器地址（如 http://your-emby-server:8096）
- `api_key`：Emby API 密钥
- `output_type`：输出方式，可选 `markdown` 或 `image`


## 使用方法

插件支持两种触发方式：

1. 指令触发（如 `/emby_report`、`/emby`、`/emby状态`）。
2. 自动问题句式触发：只要在聊天中完整出现以下问题句式之一，插件会自动回复 Emby 信息。

自动触发支持的问题句式示例：
 - 我的 emby 服务器状态
 - emby 影视库有多少内容
 - emby 现在有多少电影
 - emby 现在有多少电视剧
 - emby 媒体库统计
 - emby 服务器信息
 - emby 统计
 - emby 有多少音乐
 - 查询 emby 媒体库

根据配置，报告将以 Markdown 或图片格式返回。

## 许可证

本插件采用 AGPLv3 开源协议，详情请见 LICENSE 文件。

## 作者

shuiyind

GitHub: https://github.com/shuiyind/emby_astrbot_plugin
