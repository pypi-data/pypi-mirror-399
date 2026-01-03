import time
import sys
import subprocess
from threading import Thread

if sys.platform != "linux":
    from tkinter import Tk


class WindowCreator:
    def __init__(self):
        self.__processes = []
        self.__threads = []
        self.__windows = []

    def create_window(self, title, width=400, height=300, x=100, y=100):
        if sys.platform == "linux":
            return self.__create_yad_window(title, width, height, x, y)
        else:
            return self.__create_tkinter_window(title, width, height, x, y)

    def __create_yad_window(self, title, width, height, x, y):
        cmd = [
            'yad',
            '--title', title,
            '--width', str(width),
            '--height', str(height),
            '--posx', str(x),
            '--posy', str(y),
            '--text', 'Test Window',
            '--button', 'Close:0',
            '--buttons-layout', 'center',
            '--geometry', f'{width}x{height}+{x}+{y}',
            '--undecorated=false',
            '--skip-taskbar',
            '--sticky',
            '--on-top',
            '--center'  
        ]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        self.__processes.append(proc)
        time.sleep(1)

    def __create_tkinter_window(self, title, width, height, x, y):
        def run_window():
            window = Tk()
            window.title(title)
            window.geometry(f"{width}x{height}+{x}+{y}")
            self.__windows.append(window)
            window.update_idletasks()
            window.update()
            window.mainloop()

        thread = Thread(target=run_window, daemon=True)
        thread.start()
        self.__threads.append(thread)
        time.sleep(0.5)

    def cleanup(self):
        if sys.platform == "linux":
            for proc in self.__processes:
                proc.terminate()
                proc.wait(timeout=1)
                if proc.poll() is None:
                    proc.kill()
            
            subprocess.run(['pkill', '-f', 'yad'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
