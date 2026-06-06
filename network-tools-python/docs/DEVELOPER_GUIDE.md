# 开发者说明

## 模块职责

- `main.py`：命令行参数解析和统一入口。
- `gui.py`：Tkinter 图形界面。
- `ping.py`：系统 Ping 调用和多语言输出解析。
- `dns_check.py`：DNS 地址解析。
- `port_scan.py`：端口格式解析和 TCP 扫描。
- `scan.py`：局域网与批量目标检测。
- `ip_lookup.py`：公网 IP 和 IP 归属地查询。
- `speed_test.py`：测速及标准库降级方案。
- `report.py`：结构化报告和多格式导出。
- `version.py`：软件身份与版本信息。

## 设计原则

- 优先使用 Python 标准库。
- 网络错误转换为可读结果，不直接终止程序。
- 文件路径从参数或当前项目目录获取，不写死绝对路径。
- GUI 网络任务在线程中执行，Tkinter 控件只在主线程更新。

## 本地检查

```bash
python -m py_compile main.py gui.py ping.py dns_check.py port_scan.py
python main.py --help
python main.py ping 127.0.0.1
python main.py dns localhost
```

## 扩展建议

- 添加自动化测试目录。
- 使用 PyInstaller 构建 Windows EXE。
- 增加检测历史和图表。
- 增加 Traceroute、路由表和网卡信息。
