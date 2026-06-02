import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from xhs_crawler.auth import load_auth_data
from xhs_crawler.capture import run_capture
from xhs_crawler.crawler import run_crawl
from xhs_crawler.settings import CRAWLER_CFG


class App:
    def __init__(self, root, fonts):
        self.root = root
        self.fonts = fonts
        self.root.title(f"小红书爬虫工具 - {time.strftime('%Y-%m-%d')}")
        self.root.minsize(820, 620)
        self.root.geometry("860x640")
        self.auth_data = load_auth_data()
        self.crawl_stop = threading.Event()
        self.capturing = False
        self._build_ui()
        self.refresh_auth_status()

    def _build_ui(self):
        header = ttk.Frame(self.root, padding=(16, 12))
        header.pack(fill=tk.X)

        left = ttk.Frame(header)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(left, text="小红书爬虫工具", style='Title.TLabel').pack(anchor=tk.W)
        self.sub_status = ttk.Label(left, text="", style='Sub.TLabel')
        self.sub_status.pack(anchor=tk.W, pady=(4, 0))

        right = ttk.Frame(header)
        right.pack(side=tk.RIGHT)
        self.capture_btn = ttk.Button(right, text="捕获鉴权", command=self.start_capture, width=12)
        self.capture_btn.pack(side=tk.LEFT, padx=4)
        self.start_btn = ttk.Button(right, text="开始爬取", command=self.start_crawl, width=12)
        self.start_btn.pack(side=tk.LEFT, padx=4)
        self.stop_btn = ttk.Button(right, text="停止", command=self.stop_all, width=10, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=4)

        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        auth_frame = ttk.Frame(notebook, padding=12)
        notebook.add(auth_frame, text="抓包模式")

        auth_box = ttk.LabelFrame(auth_frame, text="操作说明", padding=12)
        auth_box.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(
            auth_box,
            text="1. 点击顶部「捕获鉴权」启动浏览器\n"
                 "2. 登录小红书，搜索关键词并点击任意帖子\n"
                 "3. 程序自动捕获鉴权并保存",
            justify=tk.LEFT
        ).pack(anchor=tk.W)

        status_box = ttk.LabelFrame(auth_frame, text="鉴权状态", padding=12)
        status_box.pack(fill=tk.X, pady=(0, 8))
        self.auth_status = ttk.Label(status_box, text="")
        self.auth_status.pack(anchor=tk.W)

        self.capture_progress = ttk.Progressbar(auth_frame, mode='determinate')
        self.capture_progress.pack(fill=tk.X, pady=8)
        self.capture_status = ttk.Label(auth_frame, text="等待捕获", style='Sub.TLabel')
        self.capture_status.pack(anchor=tk.W)

        crawl_frame = ttk.Frame(notebook, padding=12)
        notebook.add(crawl_frame, text="爬虫模式")

        setting_box = ttk.LabelFrame(crawl_frame, text="爬取设置", padding=12)
        setting_box.pack(fill=tk.X, pady=(0, 8))
        setting_box.columnconfigure(1, weight=1)

        ttk.Label(setting_box, text="搜索关键词：").grid(row=0, column=0, sticky=tk.W, pady=6, padx=(0, 12))
        self.keyword_var = tk.StringVar()
        ttk.Entry(setting_box, textvariable=self.keyword_var).grid(row=0, column=1, sticky=tk.EW, pady=6)

        ttk.Label(setting_box, text="爬取页数：").grid(row=1, column=0, sticky=tk.W, pady=6, padx=(0, 12))
        self.page_var = tk.IntVar(value=CRAWLER_CFG.get('default_page_count', 3))
        max_pages = CRAWLER_CFG.get('max_pages', 10)
        ttk.Spinbox(setting_box, from_=1, to=max_pages, textvariable=self.page_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=6)

        ttk.Label(setting_box, text="每条间隔(秒)：").grid(row=2, column=0, sticky=tk.W, pady=6, padx=(0, 12))
        self.interval_var = tk.DoubleVar(value=CRAWLER_CFG.get('default_item_interval', 3.0))
        ttk.Spinbox(setting_box, from_=0.5, to=30, increment=0.5, textvariable=self.interval_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=6)

        ttk.Label(
            setting_box,
            text="每条数据保存后等待，降低触发风控概率",
            style='Sub.TLabel'
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))

        progress_box = ttk.LabelFrame(crawl_frame, text="爬取进度", padding=12)
        progress_box.pack(fill=tk.X, pady=(0, 8))
        self.crawl_progress = ttk.Progressbar(progress_box, mode='determinate')
        self.crawl_progress.pack(fill=tk.X, pady=(0, 6))
        self.crawl_status = ttk.Label(progress_box, text="等待开始")
        self.crawl_status.pack(anchor=tk.W)

        log_frame = ttk.Frame(notebook, padding=12)
        notebook.add(log_frame, text="运行日志")

        self.log_text = scrolledtext.ScrolledText(
            log_frame, state=tk.DISABLED, wrap=tk.WORD,
            font=self.fonts['log'], spacing1=2, spacing3=2
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _log(self, msg):
        def _append():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        self.root.after(0, _append)

    def refresh_auth_status(self):
        self.auth_data = load_auth_data()
        if not self.auth_data:
            text = "未配置鉴权"
            self.auth_status.config(text=text)
            self.sub_status.config(text=text)
            return
        has_search = bool(self.auth_data.get('search'))
        has_note = bool(self.auth_data.get('note_detail'))
        has_cookie = bool(self.auth_data.get('cookies'))
        save_time = self.auth_data.get('save_time', '')
        if has_search and has_note and has_cookie:
            text = f"鉴权已就绪  ·  更新于 {save_time}"
        else:
            missing = []
            if not has_search:
                missing.append("搜索鉴权")
            if not has_note:
                missing.append("详情鉴权")
            if not has_cookie:
                missing.append("Cookie")
            text = f"鉴权不完整：{'、'.join(missing)}"
        self.auth_status.config(text=text)
        self.sub_status.config(text=text)

    def start_capture(self):
        if self.capturing:
            return
        self.capturing = True
        self.capture_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.capture_progress['value'] = 0
        self.capture_status.config(text="正在捕获...")
        self._log("开始捕获鉴权")

        def on_progress(val, text):
            self.root.after(0, lambda: (
                self.capture_progress.configure(value=val),
                self.capture_status.config(text=text)
            ))

        def on_done(data):
            def _finish():
                self.auth_data = data
                self.capturing = False
                self.capture_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                self.capture_status.config(text="捕获结束")
                self.refresh_auth_status()
            self.root.after(0, _finish)

        threading.Thread(target=run_capture, args=(self._log, on_progress, on_done), daemon=True).start()

    def start_crawl(self):
        keyword = self.keyword_var.get().strip()
        if not keyword:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
        self.auth_data = load_auth_data()
        self.crawl_stop.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.crawl_progress['value'] = 0
        self.crawl_status.config(text="爬取中...")
        self._log(f"开始爬取：{keyword}，{self.page_var.get()} 页，间隔 {self.interval_var.get()} 秒/条")

        def on_progress(val, text):
            self.root.after(0, lambda: (
                self.crawl_progress.configure(value=val),
                self.crawl_status.config(text=text)
            ))

        def on_done(count):
            def _finish():
                self.start_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                self.crawl_status.config(text=f"完成，共 {count} 条" if count else "已停止")
            self.root.after(0, _finish)

        threading.Thread(
            target=run_crawl,
            args=(keyword, self.page_var.get(), self.interval_var.get(), self.auth_data,
                  self.crawl_stop, self._log, on_progress, on_done),
            daemon=True
        ).start()

    def stop_all(self):
        self.crawl_stop.set()
        self.stop_btn.config(state=tk.DISABLED)
        self._log("已发送停止指令")
