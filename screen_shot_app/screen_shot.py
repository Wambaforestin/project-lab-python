import time
import pyautogui
import random
import tkinter as ui

def screen_shot():
    time.sleep(3)
    image = pyautogui.screenshot()
    # generate a random name for the screenshot
    name = str(random.randint(0, 1000000))
    # Save the screenshot to the directory
    try:
        image.save(f"screenshots/{name}.png")
    except FileNotFoundError:
        print("Directory not found")
    # Display the screenshot
    image.show()
    

if __name__ == "__main__":
    # screen_shot()
    root = ui.Tk() # create a root window
    frame = ui.Frame(root) # create a frame in the root window
    frame.pack() # pack the frame in the root window
    
    # create a button in the frame
    button = ui.Button(
        frame,
        text="Take Screenshot",
        command=screen_shot, # call the screen_shot function when the button is clicked
        fg="green",
    )
    
    # pack the button in the frame
    button.pack(
        side=ui.LEFT    
    )
    
    # create a close button in the frame
    close_button = ui.Button(
        frame,
        text="Close",
        command=root.destroy,
        fg="red",
    )
    
    # pack the close button in the frame
    close_button.pack(
        side=ui.LEFT
    )
    
    # run the root window
    root.mainloop()
    
