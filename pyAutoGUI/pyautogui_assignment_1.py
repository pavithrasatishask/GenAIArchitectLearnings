import pyautogui
import time
from datetime import datetime, timedelta

# Define screen coordinates (example placeholders, update based on your screen)
email_start_pos = (200, 300)  # First email in list
email_gap_y = 40  # vertical gap between emails
label_button_pos = (1200, 200)  # Label button position in Gmail UI
label_search_box_pos = (1250, 250)
apply_label_pos = (1250, 300)  # Position of the label checkbox in dropdown
close_label_menu_pos = (1300, 180)

# Define number of emails to process (adjust based on inbox size)
emails_to_process = 20  

# Labels you want to apply based on some logic (dummy example)
def decide_label(subject_text):
    subject_text = subject_text.lower()
    if 'invoice' in subject_text or 'payment' in subject_text:
        return "Finance"
    elif 'meeting' in subject_text or 'project' in subject_text:
        return "Work"
    else:
        return "Personal"

# Main automation loop
for i in range(emails_to_process):
    # Calculate email position to click
    x, y = email_start_pos[0], email_start_pos[1] + i * email_gap_y

    # Click the email to open or select it
    pyautogui.click(x, y)
    time.sleep(2)  # wait for email to load

    # Ideally here you'd capture the subject text from screen or use OCR (not easy with PyAutoGUI alone)
    # For demonstration, let's assume subject_text is fetched or static
    subject_text = input(f"Enter subject for email {i + 1}: ")  # manual input prompt to simulate

    label_to_apply = decide_label(subject_text)
    print(f"Applying label: {label_to_apply}")

    # Click label button
    pyautogui.click(label_button_pos)
    time.sleep(1)

    # Click search box in label dropdown and type label name
    pyautogui.click(label_search_box_pos)
    pyautogui.write(label_to_apply, interval=0.1)
    time.sleep(2)

    # Click on the label checkbox (you may need to fine-tune this)
    pyautogui.click(apply_label_pos)
    time.sleep(1)

    # Close label menu
    pyautogui.click(close_label_menu_pos)
    time.sleep(1)

    # Optional: go back to inbox (if email opened separately)
    pyautogui.hotkey('ctrl', 'esc')  # example shortcut, confirm on your system

    # Small pause between emails
    time.sleep(2)
