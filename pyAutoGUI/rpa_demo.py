import pyautogui
import time
print("We are starting with RPA Automation using PyAutoGUI library")

#Mouse Operations
#tripe quotes to comment multiple lines
pyautogui.click(100, 100)
pyautogui.rightClick(150,150)  
pyautogui.doubleClick(200,200)
pyautogui.leftClick(300,300)

time.sleep(3)
x, y = pyautogui.position()
print(f"The current mouse pointer position is: X={x}, Y={y}")
pyautogui.doubleClick(x,y)

time.sleep(3)
c, d = pyautogui.position()
print(f"The current mouse pointer position is: X={c}, Y={d}")
a, b = pyautogui.position() 
print(f"The current mouse pointer position is: X={a}, Y={b}")

pyautogui.moveTo(c, d, duration=1) #Move cursor to a,b
#pyautogui.dragTo(a, b, duration=1) #Drag cursor to c,d while holding mouse button

#pyautogui.scroll(500)
#pyautogui.scrollup(500) #AttributeError: module 'pyautogui' has no attribute 'scrollup'. Did you mean: 'scroll'?
#pyautogui.scrolldown(500) #AttributeError: module 'pyautogui' has no attribute 'scrolldown'. Did you mean: 'scroll'?


#Keyboard Operations
#pyautogui.write("Hello, welcome to RPA Automation using PyAutoGUI library") #type where the cursor is placed
#pyautogui.press("enter") #press the enter key or move the cursor to next line
#pyautogui.typewrite("hello") #similar to write type the text where the cursor is placed  
#pyautogui.press("enter") #press the enter key
time.sleep(3)
s,t = pyautogui.position()
pyautogui.moveTo(s,t, duration=1)
pyautogui.hotkey('ctrl', 'a') #Select all text

#for Image validation install "pip install opencv-python"
location = pyautogui.locateonscreen('image.png', confidence=0.8) #gives the box coordinates of the sample image on the screen. image file should be in the same directory.
print(location)
time.sleep(2)
pyautogui.click(pyautogui.center(location)) #clicks on the center of the image found on the screen
print(pyautogui.size())

screenshot = pyautogui.screenshot('screenshot.png') #takes screenshot and saves in the current directory with the given name
#(or) 
#screenshot = pyautogui.screenshot()
#screenshot.save('screenshot1.png') #saves the screenshot with a different name