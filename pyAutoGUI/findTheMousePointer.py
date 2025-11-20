import pyautogui  # type: ignore
import time

time.sleep(5)  # Give user 2 seconds to switch to the desired screen
x1, y1 = pyautogui.position()
time.sleep(5) 
"""x2, y2 = pyautogui.position()
time.sleep(5) 
x3, y3 = pyautogui.position()
time.sleep(5) 
x4, y4 = pyautogui.position()
time.sleep(5) 
x5, y5 = pyautogui.position()
time.sleep(5) 
x6, y6 = pyautogui.position()
time.sleep(5) """
print(f"The current mouse pointer position is: X={x1}, Y={y1}")
"""print(f"The current mouse pointer position is: X={x2}, Y={y2}")
print(f"The current mouse pointer position is: X={x3}, Y={y3}")
print(f"The current mouse pointer position is: X={x4}, Y={y4}")
print(f"The current mouse pointer position is: X={x5}, Y={y5}")
print(f"The current mouse pointer position is: X={x6}, Y={y6}")

positions = {
    "add_expense": (539, 337),
    "category": (143, 229),
    "expense_tab": (104, 270),
    "income_tab": (186, 270),
    "date": (336, 229),
    "notes": (569, 229),
    "label": (794, 229),
    "amount": (988, 229),
    "add_transaction": (1081, 294)
}

The current mouse pointer position is: X=539, Y=337
The current mouse pointer position is: X=619, Y=456
The current mouse pointer position is: X=887, Y=462
The current mouse pointer position is: X=1091, Y=460
The current mouse pointer position is: X=1518, Y=445
The current mouse pointer position is: X=1747, Y=443

Close Button: (86, 145)
Closes the add transaction popup
Category Dropdown: (143, 229)
Label: "Select category..."
When clicked, shows three tabs:
Expenses tab: (104, 270)
Income tab: (186, 270)
Transfer tab: (268, 270)
Date Field: (336, 229)
Default value: "07/11/2025"
Format: DD/MM/YYYY
Note Field: (569, 229)
Placeholder: "Write note"
Optional field
Label Dropdown: (794, 229)
Placeholder: "Select labels..."
Optional field
Amount Field: (988, 229)
Number input field
Default value: -0.00
Currency Dropdown: (1113, 229)
Default: "INR"
Attachment/Choose File Button: (779, 294)
For uploading receipts/attachments
Recurrence Dropdown: (816, 295)
Default: "Never"
Optional field
Keep Open Checkbox: Checkbox element (text label at 219, 301)
Text: "Keep open to add more transactions"
Add Transaction Button: (1081, 294)
Submit button (initially disabled until required fields are filled)
Close Popup (X) Button: (1186, 171)
Top-right corner close button

"""