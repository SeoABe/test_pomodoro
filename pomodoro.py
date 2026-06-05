# -*- coding: utf-8 -*-
"""
메모리 상주형 포모도로 타이머
- 항상 위 작은 창 + 시스템 트레이 동시 동작
- 창을 닫으면 트레이로 최소화되어 계속 동작
- 트레이 아이콘에 원형 진행률 게이지 + 남은 분 표시
- 설정 창에서 시간/옵션 변경, %APPDATA%\\pomodoro\\config.json 에 영구 저장
- 의존성: pystray, Pillow (tkinter / winsound 는 파이썬 기본 내장)
"""

import os
import json
import threading
import tkinter as tk
from tkinter import font as tkfont, messagebox

import pystray
from PIL import Image, ImageDraw, ImageFont

try:
    import winsound  # Windows 기본 내장
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


# ---------------------------------------------------------------------------
# 설정 영구 저장
# ---------------------------------------------------------------------------
CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "pomodoro")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "work_min": 25,
    "short_min": 5,
    "long_min": 15,
    "cycles_before_long": 4,
    "auto_start": True,   # 단계 종료 후 자동으로 다음 단계 시작
    "sound": True,        # 알림음
}


def load_config():
    cfg = dict(DEFAULTS)
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg.update({k: v for k, v in json.load(f).items() if k in DEFAULTS})
    except Exception:
        pass
    return cfg


def save_config(cfg):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


PHASE_META = {
    "work":  {"label": "집중",     "color": "#e3534b", "bg": "#2b1b1a"},
    "short": {"label": "짧은 휴식", "color": "#4caf78", "bg": "#16241d"},
    "long":  {"label": "긴 휴식",   "color": "#4a8fe3", "bg": "#161f2b"},
}


