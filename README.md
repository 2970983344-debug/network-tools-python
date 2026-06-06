# 🌐 Network Tools Python v1.0

> 一款面向网络运维、学习实践与故障排查的 Python 网络工具箱。  
> A Python network operations toolkit for diagnostics, learning, and troubleshooting.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?logo=windows)](https://www.microsoft.com/windows)
[![Version](https://img.shields.io/badge/Release-v1.0-16805B)](CHANGELOG.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 项目简介 | Introduction

**Network Tools Python v1.0** 是一个轻量级 Python 网络运维工具箱，同时提供 Tkinter GUI 图形界面和命令行 CLI。项目覆盖常见网络检测场景，包括 Ping、DNS、端口扫描、IP 归属地查询、网络测速、批量检测与报告导出。

**Network Tools Python v1.0** is a lightweight network operations toolkit with both a Tkinter desktop GUI and a command-line interface. It covers common diagnostic tasks such as Ping, DNS resolution, TCP port scanning, IP geolocation, speed testing, batch checks, and report export.

项目优先使用 Python 标准库，不需要数据库，也不会在代码中保存 API Key。可选的 `speedtest-cli` 不可用时，程序会自动使用标准库降级测速。

The project prioritizes the Python standard library, requires no database, and stores no API keys. If the optional `speedtest-cli` dependency is unavailable, a standard-library fallback is used automatically.

## ✨ 功能特性 | Features

- 🖥️ **GUI 图形界面 / Desktop GUI**  
  使用 Tkinter 提供统一的桌面操作界面。

- 📡 **Ping 检测 / Ping Check**  
  显示连通状态、丢包率和平均延迟，兼容中文及英文 Windows 输出。

- 🔎 **DNS 解析 / DNS Resolution**  
  查询目标域名的 IPv4、IPv6 地址和解析耗时。

- 🔌 **端口扫描 / Port Scan**  
  支持单端口、逗号分隔端口和端口范围，如 `80,443,8000-8010`。

- 🌍 **IP 归属地查询 / IP Geolocation**  
  查询本机公网 IP，或查询指定 IP 的国家、地区、城市及运营商。

- 🚀 **网络测速 / Network Speed Test**  
  测试网络延迟与下载速度，并提供无第三方依赖的降级方案。

- 📄 **HTML 报告导出 / HTML Report Export**  
  支持 HTML、TXT、CSV 和 Markdown 格式。

- 📚 **批量检测 / Batch Check**  
  从 `targets.txt` 读取多个 IP 或域名，批量执行 Ping 和可选端口扫描。

- 🛡️ **异常处理 / Error Handling**  
  对空输入、地址错误、端口错误、请求失败、权限不足和依赖缺失提供明确提示。

## 🧰 技术栈 | Tech Stack

| 技术 / Technology | 用途 / Purpose |
| --- | --- |
| Python 3.10+ | 核心开发语言 / Core language |
| Tkinter + ttk | GUI 图形界面 / Desktop interface |
| socket | DNS 与 TCP 连接 / DNS and TCP connections |
| subprocess | 系统 Ping 调用 / System Ping execution |
| urllib | IP 查询与降级测速 / HTTP requests and fallback speed test |
| concurrent.futures | 并发扫描 / Concurrent scanning |
| csv + html | 多格式报告导出 / Report export |
| speedtest-cli | 可选完整测速 / Optional full speed test |

## 📁 项目结构 | Project Structure

```text
network-tools-python/
├── main.py                  # CLI 统一入口 / CLI entry point
├── gui.py                   # Tkinter 图形界面 / Desktop GUI
├── ping.py                  # Ping 检测与多语言解析
├── dns_check.py             # DNS 解析
├── port_scan.py             # TCP 端口扫描
├── ip_lookup.py             # 公网 IP 与归属地查询
├── speed_test.py            # 网络测速与降级方案
├── scan.py                  # 局域网与批量检测
├── report.py                # 多格式报告导出
├── version.py               # 软件版本信息
├── targets.txt              # 批量检测目标示例
├── requirements.txt         # 可选依赖
├── CHANGELOG.md             # 更新日志
├── LICENSE                  # MIT License
├── screenshots/
│   ├── home.png
│   ├── ping.png
│   ├── scan.png
│   └── README.md
└── docs/
    ├── USER_GUIDE.md
    ├── DEVELOPER_GUIDE.md
    └── SOFTWARE_COPYRIGHT.md
```

## 📦 安装方法 | Installation

### 1. 获取项目 | Clone

```bash
git clone https://github.com/your-username/network-tools-python.git
cd network-tools-python
```

### 2. 创建虚拟环境 | Create a Virtual Environment

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD：

```bat
.venv\Scripts\activate.bat
```

### 3. 安装依赖 | Install Dependencies

```bash
pip install -r requirements.txt
```

> `speedtest-cli` 为可选依赖。安装失败时，除完整测速外的其他功能仍可正常使用。  
> `speedtest-cli` is optional. Other features remain available if installation fails.

## ▶️ 运行方式 | Running

启动 GUI：

```bash
python main.py gui
```

直接启动 GUI：

```bash
python gui.py
```

查看 CLI 帮助：

```bash
python main.py --help
python main.py --version
```

## 🖥️ GUI 使用说明 | GUI Guide

1. 在“目标 IP / 域名”输入框填写目标，例如 `baidu.com` 或 `8.8.8.8`。
2. 在端口输入框填写 `80,443,3306` 或 `8000-8010`。
3. 点击 Ping、端口扫描、DNS 解析、IP 查询或网络测速。
4. 检测结果会显示在下方结果区域。
5. 点击“报告导出”保存 HTML、TXT、CSV 或 Markdown 报告。
6. 点击“清空结果”清除当前检测内容。

1. Enter a target such as `baidu.com` or `8.8.8.8`.
2. Enter ports such as `80,443,3306` or `8000-8010`.
3. Select a diagnostic action.
4. Review results in the output panel.
5. Export the current results as HTML, TXT, CSV, or Markdown.

## ⌨️ 命令行使用说明 | CLI Guide

### Ping 检测

```bash
python main.py ping baidu.com
python main.py ping baidu.com --count 6 --timeout 2
```

### DNS 解析

```bash
python main.py dns baidu.com
```

### 端口扫描

```bash
python main.py ports baidu.com --ports 80,443,3306
python main.py ports 127.0.0.1 --ports 20-25,80,443
```

### IP 查询

```bash
# 查询本机公网 IP / Query current public IP
python main.py ip

# 查询指定 IP / Query a specified IP
python main.py ip 8.8.8.8
```

### 网络测速

```bash
python main.py speed

# 强制使用标准库降级方案
python main.py speed --fallback
```

### 批量检测

```bash
python main.py batch targets.txt
python main.py batch targets.txt --scan-ports --ports 80,443
```

### 生成诊断报告

```bash
python main.py report baidu.com --output network_report.html
python main.py report baidu.com --output network_report.csv
python main.py report baidu.com --output network_report.txt
```

## 📸 项目截图展示 | Screenshots

### GUI 主界面 | GUI Home

![GUI Home](screenshots/home.png)

### Ping 检测 | Ping Check

![Ping Check](screenshots/ping.png)

### 端口扫描 | Port Scan

![Port Scan](screenshots/scan.png)

> 更多截图可以添加到 `screenshots/`。  
> Additional screenshots can be added to `screenshots/`.

## 📄 HTML 报告展示 | HTML Report

生成 HTML 报告：

```bash
python main.py report baidu.com --output network_report.html
```

HTML 报告包含检测时间、检测目标、检测类型、检测结果和状态说明。

The HTML report includes the check time, target, check type, result, and status.

<!-- 将实际 HTML 报告截图保存为 screenshots/report-html.png 后取消下面一行的注释 -->
<!-- ![HTML Report](screenshots/report-html.png) -->

> 🖼️ **展示占位符 / Screenshot Placeholder:**  
> `screenshots/report-html.png`

## 🏷️ Release v1.0

首个公开版本包含完整的 GUI 和 CLI 工作流：

- Ping、DNS 和 TCP 端口扫描
- IP 归属地查询
- 网络测速与自动降级
- 局域网和批量目标检测
- HTML、TXT、CSV、Markdown 报告导出
- 中文/英文 Windows Ping 输出兼容
- 完整异常处理、使用文档和软件版本信息

The first public release delivers the complete GUI and CLI workflow, multilingual Windows Ping parsing, batch diagnostics, IP lookup, speed testing, and multi-format report export.

完整记录见 [CHANGELOG.md](CHANGELOG.md)。

## 🗺️ 未来规划 | Roadmap

- [ ] 使用 PyInstaller 发布 Windows EXE
- [ ] 增加检测历史记录
- [ ] 增加实时延迟与速度图表
- [ ] 增加 Traceroute 和路由分析
- [ ] 增加网卡、网关和本机网络信息
- [ ] 增加任务进度条和取消操作
- [ ] 增加自动化测试与 GitHub Actions
- [ ] 提供英文 GUI 语言选项

## 📜 许可证 | License

本项目基于 [MIT License](LICENSE) 开源。

This project is licensed under the [MIT License](LICENSE).

## 👤 作者信息 | Author

- **作者 / Author:** Simpson Liao
- **软件名称 / Software:** 网络运维工具箱软件
- **英文名称 / English Name:** Network Tools Python
- **版本 / Version:** v1.0
- **适用系统 / Platform:** Windows 10/11

欢迎提交 Issue、Pull Request 或改进建议。  
Issues, pull requests, and improvement suggestions are welcome.
