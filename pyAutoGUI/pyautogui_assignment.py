import time
import pyautogui
import keyboard
import pyperclip
from datetime import datetime

# Playlist names with unique suffix if exists
date_tag = datetime.now().strftime("%Y%m%d_%H%M")
playlist_cooking = f"Cooking_{date_tag}"    
playlist_others = f"Others_{date_tag}"

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

def create_playlist(name):
    pyperclip.copy(name)
    pyautogui.hotkey('shift','p')  
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')  

def add_to_playlist(name):
    pyperclip.copy(name)
    pyautogui.hotkey('shift', 'p') 
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    time.sleep(0.5)


print("✅ Starting YouTube sorter script.")
print("➡️ Go to YouTube > History > Filter Last 4 weeks manually.")
print("➡️ Play FULL SCREEN mode browser.")
print("➡️ Scroll slowly.")
print("🎯 Press 'c' when you hover mouse on a cooking video.")
print("🎯 Press 'o' when you hover mouse on any other video.")
print("❌ Press 'q' to quit.\n")
time.sleep(5)

# Create playlists
create_playlist(playlist_cooking)
create_playlist(playlist_others)

print(f"✅ Playlists created:\n   - {playlist_cooking}\n   - {playlist_others}\n")

while True:
    if keyboard.is_pressed('c'):
        print("🍳 Cooking video detected → assigning")
        add_to_playlist(playlist_cooking)

    if keyboard.is_pressed('o'):
        print("📦 Other video detected → assigning")
        add_to_playlist(playlist_others)

    if keyboard.is_pressed('q'):
        print("❌ Exiting.")
        break

    time.sleep(0.2)
