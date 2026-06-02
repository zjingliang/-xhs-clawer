import shutil
import winreg
import os


def find_chrome_path():
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            key = winreg.OpenKey(
                hive,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
            )
            path = winreg.QueryValue(key, "")
            winreg.CloseKey(key)
            if path and os.path.isfile(path):
                return path
        except OSError:
            pass
    path = shutil.which("chrome")
    if path and os.path.isfile(path):
        return path
    return None
