import json
import os
import time
import re 
from datetime import datetime
from typing import List, Dict, Any
import platform 
import threading 

try:
    import eel
    eel.init('web') 
except ImportError:
    eel = None

try:
    from pynput import keyboard
except ImportError:
    keyboard = None

IS_LINUX = False
try:
    from Xlib.display import Display
    if platform.system() == "Linux":
        IS_LINUX = True
except ImportError:
    pass 

if platform.system() == "Windows":
    try:
        import ctypes
        import ctypes.wintypes
        IS_WINDOWS = True
    except ImportError:
        IS_WINDOWS = False
else:
    IS_WINDOWS = False

DATA_FILE = 'media_data.json'
CONFIG_FILE = 'tracker_config.json' 
GLOBAL_DATA = []

is_program_active = True 

is_hotkey_listener_running = False
is_auto_tracking_active = False 
AUTO_TRACKING_INTERVAL_SECONDS = 10 
CYCLES_PER_MINUTE = 6 

last_tracking_time = None 
last_tracked_title = ""
tracking_cycle_counter = 0 

CONFIG = {
    'blacklist_keywords': [
        "Terminal", "Settings", "Visual Studio Code", "PyCharm", "IntelliJ", "Photoshop",
        "Control Panel", "System Preferences", "Explorer", "Finder", "File Manager",
        "Slack", "Discord", "Zoom Meeting", "Gmail", "WhatsApp", "Outlook", 
        "Tracker GUI", "Desktop", "Windows", "Google", "Mozilla", "Error", "Notification",
        "Popup", "Terminal", "System", "Settings", "Tools", "Help", "About",
        "Installer", "Setup", "Control", "Manager", "License", "Configuration",
        "Security", "Task Manager"
    ],
    'is_auto_tracking_active': False,
    'is_program_active': True,
    'language': 'fa'
}

def load_data():
    global GLOBAL_DATA
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                GLOBAL_DATA = json.load(f)
            except json.JSONDecodeError:
                GLOBAL_DATA = []
    else:
        GLOBAL_DATA = []

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(GLOBAL_DATA, f, indent=4, ensure_ascii=False)

def load_config():
    global CONFIG, is_auto_tracking_active, is_program_active
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            try:
                loaded_config = json.load(f)
                CONFIG.update(loaded_config)
                is_auto_tracking_active = CONFIG.get('is_auto_tracking_active', False)
                is_program_active = CONFIG.get('is_program_active', True)
            except json.JSONDecodeError:
                pass
    else:
        save_config()

def save_config():
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(CONFIG, f, indent=4, ensure_ascii=False)

def get_current_window_title():
    if not is_program_active:
        return ""
        
    try:
        if IS_WINDOWS:
            hwnd = ctypes.wintypes.HWND(ctypes.windll.user32.GetForegroundWindow())
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            return buf.value.strip()
        elif IS_LINUX:
            d = Display()
            w = d.get_input_focus().focus
            title = w.get_wm_name()
            if not title:
                title = w.query_tree().parent.get_wm_name()
            d.close()
            return title.strip() if title else ""
        elif platform.system() == "Darwin": 
            return os.popen("""/usr/bin/osascript -e 'tell application "System Events" to get name of first process whose frontmost is true'""").read().strip()
        else:
            return ""
    except Exception:
        return ""

def is_title_blacklisted(title):
    if not title:
        return True
    
    current_title_lower = title.lower()
    
    for keyword in CONFIG['blacklist_keywords']:
        if keyword.lower() in current_title_lower:
            return True
        
    return False

def clean_title_and_extract_episode(title: str) -> tuple[str, str]:
    if not title:
        return "", ""
        
    episode = ""
    clean_title = title

    episode_match = re.search(r'E\d+|S\d+E\d+|قسمت\s*\d+|فصل\s*\d+\s*قسمت\s*\d+|\b\d+\b', title, re.IGNORECASE)
    if episode_match:
        episode = episode_match.group(0).strip()
        clean_title = re.sub(r'\s*(\[.*?\]|\(.*?\)|E\d+|S\d+E\d+|قسمت\s*\d+|فصل\s*\d+\s*قسمت\s*\d+|\b\d+\b)', '', clean_title, flags=re.IGNORECASE).strip()

    title_parts = clean_title.split(' - ')
    if len(title_parts) > 1:
        clean_title = title_parts[-1].strip()

    clean_title = clean_title.split(' | ')[0].strip()

    return clean_title, episode

def record_progress(title: str, episode: str = "", stop_time: str = None, time_spent_minutes: float = 0.0):
    global GLOBAL_DATA
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    existing_item = next((item for item in GLOBAL_DATA if item['title'] == title), None)
    
    if existing_item:
        existing_item['last_updated'] = now
        existing_item['total_minutes_watched'] = existing_item.get('total_minutes_watched', 0.0) + time_spent_minutes
        
        if episode:
            existing_item['episode'] = episode
        if stop_time is not None: 
            existing_item['stop_time'] = stop_time
        
    else:
        new_item = {
            'title': title,
            'episode': episode,
            'stop_time': stop_time,
            'is_finished': False,
            'total_minutes_watched': time_spent_minutes,
            'last_updated': now
        }
        GLOBAL_DATA.append(new_item)
        
    save_data()

@eel.expose
def get_progress_data():
    load_data()
    return GLOBAL_DATA

@eel.expose
def get_item_details_by_title(title: str) -> Dict[str, Any] | None:
    load_data()
    item = next((item for item in GLOBAL_DATA if item['title'] == title), None)
    if item:
        return item.copy()
    return None

