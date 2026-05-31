#!/usr/bin/env python3
"""
Portfolio Manager – cross-platform GUI for backend servers + Cloudflare tunnels.
Monitors health, captures logs, starts/stops with one click.
"""

import os, sys, subprocess, threading, json, time, signal, platform
from pathlib import Path
from datetime import datetime
from queue import Queue
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    print("tkinter not available.")
    print("Linux:   sudo dnf install python3-tkinter")
    print("macOS:   brew install python-tk")
    print("Windows: reinstall Python with 'tcl/tk and IDLE' checked")
    sys.exit(1)

HOME = Path.home()
IS_LINUX = platform.system() == "Linux"
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"

REPOS = {
    "URL Shortener": {
        "path": str(HOME / "Dokumenty" / "FastAPI-url"),
        "port": 8000,
        "health": "http://localhost:8000/health",
        "systemd": "shortener-api",
        "tunnel_systemd": "cf-tunnel",
    },
    "GraphQL Blog": {
        "path": str(HOME / "Dokumenty" / "graphql-blog"),
        "port": 8001,
        "health": "http://localhost:8001/health",
        "systemd": "graphql-blog",
        "tunnel_systemd": "cf-tunnel-graphql",
    },
    "Portfolio API": {
        "path": str(HOME / "Dokumenty" / "python-portfolio"),
        "port": 8002,
        "health": "http://localhost:8002/health",
        "systemd": "portfolio-api",
        "tunnel_systemd": "cf-portfolio",
    },
    "AI Chat Proxy": {
        "path": str(HOME / "Dokumenty" / "ai-chat-proxy"),
        "port": 8003,
        "health": "http://localhost:8003/health",
        "systemd": "ai-chat-proxy",
        "tunnel_systemd": "cf-ai-chat",
    },
    "Task Queue": {
        "path": str(HOME / "Dokumenty" / "task-queue"),
        "port": 8004,
        "health": "http://localhost:8004/health",
        "systemd": "task-queue",
        "tunnel_systemd": "cf-task-queue",
    },
    "RAG QA": {
        "path": str(HOME / "Dokumenty" / "rag-qa"),
        "port": 8005,
        "health": "http://localhost:8005/health",
        "systemd": "rag-qa",
        "tunnel_systemd": "cf-rag",
    },
    "Chat Proxy Light": {
        "path": str(HOME / "Dokumenty" / "chat-proxy"),
        "port": 8006,
        "health": "http://localhost:8006/health",
        "systemd": "chat-proxy",
        "tunnel_systemd": "cf-chat-proxy",
    },
}

CLOUDFLARED = str(HOME / ".local" / "bin" / "cloudflared")


def find_venv_python(project_path):
    candidates = [
        f"{project_path}/venv/bin/python3",
        f"{project_path}/venv/Scripts/python.exe",
        f"{project_path}/.venv/bin/python3",
        f"{project_path}/.venv/Scripts/python.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "python3"


def is_port_used(port):
    if IS_WINDOWS:
        r = subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True, text=True)
        return bool(r.stdout.strip())
    else:
        r = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
        return bool(r.stdout.strip())


def pid_on_port(port):
    if IS_WINDOWS:
        r = subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True, text=True)
        if r.stdout.strip():
            parts = r.stdout.strip().split()
            return parts[-1] if parts else ""
        return ""
    else:
        r = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
        return r.stdout.strip().split("\n")[0] if r.stdout.strip() else ""


def tunnel_running():
    r = subprocess.run(["pgrep", "-f", "cloudflared"], capture_output=True, text=True) if not IS_WINDOWS else \
        subprocess.run("tasklist /FI \"IMAGENAME eq cloudflared.exe\"", shell=True, capture_output=True, text=True)
    return bool(r.stdout.strip())


def systemd_active(unit):
    if not IS_LINUX:
        return None
    r = subprocess.run(["systemctl", "--user", "is-active", unit], capture_output=True, text=True)
    return r.stdout.strip()


def health_check(url, timeout=3):
    try:
        import urllib.request
        r = urllib.request.urlopen(url, timeout=timeout)
        return r.status == 200
    except Exception:
        return False


