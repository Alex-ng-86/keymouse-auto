import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import pyautogui
import threading
import time
import json
import random
from pynput import mouse, keyboard

# 设置主题
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ActionDialog(ctk.CTkToplevel):
    """用于添加或编辑动作的对话框"""
    def __init__(self, parent, action_data=None):
        super().__init__(parent)
        self.title("编辑动作")
        self.geometry("380x500")
        self.resizable(False, False)
        self.result = None
        self.parent = parent
        self.attributes("-topmost", True)
        
        # 主容器
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.action_types = ["鼠标点击", "鼠标移动", "滚轮滚动", "按键输入", "输入文本", "等待时间"]
        
        # 动作类型
        ctk.CTkLabel(self.main_frame, text="动作类型", font=("Microsoft YaHei UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        self.type_var = ctk.StringVar(value=self.action_types[0])
        self.type_cb = ctk.CTkComboBox(self.main_frame, values=self.action_types, command=self.on_type_change, variable=self.type_var)
        self.type_cb.pack(fill="x", pady=(0, 15))

        # 参数区域
        self.param_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.param_frame.pack(fill="both", expand=True)
        
        # 底部按钮
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=(20, 0))
        
        ctk.CTkButton(btn_frame, text="确定", command=self.on_ok, width=100).pack(side="left", padx=(0, 10), expand=True)
        ctk.CTkButton(btn_frame, text="取消", command=self.destroy, width=100, fg_color="transparent", border_width=1).pack(side="left", padx=(10, 0), expand=True)

        self.widgets = {}
        if action_data: self.load_data(action_data)
        else: self.on_type_change()

    def clear_params(self):
        for widget in self.param_frame.winfo_children(): widget.destroy()
        self.widgets = {}

    def on_type_change(self, event=None):
        self.clear_params()
        act_type = self.type_var.get()
        
        if act_type == "鼠标点击":
            self.create_coord_inputs()
            ctk.CTkLabel(self.param_frame, text="按键").grid(row=2, column=0, sticky="w", pady=5)
            self.widgets['button'] = ctk.CTkComboBox(self.param_frame, values=["left", "right", "middle"])
            self.widgets['button'].set("left")
            self.widgets['button'].grid(row=2, column=1, sticky="e", pady=5)
            self.widgets['double'] = ctk.BooleanVar()
            ctk.CTkCheckBox(self.param_frame, text="双击", variable=self.widgets['double']).grid(row=3, column=0, columnspan=2, sticky="w", pady=10)

        elif act_type == "鼠标移动":
            self.create_coord_inputs()

        elif act_type == "滚轮滚动":
            self.create_coord_inputs() # 可选，滚动时通常不需要移动，但保留位置作为参考
            ctk.CTkLabel(self.param_frame, text="滚动量 (+向上/-向下)").grid(row=2, column=0, sticky="w", pady=5)
            self.widgets['scroll'] = ctk.CTkEntry(self.param_frame)
            self.widgets['scroll'].insert(0, "-100")
            self.widgets['scroll'].grid(row=2, column=1, sticky="e", pady=5)

        elif act_type == "按键输入":
            ctk.CTkLabel(self.param_frame, text="按键 (如 'a', 'enter')").pack(anchor="w", pady=5)
            self.widgets['key'] = ctk.CTkEntry(self.param_frame)
            self.widgets['key'].pack(fill="x", pady=5)
            ctk.CTkLabel(self.param_frame, text="提示: 特殊键用 enter, tab, esc 等", text_color="gray", font=("Arial", 12)).pack(anchor="w")

        elif act_type == "输入文本":
            ctk.CTkLabel(self.param_frame, text="文本内容").pack(anchor="w", pady=5)
            self.widgets['text'] = ctk.CTkTextbox(self.param_frame, height=100) # 文本框高度
            self.widgets['text'].pack(fill="x", pady=5)

        elif act_type == "等待时间":
            ctk.CTkLabel(self.param_frame, text="时长 (秒)").pack(anchor="w", pady=5)
            self.widgets['seconds'] = ctk.CTkEntry(self.param_frame)
            self.widgets['seconds'].insert(0, "1.0")
            self.widgets['seconds'].pack(fill="x", pady=5)

        # 通用延迟
        ctk.CTkLabel(self.param_frame, text="执行前等待 (秒)").pack(side="bottom", anchor="w", pady=(10, 5))
        self.widgets['delay'] = ctk.CTkEntry(self.param_frame)
        self.widgets['delay'].insert(0, "0.1")
        self.widgets['delay'].pack(side="bottom", fill="x", pady=5)

    def create_coord_inputs(self):
        self.param_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.param_frame, text="X 坐标").grid(row=0, column=0, sticky="w", pady=5)
        self.widgets['x'] = ctk.CTkEntry(self.param_frame)
        self.widgets['x'].grid(row=0, column=1, sticky="e", pady=5)
        ctk.CTkLabel(self.param_frame, text="Y 坐标").grid(row=1, column=0, sticky="w", pady=5)
        self.widgets['y'] = ctk.CTkEntry(self.param_frame)
        self.widgets['y'].grid(row=1, column=1, sticky="e", pady=5)
        x, y = pyautogui.position()
        self.widgets['x'].insert(0, str(x))
        self.widgets['y'].insert(0, str(y))

    def load_data(self, data):
        mapping = {'click': "鼠标点击", 'move': "鼠标移动", 'scroll': "滚轮滚动", 
                   'key': "按键输入", 'text': "输入文本", 'wait': "等待时间"}
        for k, v in mapping.items():
            if k == data['type']:
                self.type_var.set(v)
                break
        self.on_type_change()
        try:
            if 'x' in data: self.widgets['x'].delete(0, 'end'); self.widgets['x'].insert(0, str(data['x']))
            if 'y' in data: self.widgets['y'].delete(0, 'end'); self.widgets['y'].insert(0, str(data['y']))
            if 'button' in data: self.widgets['button'].set(data['button'])
            if 'double' in data: self.widgets['double'].set(data.get('double', False))
            if 'amount' in data: self.widgets['scroll'].delete(0, 'end'); self.widgets['scroll'].insert(0, str(data['amount']))
            if 'key' in data: self.widgets['key'].delete(0, 'end'); self.widgets['key'].insert(0, data['key'])
            if 'text' in data: 
                self.widgets['text'].delete("1.0", 'end')
                self.widgets['text'].insert("1.0", data['text'])
            if 'seconds' in data: self.widgets['seconds'].delete(0, 'end'); self.widgets['seconds'].insert(0, str(data['seconds']))
            if 'delay' in data: self.widgets['delay'].delete(0, 'end'); self.widgets['delay'].insert(0, str(data.get('delay', 0.1)))
        except: pass

    def on_ok(self):
        act_type = self.type_var.get()
        try:
            res = {'delay': float(self.widgets['delay'].get() or 0)}
            if act_type == "鼠标点击":
                res.update({'type': 'click', 'x': int(self.widgets['x'].get()), 'y': int(self.widgets['y'].get()), 
                           'button': self.widgets['button'].get(), 'double': self.widgets['double'].get()})
            elif act_type == "鼠标移动":
                res.update({'type': 'move', 'x': int(self.widgets['x'].get()), 'y': int(self.widgets['y'].get())})
            elif act_type == "滚轮滚动":
                res.update({'type': 'scroll', 'x': int(self.widgets['x'].get()), 'y': int(self.widgets['y'].get()),
                           'amount': int(self.widgets['scroll'].get())})
            elif act_type == "按键输入":
                res.update({'type': 'key', 'key': self.widgets['key'].get()})
            elif act_type == "输入文本":
                res.update({'type': 'text', 'text': self.widgets['text'].get("1.0", "end-1c")})
            elif act_type == "等待时间":
                res.update({'type': 'wait', 'seconds': float(self.widgets['seconds'].get())})
            self.result = res
            self.destroy()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的参数")
            self.lift()

class AutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("灵动点击助手")
        self.geometry("750x700")
        
        self.script_data = [] 
        self.running = False
        self.current_mode = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_widgets()
        
        self.hotkey_thread = threading.Thread(target=self.global_hotkey_listener, daemon=True)
        self.hotkey_thread.start()

    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self, width=700, command=self.on_tab_change)
        self.tabview.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        
        # 增大 Tab 按钮
        self.tabview._segmented_button.configure(font=("Microsoft YaHei UI", 16, "bold"), height=40)
        
        self.tabview.add("简单连点器")
        self.tabview.add("脚本编辑器")
        
        self.setup_clicker_tab()
        self.setup_editor_tab()
        
        self.status_var = ctk.StringVar(value="就绪 - 按 F8 控制")
        self.status_bar = ctk.CTkLabel(self, textvariable=self.status_var, height=30, fg_color=("gray85", "gray20"), corner_radius=5)
        self.status_bar.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def on_tab_change(self):
        current_tab = self.tabview.get()
        if current_tab == "简单连点器":
            self.status_var.set("就绪 - 按 F8 控制")
        elif current_tab == "脚本编辑器":
            self.status_var.set("就绪 - 按 F9/F10 控制")

    def setup_clicker_tab(self):
        tab = self.tabview.tab("简单连点器")
        tab.grid_columnconfigure(0, weight=1)
        
        card = ctk.CTkFrame(tab)
        card.grid(row=0, column=0, pady=20, padx=20, sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(card, text="连点设置", font=("Microsoft YaHei UI", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        # 基础设置
        ctk.CTkLabel(card, text="点击间隔 (秒):").grid(row=1, column=0, sticky="e", padx=20, pady=10)
        self.click_interval = ctk.CTkEntry(card, width=120)
        self.click_interval.insert(0, "0.1")
        self.click_interval.grid(row=1, column=1, sticky="w", padx=20, pady=10)

        # 随机化设置
        rand_frame = ctk.CTkFrame(card, fg_color="transparent")
        rand_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ctk.CTkLabel(rand_frame, text="随机间隔 (±秒):").pack(side="left", padx=5)
        self.rand_interval = ctk.CTkEntry(rand_frame, width=80)
        self.rand_interval.insert(0, "0.0")
        self.rand_interval.pack(side="left", padx=5)
        
        ctk.CTkLabel(rand_frame, text="随机位置 (±像素):").pack(side="left", padx=(20, 5))
        self.rand_pos = ctk.CTkEntry(rand_frame, width=80)
        self.rand_pos.insert(0, "0")
        self.rand_pos.pack(side="left", padx=5)

        # 控制区
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=20)
        
        self.btn_clicker_start = ctk.CTkButton(btn_frame, text="开始 (F8)", command=self.start_clicker, width=140, height=45, font=("bold", 14))
        self.btn_clicker_start.pack(side="left", padx=15)
        self.btn_clicker_stop = ctk.CTkButton(btn_frame, text="停止 (F8)", command=self.stop_all, width=140, height=45, fg_color="#D32F2F", hover_color="#B71C1C", state="disabled", font=("bold", 14))
        self.btn_clicker_stop.pack(side="left", padx=15)

    def setup_editor_tab(self):
        tab = self.tabview.tab("脚本编辑器")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # 工具栏
        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(5, 10))
        
        btns = [
            ("➕ 添加", self.add_action, None), ("✎ 编辑", self.edit_action, None), ("❌ 删除", self.delete_action, "#D32F2F"),
            ("⬆", lambda: self.move_action(-1), "transparent"), ("⬇", lambda: self.move_action(1), "transparent"),
            ("💾 保存", self.save_script, "transparent"), ("📂 打开", self.load_script, "transparent")
        ]
        for t, c, color in btns:
            k = {"width": 60, "height": 30}
            if color == "transparent": k.update({"fg_color": "transparent", "border_width": 1, "text_color": ("gray10", "gray90")})
            elif color: k["fg_color"] = color
            ctk.CTkButton(toolbar, text=t, command=c, **k).pack(side="left", padx=3)

        # 列表
        tree_frame = ctk.CTkFrame(tab)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=5)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=30, borderwidth=0)
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", relief="flat")
        style.map("Treeview", background=[('selected', '#1f6aa5')])

        self.tree = ttk.Treeview(tree_frame, columns=("id", "type", "detail", "delay"), show='headings', selectmode='browse')
        self.tree.heading("id", text="#"); self.tree.column("id", width=40, anchor='center')
        self.tree.heading("type", text="类型"); self.tree.column("type", width=80, anchor='center')
        self.tree.heading("detail", text="参数详情"); self.tree.column("detail", width=350)
        self.tree.heading("delay", text="前置等待"); self.tree.column("delay", width=80, anchor='center')
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ctk.CTkScrollbar(tree_frame, command=self.tree.yview); sb.pack(side="right", fill="y")
        self.tree.configure(yscroll=sb.set)
        self.tree.bind("<Double-1>", lambda e: self.edit_action())

        # 底部控制
        ctrl_frame = ctk.CTkFrame(tab, height=60)
        ctrl_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        ctk.CTkLabel(ctrl_frame, text="循环次数:").pack(side="left", padx=(15, 5))
        self.loop_count = ctk.CTkEntry(ctrl_frame, width=50); self.loop_count.insert(0, "1"); self.loop_count.pack(side="left")
        
        self.humanize = ctk.BooleanVar()
        ctk.CTkCheckBox(ctrl_frame, text="防检测 (随机抖动)", variable=self.humanize).pack(side="left", padx=20)

        self.btn_play = ctk.CTkButton(ctrl_frame, text="▶ 开始回放 (F10)", command=self.toggle_playback, width=140, fg_color="#2E7D32")
        self.btn_play.pack(side="right", padx=15, pady=10)
        self.btn_record = ctk.CTkButton(ctrl_frame, text="🔴 开始录制 (F9)", command=self.toggle_record, width=140, fg_color="#C62828")
        self.btn_record.pack(side="right", padx=10, pady=10)

    # 逻辑实现
    def start_clicker(self):
        if self.running: return
        try:
            base = float(self.click_interval.get())
            rand_t = float(self.rand_interval.get())
            rand_p = int(self.rand_pos.get())
            if base <= 0: raise ValueError
        except:
            messagebox.showerror("错误", "参数无效")
            return
            
        self.running = True; self.current_mode = 'clicker'
        self.update_ui_state('running')
        threading.Thread(target=self.clicker_loop, args=(base, rand_t, rand_p), daemon=True).start()

    def clicker_loop(self, base, rand_t, rand_p):
        start_pos = pyautogui.position()
        while self.running and self.current_mode == 'clicker':
            # 随机位置
            x, y = pyautogui.position()
            if rand_p > 0:
                x += random.randint(-rand_p, rand_p)
                y += random.randint(-rand_p, rand_p)
            
            pyautogui.click(x, y)
            
            # 随机间隔
            sleep_time = base
            if rand_t > 0:
                sleep_time += random.uniform(-rand_t, rand_t)
            sleep_time = max(0.01, sleep_time)
            
            end = time.time() + sleep_time
            while time.time() < end:
                if not self.running: break
                time.sleep(0.01)
        self.stop_all()

    def refresh_tree(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for i, item in enumerate(self.script_data):
            detail = ""
            if item['type'] == 'click': detail = f"{item['button']} click ({item['x']}, {item['y']})" + (" [Double]" if item.get('double') else "")
            elif item['type'] == 'move': detail = f"Move to ({item['x']}, {item['y']})"
            elif item['type'] == 'scroll': detail = f"Scroll {item['amount']}"
            elif item['type'] == 'key': detail = f"Key: {item['key']}"
            elif item['type'] == 'text': detail = f"Type: {item['text']}"
            elif item['type'] == 'wait': detail = f"Wait {item['seconds']}s"
            self.tree.insert("", "end", values=(i+1, item['type'], detail, f"{item.get('delay', 0)}s"))

    def playback_thread(self):
        try: loops = int(self.loop_count.get())
        except: loops = 1
        human = self.humanize.get()
        count = 0
        
        while self.running:
            if loops > 0 and count >= loops: break
            count += 1
            self.status_var.set(f"回放中: 第 {count} 次")
            
            for item in self.script_data:
                if not self.running: break
                
                # 延迟逻辑
                delay = item.get('delay', 0)
                if human: delay += random.uniform(0.01, 0.05)
                if delay > 0: time.sleep(delay)
                
                # 执行动作
                if item['type'] == 'click':
                    x, y = item['x'], item['y']
                    if human:
                        x += random.randint(-2, 2)
                        y += random.randint(-2, 2)
                    pyautogui.click(x=x, y=y, button=item['button'])
                    if item.get('double'): 
                        time.sleep(random.uniform(0.05, 0.1) if human else 0.05)
                        pyautogui.click(x=x, y=y, button=item['button'])
                        
                elif item['type'] == 'move':
                    x, y = item['x'], item['y']
                    if human:
                        x += random.randint(-2, 2)
                        y += random.randint(-2, 2)
                        pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.3))
                    else:
                        pyautogui.moveTo(x, y)
                        
                elif item['type'] == 'scroll':
                    pyautogui.scroll(item['amount'])
                    
                elif item['type'] == 'key':
                    pyautogui.press(item['key'])
                    
                elif item['type'] == 'text':
                    # 逐字输入模拟
                    if human:
                        pyautogui.write(item['text'], interval=random.uniform(0.05, 0.15))
                    else:
                        pyautogui.write(item['text'])
                        
                elif item['type'] == 'wait':
                    wait_t = item['seconds']
                    if human: wait_t += random.uniform(0, 0.5)
                    time.sleep(wait_t)
            
            time.sleep(0.1)
        self.stop_all()

    # 其他方法保持不变 (add_action, edit_action, delete_action, move_action, record logic, hotkey)
    def add_action(self):
        dlg = ActionDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.script_data.append(dlg.result)
            self.refresh_tree()
    
    def edit_action(self):
        s = self.tree.selection()
        if not s: return
        idx = self.tree.index(s[0])
        dlg = ActionDialog(self, self.script_data[idx])
        self.wait_window(dlg)
        if dlg.result:
            self.script_data[idx] = dlg.result
            self.refresh_tree()
            
    def delete_action(self):
        s = self.tree.selection()
        if not s: return
        idx = self.tree.index(s[0])
        del self.script_data[idx]
        self.refresh_tree()
        
    def move_action(self, d):
        s = self.tree.selection()
        if not s: return
        idx = self.tree.index(s[0])
        n = idx + d
        if 0 <= n < len(self.script_data):
            self.script_data[idx], self.script_data[n] = self.script_data[n], self.script_data[idx]
            self.refresh_tree()
            self.tree.selection_set(self.tree.get_children()[n])
            
    def toggle_record(self):
        if self.running and self.current_mode == 'recording': self.stop_all()
        else: self.start_recording()
        
    def start_recording(self):
        if self.running: return
        self.running = True; self.current_mode = 'recording'
        self.script_data = []
        self.refresh_tree()
        self.update_ui_state('running')
        self.status_var.set("正在录制... (F9 停止)")
        self.last_time = time.time()
        self.mouse_listener = mouse.Listener(on_click=self.on_rec_click, on_scroll=self.on_rec_scroll)
        self.key_listener = keyboard.Listener(on_press=self.on_rec_key)
        self.mouse_listener.start(); self.key_listener.start()
        
    def on_rec_click(self, x, y, button, pressed):
        if not pressed or not self.running: return
        self.add_rec_event({'type': 'click', 'x': x, 'y': y, 'button': str(button).split('.')[-1]})
        
    def on_rec_scroll(self, x, y, dx, dy):
        if not self.running: return
        self.add_rec_event({'type': 'scroll', 'x': x, 'y': y, 'amount': dy * 100})
        
    def on_rec_key(self, key):
        if not self.running: return
        if key == keyboard.Key.f9 or key == keyboard.Key.esc: return
        try: k = key.char
        except: k = str(key).split('.')[-1]
        self.add_rec_event({'type': 'key', 'key': k})
        
    def add_rec_event(self, evt):
        now = time.time()
        evt['delay'] = round(now - self.last_time, 2)
        self.last_time = now
        self.script_data.append(evt)
        self.after(0, self.refresh_tree)
        
    def toggle_playback(self):
        if self.running and self.current_mode == 'playback': self.stop_all()
        else: self.start_playback()
        
    def start_playback(self):
        if not self.script_data: return
        self.running = True; self.current_mode = 'playback'
        self.update_ui_state('running')
        threading.Thread(target=self.playback_thread, daemon=True).start()
        
    def global_hotkey_listener(self):
        with keyboard.GlobalHotKeys({
            '<f8>': lambda: self.after(0, self.toggle_clicker),
            '<f9>': lambda: self.after(0, self.toggle_record),
            '<f10>': lambda: self.after(0, self.toggle_playback),
            '<esc>': lambda: self.after(0, self.stop_all)
        }) as h: h.join()
        
    def toggle_clicker(self):
        if self.tabview.get() == "简单连点器":
            if self.running: self.stop_all()
            else: self.start_clicker()
            
    def stop_all(self):
        self.running = False
        if hasattr(self, 'mouse_listener'): self.mouse_listener.stop()
        if hasattr(self, 'key_listener'): self.key_listener.stop()
        self.update_ui_state('stopped')
        # 恢复状态栏文字
        self.on_tab_change()
        
    def update_ui_state(self, state):
        if state == 'running':
            self.btn_clicker_start.configure(state="disabled")
            self.btn_clicker_stop.configure(state="normal")
            self.btn_record.configure(text="⏹ 停止 (F9)", fg_color="#D32F2F")
            self.btn_play.configure(text="⏹ 停止 (F10)", fg_color="#D32F2F")
        else:
            self.btn_clicker_start.configure(state="normal")
            self.btn_clicker_stop.configure(state="disabled")
            self.btn_record.configure(text="🔴 开始录制 (F9)", fg_color="#C62828")
            self.btn_play.configure(text="▶ 开始回放 (F10)", fg_color="#2E7D32")
            
    def save_script(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'w') as f: json.dump(self.script_data, f, indent=2)
            
    def load_script(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'r') as f: self.script_data = json.load(f)
            self.refresh_tree()

if __name__ == "__main__":
    app = AutoClickerApp()
    app.protocol("WM_DELETE_WINDOW", lambda: (app.stop_all(), app.destroy()))
    app.mainloop()