class Pomodoro:
    def __init__(self):
        self.cfg = load_config()

        # --- 상태 ---
        self.phase = "work"
        self.remaining = self._phase_secs("work")
        self.running = False
        self.completed_work = 0
        self._settings_win = None

        # --- tkinter 창 ---
        self.root = tk.Tk()
        self.root.title("포모도로")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.geometry("210x150")
        self._place_bottom_right()

        self.phase_lbl = tk.Label(self.root, font=("Segoe UI", 11, "bold"))
        self.phase_lbl.pack(pady=(10, 0))

        self.time_lbl = tk.Label(self.root, font=tkfont.Font(family="Consolas", size=34, weight="bold"))
        self.time_lbl.pack()

        btns = tk.Frame(self.root)
        btns.pack(pady=(4, 4))
        self.start_btn = tk.Button(btns, text="시작", width=6, command=self.toggle)
        self.start_btn.grid(row=0, column=0, padx=2)
        tk.Button(btns, text="리셋", width=5, command=self.reset).grid(row=0, column=1, padx=2)
        tk.Button(btns, text="건너뛰기", width=7, command=self.skip).grid(row=0, column=2, padx=2)

        bottom = tk.Frame(self.root)
        bottom.pack()
        tk.Button(bottom, text="⚙ 설정", width=8, command=self.open_settings,
                  relief="flat").grid(row=0, column=0, padx=2)

        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        # --- 트레이 아이콘 ---
        self.icon = pystray.Icon("pomodoro", self._make_icon(), "포모도로")
        self.icon.menu = pystray.Menu(
            pystray.MenuItem("창 보이기/숨기기", self._tray_toggle_window, default=True),
            pystray.MenuItem(lambda i: "일시정지" if self.running else "시작", self._tray_toggle_run),
            pystray.MenuItem("리셋", lambda i: self.root.after(0, self.reset)),
            pystray.MenuItem("건너뛰기", lambda i: self.root.after(0, self.skip)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("설정…", lambda i: self.root.after(0, self.open_settings)),
            pystray.MenuItem("종료", self._tray_quit),
        )

        self._render()
        self._tick()

    # ------------------------------------------------------------------ 설정값
    def _phase_secs(self, phase):
        return {
            "work": self.cfg["work_min"],
            "short": self.cfg["short_min"],
            "long": self.cfg["long_min"],
        }[phase] * 60

    # ------------------------------------------------------------------ 배치
    def _place_bottom_right(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{sw - 230}+{sh - 220}")

    # ------------------------------------------------------------------ 로직
    def toggle(self):
        self.running = not self.running
        self._render()

    def reset(self):
        self.running = False
        self.remaining = self._phase_secs(self.phase)
        self._render()

    def skip(self):
        self._advance(played_full=False)

    def _advance(self, played_full=True):
        if self.phase == "work":
            if played_full:
                self.completed_work += 1
            if self.completed_work > 0 and self.completed_work % self.cfg["cycles_before_long"] == 0:
                self.phase = "long"
            else:
                self.phase = "short"
        else:
            self.phase = "work"
        self.remaining = self._phase_secs(self.phase)
        # 자동 시작 옵션: 사용자가 건너뛴 경우에도 흐름 유지
        self.running = bool(self.cfg["auto_start"])
        self._render()

    def _tick(self):
        if self.running and self.remaining > 0:
            self.remaining -= 1
            self._render()
            if self.remaining <= 0:
                self._on_phase_end()
        self.root.after(1000, self._tick)

    def _on_phase_end(self):
        finished = PHASE_META[self.phase]["label"]
        self._advance(played_full=True)
        nxt = PHASE_META[self.phase]["label"]
        verb = "자동 시작합니다" if self.cfg["auto_start"] else "시작 시간입니다"
        self._notify(f"{finished} 완료", f"{nxt} {verb}.")
        self._beep()

    # ------------------------------------------------------------------ 표시
    def _fmt(self):
        m, s = divmod(self.remaining, 60)
        return f"{m:02d}:{s:02d}"

    def _progress(self):
        total = self._phase_secs(self.phase)
        return 0.0 if total <= 0 else 1.0 - self.remaining / total

    def _render(self):
        p = PHASE_META[self.phase]
        self.root.configure(bg=p["bg"])
        self.phase_lbl.configure(
            text=f'{p["label"]}  ·  {self.completed_work}회 완료',
            fg=p["color"], bg=p["bg"])
        self.time_lbl.configure(text=self._fmt(), fg="#f5f5f5", bg=p["bg"])
        self.start_btn.configure(text="일시정지" if self.running else "시작")
        try:
            self.icon.icon = self._make_icon()
            self.icon.title = f'{p["label"]} {self._fmt()}'
        except Exception:
            pass

    def _make_icon(self):
        """원형 진행률 게이지 + 남은 분 숫자를 그린 트레이 아이콘."""
        p = PHASE_META[self.phase]
        S = 64
        scale = 4  # 안티앨리어싱용 슈퍼샘플링
        big = S * scale
        img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        pad = 3 * scale
        box = (pad, pad, big - pad, big - pad)
        # 바탕 링(어둡게)
        d.ellipse(box, fill=(40, 40, 40, 255))
        # 진행 호(밝게) — 12시 방향에서 시계방향
        sweep = 360 * self._progress()
        if sweep > 0:
            d.pieslice(box, -90, -90 + sweep, fill=p["color"])
        # 가운데 구멍 → 도넛
        hole = 14 * scale
        d.ellipse((hole, hole, big - hole, big - hole), fill=(28, 28, 28, 255))

        # 남은 분(또는 마지막 1분은 초) 숫자
        m = self.remaining // 60
        text = str(m) if m > 0 else str(self.remaining)
        try:
            fnt = ImageFont.truetype("arialbd.ttf", (30 if len(text) < 2 else 24) * scale)
        except Exception:
            fnt = ImageFont.load_default()
        bbox = d.textbbox((0, 0), text, font=fnt)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(((big - tw) / 2 - bbox[0], (big - th) / 2 - bbox[1]), text,
               font=fnt, fill="#ffffff")

        return img.resize((S, S), Image.LANCZOS)

    # ------------------------------------------------------------------ 알림
    def _notify(self, title, msg):
        try:
            self.icon.notify(msg, title)
        except Exception:
            pass

    def _beep(self):
        if HAS_SOUND and self.cfg["sound"]:
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass

    # ------------------------------------------------------------------ 설정 창
    def open_settings(self):
        if self._settings_win is not None and tk.Toplevel.winfo_exists(self._settings_win):
            self._settings_win.lift()
            return
        self.show_window()
        win = tk.Toplevel(self.root)
        self._settings_win = win
        win.title("설정")
        win.attributes("-topmost", True)
        win.resizable(False, False)
        win.configure(padx=14, pady=12)

        rows = [
            ("집중 (분)", "work_min"),
            ("짧은 휴식 (분)", "short_min"),
            ("긴 휴식 (분)", "long_min"),
            ("긴 휴식 주기 (집중 N회)", "cycles_before_long"),
        ]
        vars_int = {}
        for i, (label, key) in enumerate(rows):
            tk.Label(win, text=label).grid(row=i, column=0, sticky="w", pady=3)
            v = tk.IntVar(value=self.cfg[key])
            vars_int[key] = v
            tk.Spinbox(win, from_=1, to=180, width=6, textvariable=v).grid(row=i, column=1, padx=8)

        auto_v = tk.BooleanVar(value=self.cfg["auto_start"])
        sound_v = tk.BooleanVar(value=self.cfg["sound"])
        tk.Checkbutton(win, text="단계 종료 후 자동 시작", variable=auto_v).grid(
            row=len(rows), column=0, columnspan=2, sticky="w", pady=(6, 0))
        tk.Checkbutton(win, text="알림음", variable=sound_v).grid(
            row=len(rows) + 1, column=0, columnspan=2, sticky="w")

        def apply_and_close():
            for key, v in vars_int.items():
                try:
                    self.cfg[key] = max(1, int(v.get()))
                except Exception:
                    pass
            self.cfg["auto_start"] = bool(auto_v.get())
            self.cfg["sound"] = bool(sound_v.get())
            save_config(self.cfg)
            # 현재 단계의 남은 시간을 새 길이에 맞춰 갱신(정지 상태일 때만)
            if not self.running:
                self.remaining = self._phase_secs(self.phase)
            self._render()
            self._settings_win = None
            win.destroy()

        def cancel():
            self._settings_win = None
            win.destroy()

        btnf = tk.Frame(win)
        btnf.grid(row=len(rows) + 2, column=0, columnspan=2, pady=(12, 0))
        tk.Button(btnf, text="저장", width=8, command=apply_and_close).grid(row=0, column=0, padx=4)
        tk.Button(btnf, text="취소", width=8, command=cancel).grid(row=0, column=1, padx=4)
        win.protocol("WM_DELETE_WINDOW", cancel)

    # ------------------------------------------------------------------ 창/트레이 제어
    def hide_window(self):
        self.root.withdraw()

    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)

    def _tray_toggle_window(self, icon, item):
        def do():
            if self.root.state() == "withdrawn":
                self.show_window()
            else:
                self.hide_window()
        self.root.after(0, do)

    def _tray_toggle_run(self, icon, item):
        self.root.after(0, self.toggle)

    def _tray_quit(self, icon, item):
        self.icon.stop()
        self.root.after(0, self.root.destroy)

    # ------------------------------------------------------------------ 실행
    def run(self):
        threading.Thread(target=self.icon.run, daemon=True).start()
        self.root.mainloop()
        try:
            self.icon.stop()
        except Exception:
            pass


def _selftest():
    """동결(exe) 빌드의 임포트/아이콘/알림 경로를 헤드리스로 검증 후 종료."""
    app = Pomodoro()
    app.toggle()
    app.skip()
    assert app._make_icon().size == (64, 64)
    app._notify("selftest", "ok")
    app._beep()
    app.root.after(200, lambda: app.icon.stop())
    app.root.after(300, app.root.destroy)
    threading.Thread(target=app.icon.run, daemon=True).start()
    app.root.mainloop()
    print("SELFTEST OK", "phase=", app.phase)


if __name__ == "__main__":
    if os.environ.get("POMO_SELFTEST"):
        _selftest()
    else:
        Pomodoro().run()
