import os
import platform

def get_paths():
    system = platform.system()
    if system == "Windows":
        appdata = os.getenv("APPDATA")
        return {
            'storage_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "storage.json"),
            'sqlite_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "state.vscdb"),
            'session_path': os.path.join(appdata, "Cursor", "Session Storage")
        }
    elif system == "Darwin":
        base = os.path.expanduser("~/Library/Application Support/Cursor")
        return {
            'storage_path': os.path.join(base, "User/globalStorage/storage.json"),
            'sqlite_path': os.path.join(base, "User/globalStorage/state.vscdb"),
            'session_path': os.path.join(base, "Session Storage")
        }
    elif system == "Linux":
        home = os.path.expanduser("~")
        for dirname in ["Cursor", "cursor"]:
            path = os.path.join(home, ".config", dirname)
            if os.path.exists(path):
                return {
                    'storage_path': os.path.join(path, "User/globalStorage/storage.json"),
                    'sqlite_path': os.path.join(path, "User/globalStorage/state.vscdb"),
                    'session_path': os.path.join(path, "Session Storage")
                }
    return None