def get_tunnel_url():
    try:
        r = subprocess.run(
            ["journalctl", "--user", "-u", "cf-portfolio", "--no-pager", "-n", "50"],
            capture_output=True, text=True, timeout=5
        )
        import re
        urls = re.findall(r"https://[a-z0-9-]+\.trycloudflare\.com", r.stdout)
        return urls[-1] if urls else None
    except Exception:
        return None


class ServerProcess:
    def __init__(self, name, project_path, port):
        self.name = name
        self.project_path = project_path
        self.port = port
        self.process = None
        self.log_queue = Queue()
        self.running = False
        self._reader_thread = None

    def start(self):
        if is_port_used(self.port):
            self.log(f"already running on :{self.port}")
            self.running = True
            return True
        venv_python = find_venv_python(self.project_path)
        cmd = f"cd \"{self.project_path}\" && \"{venv_python}\" -m uvicorn app.main:app --host 0.0.0.0 --port {self.port}"
        try:
            self.process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                preexec_fn=os.setsid if not IS_WINDOWS else None,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if IS_WINDOWS else 0,
                bufsize=1, text=True
            )
            self.running = True
            self._reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self._reader_thread.start()
            self.log(f"started on :{self.port}")
            return True
        except Exception as e:
            self.log(f"failed: {e}")
            return False

    def stop(self):
        if self.process and self.process.poll() is None:
            if IS_WINDOWS:
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process.wait(timeout=5)
        pid = pid_on_port(self.port)
        if pid:
            if IS_WINDOWS:
                subprocess.run(f"taskkill /F /PID {pid}", shell=True)
            else:
                subprocess.run(["kill", pid])
        self.running = False
        self.log("stopped")

    def _read_output(self):
        try:
            for line in iter(self.process.stdout.readline, ""):
                self.log_queue.put(line.rstrip())
        except Exception:
            pass

    def drain_log(self):
        lines = []
        while not self.log_queue.empty():
            lines.append(self.log_queue.get_nowait())
        return lines

    def log(self, msg):
        self.log_queue.put(f"[{self.name}] {msg}")


