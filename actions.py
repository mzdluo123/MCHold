
import win32gui
import win32api
import win32process
import win32con
import ctypes
import win32security

class MCInfo:
    def __init__(self):
        self.pid = 0
        self.path = ""
        self.title = ""
        self.hwnd = 0


def get_dbg_privilege():
    hToken = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY)
    id = win32security.LookupPrivilegeValue(None, win32security.SE_DEBUG_NAME)
    newPrivileges = [(id, win32security.SE_PRIVILEGE_ENABLED)]
    win32security.AdjustTokenPrivileges(hToken, 0, newPrivileges)

get_dbg_privilege()

def hide_window(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)


def show_window(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)


def enum_all_window_by_process(pid):
    def callback(hwnd, hwnds):
        if win32process.GetWindowThreadProcessId(hwnd)[1] == pid:
            # check window is mc
            text = win32gui.GetWindowText(hwnd)
            if "Minecraft" in text:
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds

def check_window_visible(hwnd):
    return win32gui.IsWindowVisible(hwnd)

def suspend_process(pid):
    hProcess = ctypes.windll.kernel32.OpenProcess(0x0800, False, pid)
    ret = ctypes.windll.ntdll.NtSuspendProcess(hProcess)
    ctypes.windll.kernel32.CloseHandle(hProcess)


def resume_process(pid):
    hProcess = ctypes.windll.kernel32.OpenProcess(0x0800, False, pid)
    ret = ctypes.windll.ntdll.NtResumeProcess(hProcess)
    ctypes.windll.kernel32.CloseHandle(hProcess)


def suspend_minecraft(info):
    hide_window(info.hwnd)
    clean_working_set(info.pid)
    suspend_process(info.pid)


def resume_minecraft(info):
    resume_process(info.pid)
    show_window(info.hwnd)

def get_process_memory_info(pid):
    hProcess = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
    count = win32process.GetProcessMemoryInfo(hProcess)
    win32api.CloseHandle(hProcess)
    return count

def clean_working_set(pid):
    hProcess = ctypes.windll.kernel32.OpenProcess(win32con.PROCESS_SET_QUOTA | win32con.PROCESS_QUERY_INFORMATION , False, pid)
    ctypes.windll.psapi.EmptyWorkingSet(hProcess)
    ctypes.windll.kernel32.CloseHandle(hProcess)

def get_mc_info():
    mcinfo = MCInfo()
    try:
        def windows(hwnd, mcinfo):
            text = win32gui.GetWindowText(hwnd)
            if "Minecraft" in text:
                process_id = win32process.GetWindowThreadProcessId(hwnd)[1]
                proc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False,
                                            process_id)

                file_name = win32process.GetModuleFileNameEx(proc, 0)
                win32api.CloseHandle(proc)
                if file_name.endswith("java.exe"):
                    mcinfo.pid = process_id
                    mcinfo.path = file_name
                    mcinfo.title = text
                    raise StopIteration()
            return True

        win32gui.EnumWindows(windows, mcinfo)
    except StopIteration:
        pass
    mcinfo.hwnd = enum_all_window_by_process(mcinfo.pid)[0]
    return mcinfo


def main():
    mcinfo = get_mc_info()

    suspend_minecraft(mcinfo)
    resume_minecraft(mcinfo)

if __name__ == "__main__":
    main()
