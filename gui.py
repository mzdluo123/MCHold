import tkinter as tk
from actions import get_mc_info, suspend_minecraft, resume_minecraft,check_window_visible,get_process_memory_info

class Ui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MC休眠助手")
        # self.root.resizable(False,False)
        self.root.attributes("-toolwindow", 3)
        self.root.wm_attributes('-topmost', 1)
        self.left_panel = tk.Frame(self.root, bg="lightgray", padx=10, pady=50)
        self.left_panel.pack(side=tk.TOP, fill=tk.Y)
        self.label1 = tk.Label(self.left_panel, text="文本信息1",anchor="w")
        self.label1.pack()
        self.label2 = tk.Label(self.left_panel, text="文本信息2",anchor="w")
        self.label2.pack()

        self.label_window_visible = tk.Label(self.left_panel, text="文本信息2",anchor="w")
        self.label_window_visible.pack()
        self.label_memory = tk.Label(self.left_panel, text="label_memory",anchor="w")
        self.label_memory.pack()
        # self.refresh_button = tk.Button(self.root, text="刷新", command=self.refresh_panel)
        # self.refresh_button.pack()
        self.button1 = tk.Button(self.root, text="挂起", command=self.suspend_callback)
        self.button1.pack(side=tk.LEFT, padx=10, pady=10)
        self.button2 = tk.Button(self.root, text="恢复", command=self.resume_callback)
        self.button2.pack(side=tk.RIGHT, padx=10, pady=10)
        self.refresh_panel()

    def lock_all_btn(self):
        self.button1.config(state="disabled")
        self.button2.config(state="disabled")
        #self.refresh_button.config(state="disabled")

    def unlock_all_btn(self):
        self.button1.config(state="normal")
        self.button2.config(state="normal")
        #self.refresh_button.config(state="normal")

    def refresh_panel(self):
        try:
            self.info = get_mc_info()
            self.label1.config(text=self.info.title)
            self.label2.config(text=f"PID: {self.info.pid}")
            count = get_process_memory_info(self.info.pid)
            working = count["WorkingSetSize"] / 1024 / 1024
            self.label_memory.config(text=f"物理内存占用: {round(working)}MB")
            if check_window_visible(self.info.hwnd):
                self.label_window_visible.config(text="窗口可见")
            else:
                self.label_window_visible.config(text="窗口不可见")
        except Exception as e:
            self.label1.config(text="未找到Minecraft进程")
            self.label2.config(text="")
            self.label_window_visible.config(text="")
            self.label_memory.config(text="")
            self.info = None


    def suspend_callback(self):
        if self.info is None:
            return
        try:
            self.lock_all_btn()
            if check_window_visible(self.info.hwnd):
                suspend_minecraft(self.info)
        finally:
            self.refresh_panel()
            self.unlock_all_btn()

    def resume_callback(self):
        if self.info is None:
            return
        try:
            self.lock_all_btn()
            if not check_window_visible(self.info.hwnd):
                resume_minecraft(self.info)
        finally:
            self.refresh_panel()
            self.unlock_all_btn()

    def refresh_timer(self):
        self.refresh_panel()
        self.root.after(2000, self.refresh_timer)

    def run(self):
        self.root.after(2000, self.refresh_timer)
        self.root.mainloop()

if __name__ == "__main__":
    ui = Ui()
    ui.run()

