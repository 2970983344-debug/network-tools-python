# Network Tools Python v2.0

一个面向 Windows 10/11 的轻量级网络运维工具集，使用 Python 标准库实现，不依赖第三方包。

## 功能

- Ping 检测
- 端口扫描
- 局域网设备扫描
- DNS 检测
- 网络诊断报告生成

## 项目结构

```text
network-tools-python
├── main.py
├── ping.py
├── port_scan.py
├── scan.py
├── dns_check.py
├── report.py
├── README.md
├── requirements.txt
└── .gitignore
```

项目中也保留了 `screenshots/` 目录，用于保存运行截图和截图说明。

## 环境要求

- Windows 10/11
- Python 3.10+
- 无第三方依赖

安装依赖：

```bash
pip install -r requirements.txt
```

`requirements.txt` 当前仅说明项目使用标准库，因此不会安装额外包。

## 使用方法

所有功能都通过 `main.py` 调用。

### Ping 检测

```bash
python main.py ping baidu.com
```

指定次数和超时时间：

```bash
python main.py ping baidu.com --count 6 --timeout 2
```

说明：

- Windows 下调用系统 `ping` 命令。
- 已兼容中文 / 英文 Windows 输出。
- 如果无法解析平均延迟，会显示 `unknown`。

### 端口扫描

默认检测 `80,443,3306`：

```bash
python main.py ports baidu.com
```

自定义端口：

```bash
python main.py ports 127.0.0.1 --ports 22,80,443,3306
```

### 局域网设备扫描

```bash
python main.py scan 192.168.1.0/24
```

指定探测端口：

```bash
python main.py scan 192.168.1.0/24 --ports 80,443,8080
```

说明：

- 局域网扫描通过 TCP 端口连接判断设备是否可能在线。
- 默认最多扫描 256 个地址，可通过 `--limit` 调整。

### DNS 检测

```bash
python main.py dns baidu.com
```

指定超时时间：

```bash
python main.py dns baidu.com --timeout 3
```

### 生成网络诊断报告

```bash
python main.py report baidu.com --output network_report.md
```

带局域网扫描：

```bash
python main.py report baidu.com --subnet 192.168.1.0/24 --output network_report.md
```

跳过局域网扫描：

```bash
python main.py report baidu.com --no-scan --output network_report.md
```

报告内容包括：

- Ping 状态
- DNS 解析结果
- 端口开放状态
- 可选的局域网设备扫描结果

## 截图说明

截图说明已生成到：

```text
screenshots/README.md
```

建议保存以下截图：

- Ping 检测结果
- 端口扫描结果
- DNS 检测结果
- 局域网扫描结果
- 报告生成结果

## 注意事项

- 请只扫描自己拥有或被授权的网络。
- 端口扫描和局域网扫描可能被防火墙拦截，显示关闭或超时不一定代表主机不存在。
- Ping 检测依赖系统 `ping` 命令，某些网络会禁止 ICMP。