class ManagerApp:
    def __init__(self):
        self.servers = {name: ServerProcess(name, info["path"], info["port"])
                        for name, info in REPOS.items()}
        self.tunnel_proc = None
        self.root = tk.Tk()
        self.root.title("Portfolio Manager")
        self.root.geometry("800x640")
        self.root.configure(bg="#0a0a0f")
        self.root.minsize(600, 480)
        if IS_WINDOWS:
            self.root.iconbitmap(default="")
        self._build_ui()
        self._start_status_poller()

    def _build_ui(self):
        # Title
        header = tk.Frame(self.root, bg="#12121e", height=48)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="⚡ Portfolio Manager", font=("Segoe UI", 14, "bold"),
                 fg="#6366f1", bg="#12121e").pack(side=tk.LEFT, padx=16, pady=10)

        # Control bar
        bar = tk.Frame(self.root, bg="#0a0a0f")
        bar.pack(fill=tk.X, padx=12, pady=6)
        for text, cmd, color in [
            ("▶ All", self._start_all, "#22c55e"),
            ("■ All", self._stop_all, "#ef4444"),
            ("⟳ Status", self._status, "#6366f1"),
            ("☰ Logs", self._toggle_logs, "#f59e0b"),
        ]:
            b = tk.Button(bar, text=text, font=("Segoe UI", 9, "bold"),
                          bg=color, fg="white", relief="flat", padx=14, pady=4,
                          cursor="hand2", border=0, command=cmd)
            b.pack(side=tk.LEFT, padx=3)

        # Project cards
        self.cards = {}
        cards_frame = tk.Frame(self.root, bg="#0a0a0f")
        cards_frame.pack(fill=tk.X, padx=12, pady=4)

        for name, info in REPOS.items():
            card = tk.Frame(cards_frame, bg="#12121e", highlightbackground="#2a2a44",
                            highlightthickness=1, padx=12, pady=8)
            card.pack(fill=tk.X, pady=3)

            row1 = tk.Frame(card, bg="#12121e")
            row1.pack(fill=tk.X)

            # Status dot
            dot = tk.Canvas(row1, width=10, height=10, bg="#12121e", highlightthickness=0)
            dot.create_oval(1, 1, 9, 9, fill="#8888aa", outline="")
            dot.pack(side=tk.LEFT, padx=(0, 8))

            tk.Label(row1, text=name, font=("Segoe UI", 11, "bold"),
                     fg="#e2e2f0", bg="#12121e").pack(side=tk.LEFT)

            # URL label
            url_label = tk.Label(row1, text="", font=("Segoe UI", 8),
                                 fg="#8888aa", bg="#12121e")
            url_label.pack(side=tk.LEFT, padx=(10, 0))

            for text, cmd, color in [
                ("▶", lambda n=name: self._start_backend(n), "#22c55e"),
                ("■", lambda n=name: self._stop_backend(n), "#ef4444"),
                ("🌐", lambda n=name: self._open_browser(n), "#6366f1"),
            ]:
                b = tk.Button(row1, text=text, font=("Segoe UI", 9),
                              bg=color, fg="white", relief="flat", width=3, pady=1,
                              cursor="hand2", border=0, command=cmd)
                b.pack(side=tk.RIGHT, padx=2)

            # Second row: tunnel controls
            row2 = tk.Frame(card, bg="#12121e")
            row2.pack(fill=tk.X, pady=(4, 0))

            tunnel_label = tk.Label(row2, text="Tunnel: —", font=("Segoe UI", 8),
                                    fg="#8888aa", bg="#12121e")
            tunnel_label.pack(side=tk.LEFT, padx=(18, 0))

            for text, cmd in [
                ("⏳", lambda n=name: self._start_tunnel(n)),
                ("⏹", lambda: self._stop_tunnel()),
            ]:
                b = tk.Button(row2, text=text, font=("Segoe UI", 8),
                              bg="#1a1a2e", fg="#8888aa", relief="flat", width=3, pady=0,
                              cursor="hand2", border=0, command=cmd)
                b.pack(side=tk.RIGHT, padx=1)

            self.cards[name] = {"card": card, "dot": dot, "url_label": url_label,
                                "tunnel_label": tunnel_label, "info": info}

        # Tunnel URL bar
        tunnel_bar = tk.Frame(self.root, bg="#12121e", highlightbackground="#2a2a44",
                              highlightthickness=1, padx=12, pady=4)
        tunnel_bar.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(tunnel_bar, text="🔗", font=("Segoe UI", 10), bg="#12121e",
                 fg="#8888aa").pack(side=tk.LEFT, padx=(0, 6))
        self.tunnel_url_var = tk.StringVar(value="Tunnel: —")
        tk.Label(tunnel_bar, textvariable=self.tunnel_url_var, font=("Segoe UI", 9),
                 bg="#12121e", fg="#6366f1").pack(side=tk.LEFT)

        # Log area (collapsible)
        log_container = tk.Frame(self.root, bg="#0a0a0f")
        log_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        log_header = tk.Frame(log_container, bg="#0a0a0f")
        log_header.pack(fill=tk.X)
        tk.Label(log_header, text="Server Logs", font=("Segoe UI", 9, "bold"),
                 fg="#8888aa", bg="#0a0a0f").pack(side=tk.LEFT)

        self.log_canvas_visible = True
        self._log_text = tk.Text(log_container, font=("Consolas", 9), bg="#0a0a0f",
                                 fg="#22c55e", insertbackground="#e2e2f0",
                                 relief="flat", border=0, state=tk.DISABLED,
                                 wrap=tk.WORD, height=14)
        self._log_text.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        # Status bar
        status = tk.Frame(self.root, bg="#12121e", height=28)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(status, textvariable=self.status_var, font=("Segoe UI", 8),
                 fg="#8888aa", bg="#12121e").pack(side=tk.LEFT, padx=12)

        self._log("Portfolio Manager loaded")
        self._log(f"Platform: {platform.system()} {platform.machine()}")

    def _log(self, msg):
        self.root.after(0, self._append_log, msg)

    def _append_log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_text.config(state=tk.NORMAL)
        self._log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self._log_text.see(tk.END)
        self._log_text.config(state=tk.DISABLED)

    def _update_status(self, text):
        self.status_var.set(text)

    def _toggle_logs(self):
        if self.log_canvas_visible:
            self._log_text.pack_forget()
            self.log_canvas_visible = False
        else:
            self._log_text.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
            self.log_canvas_visible = True

    def _thread(self, target):
        threading.Thread(target=target, daemon=True).start()

    def _start_backend(self, name):
        def go():
            srv = self.servers[name]
            ok = srv.start()
            self._drain_log(srv)
            if ok:
                self._log(f"[{name}] backend started")
        self._thread(go)

    def _stop_backend(self, name):
        def go():
            srv = self.servers[name]
            srv.stop()
            self._drain_log(srv)
            self._log(f"[{name}] backend stopped")
        self._thread(go)

    def _start_all(self):
        def go():
            self._log("── Starting all backends ──")
            for name in self.servers:
                self._start_backend(name)
            time.sleep(3)
            self._start_tunnel("Portfolio API")
        self._thread(go)

    def _stop_all(self):
        def go():
            self._log("── Stopping everything ──")
            self._stop_tunnel()
            for name in list(self.servers.keys()):
                self._stop_backend(name)
            subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True)
            subprocess.run(["pkill", "-f", "cloudflared"], capture_output=True)
            self._log("All services stopped")
        self._thread(go)

    def _start_tunnel(self, name):
        def go():
            if IS_WINDOWS:
                cmd = f"start /B {CLOUDFLARED} tunnel --url http://localhost:{REPOS[name]['port']}"
            else:
                cmd = f"{CLOUDFLARED} tunnel --url http://localhost:{REPOS[name]['port']}"
            self.tunnel_proc = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                preexec_fn=os.setsid if not IS_WINDOWS else None,
                bufsize=1, text=True
            )
            self._log("Tunnel starting (may take 30s for DNS)...")
            threading.Thread(target=self._read_tunnel_log, daemon=True).start()
        self._thread(go)

    def _read_tunnel_log(self):
        import re
        try:
            for line in iter(self.tunnel_proc.stdout.readline, ""):
                line = line.rstrip()
                self._log(f"[tunnel] {line}")
                m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", line)
                if m:
                    url = m.group(0)
                    self.root.after(0, lambda u=url: self.tunnel_url_var.set(f"🔗 {u}"))
        except Exception:
            pass

    def _stop_tunnel(self):
        if self.tunnel_proc and self.tunnel_proc.poll() is None:
            if IS_WINDOWS:
                subprocess.run("taskkill /F /IM cloudflared.exe", shell=True)
            else:
                os.killpg(os.getpgid(self.tunnel_proc.pid), signal.SIGTERM)
        else:
            subprocess.run(["pkill", "-f", "cloudflared"], capture_output=True)
        self.tunnel_url_var.set("Tunnel: —")
        self._log("Tunnel stopped")

    def _open_browser(self, name):
        info = REPOS[name]
        url = f"http://localhost:{info['port']}"
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            self._log(f"Open browser: {url}")

    def _status(self):
        def go():
            self._log("── Status ──")
            for name, info in REPOS.items():
                used = is_port_used(info["port"])
                pid = pid_on_port(info["port"])
                healthy = health_check(info["health"])
                s = "🟢" if healthy else ("🟡" if used else "🔴")
                self._log(f"  {s} {name}: port {info['port']} {'PID '+pid if pid else 'free'}")
                self._update_card_dot(name, healthy)
            t = tunnel_running()
            self._log(f"  {'🟢' if t else '🔴'} Tunnel: {'running' if t else 'stopped'}")
        self._thread(go)

    def _update_card_dot(self, name, healthy):
        def go():
            card = self.cards[name]
            color = "#22c55e" if healthy else "#ef4444"
            card["dot"].itemconfig(1, fill=color)
        self.root.after(0, go)

    def _drain_log(self, srv):
        for line in srv.drain_log():
            self._log(line)

    def _start_status_poller(self):
        def poll():
            while True:
                time.sleep(5)
                for name, card in self.cards.items():
                    healthy = health_check(card["info"]["health"], timeout=2)
                    color = "#22c55e" if healthy else "#ef4444"
                    self.root.after(0, lambda c=color, n=name: self.cards[n]["dot"].itemconfig(1, fill=c))
                    if healthy:
                        ip = "localhost"
                        self.root.after(0, lambda n=name, ip=ip: self.cards[n]["url_label"].config(
                            text=f"http://{ip}:{card['info']['port']}"))
        threading.Thread(target=poll, daemon=True).start()

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._stop_all()


if __name__ == "__main__":
    ManagerApp().run()
