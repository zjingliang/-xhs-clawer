# xhs-crawler

小红书关键词搜索爬虫工具，带图形界面。通过浏览器抓包获取鉴权信息后，调用官方 API 爬取搜索结果并导出 CSV。

> **仅供学习与研究使用。** 请遵守小红书用户协议及相关法律法规，不得用于商业用途或大规模采集。使用者需自行承担风险。

## 功能

- **抓包模式**：自动启动 Chrome，监听搜索与帖子详情 API，保存鉴权 Header 与 Cookie
- **爬虫模式**：按关键词分页搜索，获取标题、作者、互动数据、正文、链接等，导出 CSV
- **间隔控制**：每条数据保存后可设置等待时间，降低触发风控的概率
- **日志脱敏**：运行日志不输出完整 URL 或鉴权内容

## 环境要求

- Windows 10/11（已在 Windows 上测试）
- Python 3.8+
- Google Chrome 浏览器

## 安装

```bash
git clone https://github.com/<your-username>/xhs-crawler.git
cd xhs-crawler
pip install -r requirements.txt
```

## 配置

主配置文件：`config/config.json`

| 字段 | 说明 |
|------|------|
| `auth_file` | 鉴权保存路径，默认 `xhs_auth.json` |
| `capture.max_wait_seconds` | 抓包最长等待时间（秒） |
| `capture.site_url` | 抓包时打开的小红书首页 |
| `crawler.default_page_count` | 默认爬取页数 |
| `crawler.default_item_interval` | 默认每条间隔（秒） |
| `crawler.page_size` | 每页条数 |
| `crawler.output_suffix` | CSV 文件名后缀 |

首次使用可复制示例配置：

```bash
copy config\config.example.json config\config.json
```

鉴权文件 `xhs_auth.json` **不会**随仓库提交（已在 `.gitignore` 中排除）。格式参考 `xhs_auth.example.json`，须通过 GUI 抓包模式自动生成，**请勿手动填写真实 token 后上传 GitHub**。

## 使用

```bash
python main.py
```

### 1. 捕获鉴权

1. 点击顶部 **「捕获鉴权」**
2. 在弹出的 Chrome 中登录小红书
3. 搜索任意关键词，并 **点击一条帖子**（用于捕获详情 API 鉴权）
4. 等待提示「鉴权已保存」

须同时捕获：**搜索鉴权**、**帖子详情鉴权**、**Cookie**。

### 2. 开始爬取

1. 切换到 **「爬虫模式」** 标签
2. 输入搜索关键词、页数、每条间隔
3. 点击 **「开始爬取」**
4. 结果保存为 `{关键词}_小红书数据.csv`（位于项目根目录）

## 项目结构

```
xhs-crawler/
├── main.py                 # 程序入口
├── gui/
│   ├── app.py              # tkinter 界面
│   └── theme.py            # DPI 与高 DPI 字体
├── xhs_crawler/
│   ├── capture.py          # 浏览器抓包
│   ├── crawler.py          # 搜索与详情爬取
│   ├── auth.py             # 鉴权读写
│   ├── browser.py          # Chrome 路径检测
│   ├── settings.py         # 配置加载
│   └── utils.py            # 日期转换等工具
├── config/
│   ├── config.json         # 运行配置
│   └── config.example.json # 配置示例
├── xhs_auth.example.json   # 鉴权文件格式示例（占位符，已脱敏）
├── requirements.txt
├── LICENSE                 # MIT License
└── README.md
```

## 输出字段

CSV 包含：发布标题、发布作者、发布时间、发布类型、热力值、点赞量、收藏量、评论数量、分享数量、发布内容、发布链接、图片链接。

## 常见问题

**鉴权不完整 / 搜索请求失败**

重新执行抓包流程，确保已登录、已搜索、已点击帖子。

**发布内容为空**

须捕获帖子详情（feed）鉴权；仅搜索鉴权无法获取正文。

**找不到 Chrome**

请安装 Google Chrome；程序会通过注册表或 PATH 自动查找。

## 免责声明

本项目为开源学习工具，与小红书官方无关。作者不对因使用本工具产生的账号封禁、数据纠纷或法律问题负责。请勿将本工具用于侵犯他人权益或违反平台规则的行为。

## License

[MIT License](LICENSE)
