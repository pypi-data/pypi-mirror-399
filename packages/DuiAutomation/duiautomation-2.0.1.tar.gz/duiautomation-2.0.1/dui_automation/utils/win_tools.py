import ctypes
import os
import sys
import psutil


def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()


def admin_exec(exec_name, params, debug=False):
    ctypes.windll.shell32.ShellExecuteW(None, "runas", exec_name, params, None, 1 if debug else 0)


def try_admin(exec_name: str, params: str, debug=False):
    _is_admin = is_admin()
    if _is_admin:
        os.system(f"{exec_name} {params}")
    else:
        if sys.version_info[0] == 3:    # python3
            admin_exec(exec_name, params, debug)
        # else:                         # python2
        #     ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1)


def kill_process(pid: int, debug=False):
    try_admin(exec_name="taskkill", params=f"/F /T /PID {pid}", debug=debug)


if __name__ == '__main__':
    print(try_admin("hook", '"C:\Program Files (x86)\QiYou\QiYou.exe" -l D:\PyWorker\dlinject\win.js', debug=True))
    for proc in psutil.process_iter():
        if proc.name().startswith("hook"):
            print(proc.name())
            print(proc.pid)
            kill_process(proc.pid)
    # runAdmin('hook "C:\Program Files (x86)\QiYou\QiYou.exe" -l D:\PyWorker\dlinject\win.js')
    # win32process.CreateProcess('c:\\windows\\notepad.exe', '', None, None, 0, win32process.CREATE_NO_WINDOW, None, None, win32process.STARTUPINFO())
