"""Tkinter desktop interface for the network operations toolbox."""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from dns_check import check_dns
from ip_lookup import lookup_ip
from ping import ping_host
from port_scan import parse_port_spec, scan_ports
from report import create_entry, export_report
from speed_test import run_speed_test
from version import AUTHOR, VERSION, version_text


class NetworkToolsGUI:
    """Desktop GUI that runs network tasks outside Tkinter's UI thread."""

    def __init__(self, root):
        self.root = root
        self.root.title(version_text())
        self.root.geometry("920x650")
        self.root.minsize(760, 560)
        self.last_entries = []
        self._build_styles()
        self._build_ui()

    def _build_styles(self):
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 18, "bold"))
        style.configure("Sub.TLabel", foreground="#5d6878")
        style.configure("Action.TButton", padding=(12, 8))

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="网络运维工具箱软件", style="Title.TLabel").pack(
            anchor=tk.W
        )
        ttk.Label(
            container,
            text=f"{VERSION}  |  Ping、端口、DNS、IP 归属地、测速与报告导出",
            style="Sub.TLabel",
        ).pack(anchor=tk.W, pady=(4, 16))

        form = ttk.LabelFrame(container, text="检测参数", padding=14)
        form.pack(fill=tk.X)
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="目标 IP / 域名").grid(row=0, column=0, sticky=tk.W)
        self.target_var = tk.StringVar(value="baidu.com")
        ttk.Entry(form, textvariable=self.target_var).grid(
            row=0, column=1, sticky=tk.EW, padx=(12, 0)
        )

        ttk.Label(form, text="端口 / 范围").grid(
            row=1, column=0, sticky=tk.W, pady=(12, 0)
        )
        self.ports_var = tk.StringVar(value="80,443,3306")
        ttk.Entry(form, textvariable=self.ports_var).grid(
            row=1, column=1, sticky=tk.EW, padx=(12, 0), pady=(12, 0)
        )

        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=14)
        buttons = [
            ("Ping 检测", self.run_ping),
            ("端口扫描", self.run_ports),
            ("DNS 解析", self.run_dns),
            ("IP 查询", self.run_ip_lookup),
            ("网络测速", self.run_speed),
            ("报告导出", self.export_current_report),
            ("清空结果", self.clear_results),
        ]
        for index, (label, command) in enumerate(buttons):
            ttk.Button(
                actions, text=label, command=command, style="Action.TButton"
            ).grid(row=index // 4, column=index % 4, padx=(0, 10), pady=(0, 10), sticky=tk.EW)
        for column in range(4):
            actions.columnconfigure(column, weight=1)

        output_frame = ttk.LabelFrame(container, text="检测结果", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        self.output = tk.Text(
            output_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            background="#f8fafc",
            foreground="#172033",
            relief=tk.FLAT,
            padx=12,
            pady=12,
        )
        scrollbar = ttk.Scrollbar(
            output_frame, orient=tk.VERTICAL, command=self.output.yview
        )
        self.output.configure(yscrollcommand=scrollbar.set)
        self.output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_var = tk.StringVar(value=f"就绪  |  作者：{AUTHOR}")
        ttk.Label(container, textvariable=self.status_var, style="Sub.TLabel").pack(
            anchor=tk.W, pady=(10, 0)
        )

    def run_ping(self):
        target = self._required_target()
        if not target:
            return

        def task():
            result = ping_host(target)
            entry = create_entry(
                target,
                "Ping 检测",
                result.to_text().replace("\n", "; "),
                "正常" if result.success else "异常",
            )
            return result.to_text(), [entry]

        self._run_background("正在执行 Ping 检测...", task)

    def run_ports(self):
        target = self._required_target()
        if not target:
            return
        try:
            ports = parse_port_spec(self.ports_var.get())
        except ValueError as exc:
            messagebox.showerror("端口格式错误", str(exc))
            return

        def task():
            results = scan_ports(target, ports)
            lines = []
            entries = []
            for item in results:
                status = "开放" if item.open else "关闭/不可达"
                lines.append(f"{target}:{item.port}  {status}  {item.message}")
                entries.append(
                    create_entry(f"{target}:{item.port}", "端口扫描", item.message, status)
                )
            return "\n".join(lines), entries

        self._run_background("正在扫描端口...", task)

    def run_dns(self):
        target = self._required_target()
        if not target:
            return

        def task():
            result = check_dns(target)
            entry = create_entry(
                target,
                "DNS 解析",
                result.to_text().replace("\n", "; "),
                "正常" if result.success else "异常",
            )
            return result.to_text(), [entry]

        self._run_background("正在解析 DNS...", task)

    def run_ip_lookup(self):
        target = self.target_var.get().strip()

        def task():
            result = lookup_ip(target or None)
            entry = create_entry(
                result.ip or target or "本机公网 IP",
                "IP 归属地查询",
                result.to_text().replace("\n", "; "),
                "正常" if result.success else "异常",
            )
            return result.to_text(), [entry]

        self._run_background("正在查询 IP 信息...", task)

    def run_speed(self):
        def task():
            result = run_speed_test()
            entry = create_entry(
                "当前网络",
                "网络测速",
                result.to_text().replace("\n", "; "),
                "正常" if result.success else "异常",
            )
            return result.to_text(), [entry]

        self._run_background("正在测试网络速度，请稍候...", task)

    def export_current_report(self):
        if not self.last_entries:
            messagebox.showwarning("没有结果", "请先执行至少一项检测。")
            return
        path = filedialog.asksaveasfilename(
            title="导出检测报告",
            defaultextension=".html",
            filetypes=[
                ("HTML 报告", "*.html"),
                ("TXT 报告", "*.txt"),
                ("CSV 报告", "*.csv"),
                ("Markdown 报告", "*.md"),
            ],
        )
        if not path:
            return
        try:
            output = export_report(self.last_entries, path)
            self.status_var.set(f"报告已导出：{output}")
            messagebox.showinfo("导出成功", output)
        except (ValueError, PermissionError, OSError) as exc:
            messagebox.showerror("导出失败", str(exc))

    def clear_results(self):
        self.output.delete("1.0", tk.END)
        self.last_entries = []
        self.status_var.set("结果已清空")

    def _required_target(self):
        target = self.target_var.get().strip()
        if not target:
            messagebox.showwarning("输入为空", "请输入 IP 地址或域名。")
            return None
        return target

    def _run_background(self, status, task):
        self.status_var.set(status)
        self._append_output(f"\n[{status}]\n")

        def worker():
            try:
                text, entries = task()
                self.root.after(0, self._show_task_result, text, entries)
            except (ValueError, FileNotFoundError, PermissionError, OSError) as exc:
                self.root.after(0, self._show_task_error, str(exc))
            except Exception as exc:
                self.root.after(0, self._show_task_error, f"操作失败：{exc}")

        threading.Thread(target=worker, daemon=True).start()

    def _show_task_result(self, text, entries):
        self._append_output(text + "\n")
        self.last_entries.extend(entries)
        self.status_var.set("检测完成")

    def _show_task_error(self, message):
        self._append_output(f"错误：{message}\n")
        self.status_var.set("检测失败")
        messagebox.showerror("操作失败", message)

    def _append_output(self, text):
        self.output.insert(tk.END, text)
        self.output.see(tk.END)


def launch_gui():
    """Create and run the Tkinter desktop window."""
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        raise RuntimeError(f"Unable to start Tkinter GUI: {exc}") from exc
    NetworkToolsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
