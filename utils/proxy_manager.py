import winreg
import ctypes


INTERNET_OPTION_SETTINGS_CHANGED = 39
INTERNET_OPTION_REFRESH = 37


def _refresh_windows_proxy():
    ctypes.windll.Wininet.InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
    ctypes.windll.Wininet.InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)


def enable_proxy(host="127.0.0.1", port=8080):
    path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)

    winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
    winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, f"{host}:{port}")

    winreg.CloseKey(key)

    # 🔥 FORCE WINDOWS TO APPLY
    ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)
    ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)

    print("[+] Proxy enabled & applied")


def disable_proxy():
    path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)

    winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)

    winreg.CloseKey(key)

    ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)
    ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)

    print("[+] Proxy disabled")