@eel.expose
def get_stats_summary():
    load_data()
    total_items = len(GLOBAL_DATA)
    in_progress_items = sum(1 for item in GLOBAL_DATA if not item.get('is_finished'))
    finished_items = total_items - in_progress_items
    
    total_time_minutes = sum(item.get('total_minutes_watched', 0) for item in GLOBAL_DATA)
    
    hours = int(total_time_minutes // 60)
    minutes = int(total_time_minutes % 60)
    
    total_time_tracked = f"{hours}h {minutes}m"
    
    return {
        'total_items': total_items,
        'in_progress_items': in_progress_items,
        'finished_items': finished_items,
        'total_time_tracked': total_time_tracked
    }

@eel.expose
def mark_item_as_finished_by_title(title: str) -> bool:
    load_data()
    item = next((item for item in GLOBAL_DATA if item['title'] == title), None)
    if item:
        item['is_finished'] = True
        item['episode'] = "" 
        item['stop_time'] = None 
        item['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_data()
        return True
    return False

@eel.expose
def delete_item_by_title(title: str) -> bool:
    global GLOBAL_DATA
    load_data()
    initial_length = len(GLOBAL_DATA)
    GLOBAL_DATA = [item for item in GLOBAL_DATA if item['title'] != title]
    if len(GLOBAL_DATA) < initial_length:
        save_data()
        return True
    return False

@eel.expose
def save_manual_progress(title: str, episode: str, stop_time: str) -> bool:
    load_data()
    if not title:
        return False
        
    existing_item = next((item for item in GLOBAL_DATA if item['title'] == title), None)
    
    if existing_item:
        existing_item['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        existing_item['episode'] = episode.strip()
        existing_item['stop_time'] = stop_time.strip() or None 
        if existing_item.get('is_finished'):
             existing_item['is_finished'] = False
             
    else:
        record_progress(title.strip(), episode.strip(), stop_time.strip(), time_spent_minutes=0.0)
        
    save_data()
    return True

@eel.expose
def get_blacklist_keywords():
    load_config()
    return CONFIG['blacklist_keywords']

@eel.expose
def add_blacklist_keyword(keyword: str) -> bool:
    load_config()
    keyword = keyword.strip()
    if keyword and keyword not in CONFIG['blacklist_keywords']:
        CONFIG['blacklist_keywords'].append(keyword)
        save_config()
        if eel:
            try:
                eel.update_blacklist_display(CONFIG['blacklist_keywords'])
            except AttributeError:
                pass
        return True
    return False 

@eel.expose
def remove_blacklist_keyword(keyword: str) -> bool:
    load_config()
    keyword = keyword.strip()
    if keyword in CONFIG['blacklist_keywords']:
        CONFIG['blacklist_keywords'].remove(keyword)
        save_config()
        if eel:
            try:
                eel.update_blacklist_display(CONFIG['blacklist_keywords'])
            except AttributeError:
                pass
        return True
    return False

@eel.expose
def get_program_status():
    load_config()
    return {
        'is_program_active': is_program_active,
        'is_auto_tracking_active': is_auto_tracking_active
    }

@eel.expose
def toggle_program_active():
    global is_program_active, CONFIG
    
    is_program_active = not is_program_active
    
    CONFIG['is_program_active'] = is_program_active
    
    save_config()

    if eel:
        try:
            eel.update_program_status(is_program_active)
        except AttributeError:
            pass
    
    return is_program_active

def auto_tracking_loop():
    global last_tracking_time, last_tracked_title, tracking_cycle_counter
    
    while True:
        if is_program_active and is_auto_tracking_active:
            
            current_title = get_current_window_title()
            
            if current_title and not is_title_blacklisted(current_title):
                
                title, auto_episode = clean_title_and_extract_episode(current_title)
                current_time = time.time()
                
                if last_tracking_time is not None and title == last_tracked_title:
                    time_spent_seconds = current_time - last_tracking_time
                    time_spent_minutes = time_spent_seconds / 60
                    tracking_cycle_counter += 1
                    
                    record_progress(title, auto_episode, stop_time=None, time_spent_minutes=time_spent_minutes)
                    
                elif title != last_tracked_title:
                    
                    if last_tracked_title:
                        pass
                        
                    record_progress(title, auto_episode, stop_time=None, time_spent_minutes=0.0) 
                    
                last_tracking_time = current_time
                last_tracked_title = title
                
            else:
                last_tracking_time = None
                last_tracked_title = ""
                tracking_cycle_counter = 0
            
        else:
            last_tracking_time = None
            last_tracked_title = ""
            tracking_cycle_counter = 0
            
        time.sleep(AUTO_TRACKING_INTERVAL_SECONDS)

@eel.expose
def toggle_auto_tracking():
    global is_auto_tracking_active, CONFIG
    
    is_auto_tracking_active = not is_auto_tracking_active
    
    CONFIG['is_auto_tracking_active'] = is_auto_tracking_active
    
    save_config()

    if eel:
        try:
            eel.update_tracking_status(is_auto_tracking_active)
        except AttributeError:
            pass
    
    return is_auto_tracking_active
    
if __name__ == "__main__":
    load_config() 
    
    if eel:
        
        auto_tracking_thread = threading.Thread(target=auto_tracking_loop, daemon=True)
        auto_tracking_thread.start()
        
        try:
            eel.start('index.html', size=(800, 600))
        except Exception as e:
            print(f"Eel startup failed: {e}")
