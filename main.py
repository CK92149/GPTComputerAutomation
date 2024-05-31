import os
import base64
import requests
from PIL import ImageGrab
import pyautogui
import tkinter as tk
from tkinter import scrolledtext
import re
import comtypes.client
import json
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the COM library
comtypes.CoInitialize()

# Load the UIAutomation type library
uiautomation = comtypes.client.GetModule('UIAutomationCore.dll')

# Import the generated module
import comtypes.gen.UIAutomationClient as UIA

# Create the CUIAutomation object
uiautomation = comtypes.client.CreateObject(UIA.CUIAutomation)

# Get the root element (the desktop)
root_element = uiautomation.GetRootElement()

# Function to get the control type name
def get_control_type_name(control_type):
    control_types = {
        50000: "Button",
        50001: "Calendar",
        50002: "CheckBox",
        50003: "ComboBox",
        50004: "Edit",
        50005: "Hyperlink",
        50006: "Image",
        50007: "ListItem",
        50008: "List",
        50009: "Menu",
        50010: "MenuBar",
        50011: "MenuItem",
        50012: "ProgressBar",
        50013: "RadioButton",
        50014: "ScrollBar",
        50015: "Slider",
        50016: "Spinner",
        50017: "StatusBar",
        50018: "Tab",
        50019: "TabItem",
        50020: "Text",
        50021: "ToolBar",
        50022: "ToolTip",
        50023: "Tree",
        50024: "TreeItem",
        50025: "Custom",
        50026: "Group",
        50027: "Thumb",
        50028: "DataGrid",
        50029: "DataItem",
        50030: "Document",
        50031: "SplitButton",
        50032: "Window",
        50033: "Pane",
        50034: "Header",
        50035: "HeaderItem",
        50036: "Table",
        50037: "TitleBar",
        50038: "Separator",
        50039: "SemanticZoom",
        50040: "AppBar"
    }
    return control_types.get(control_type, "Unknown")

# Function to recursively print visible clickable UI elements with their coordinates
def print_ui_elements(element, depth=0, output_file=None):
    try:
        # Get the element runtime ID
        runtime_id = element.GetRuntimeId()
        if runtime_id in visited_elements:
            return
        visited_elements.add(runtime_id)

        # Check if the element is visible and is a clickable control type
        if not element.CurrentIsOffscreen:
            control_type = element.CurrentControlType
            if control_type in [50000, 50005, 50011]:  # Button, Hyperlink, MenuItem
                name = element.CurrentName
                control_type_name = get_control_type_name(control_type)
                bounding_rectangle = element.CurrentBoundingRectangle
                output = {
                    "Name": name,
                    "ControlType": control_type_name,
                    "Coordinates": {
                        "left": bounding_rectangle.left,
                        "top": bounding_rectangle.top,
                        "right": bounding_rectangle.right,
                        "bottom": bounding_rectangle.bottom
                    }
                }
                if output_file:
                    output_file.write(str(output) + "\n")
                else:
                    print(output)

        # Get all child elements
        children = element.FindAll(UIA.TreeScope_Children, uiautomation.CreateTrueCondition())
        for i in range(children.Length):
            child = children.GetElement(i)
            print_ui_elements(child, depth + 1, output_file)
    except comtypes.COMError as e:
        error_message = f"COMError at depth {depth}, Error: {e}"
        if output_file:
            output_file.write(error_message + "\n")
        else:
            print(error_message)
    except Exception as e:
        error_message = f"Exception at depth {depth}, Error: {e}"
        if output_file:
            output_file.write(error_message + "\n")
        else:
            print(error_message)

# Function to capture UI elements and save them to a file
def capture_ui_elements():
    global visited_elements
    visited_elements = set()  # Reset the visited elements set
    with open('ui_elements.txt', 'w') as output_file:
        print_ui_elements(root_element, output_file=output_file)
    status_text.set("UI elements captured and saved to ui_elements.txt")

# Function to take a screenshot and save it as screenshot.png
def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    status_text.set("Screenshot taken and saved as screenshot.png")
    return "screenshot.png"

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to read ui_elements.txt file
def read_ui_elements():
    with open('ui_elements.txt', 'r') as file:
        return file.read()

# Function to handle the API request
def analyze_image(base64_image, ui_elements_text):
    user_input = user_input_entry.get()
    combined_text = hardcoded_text + user_input + hardcoded_text2

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('API_KEY')}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": combined_text + "\n" + ui_elements_text,
                "attachments": [
                    {
                        "type": "image",
                        "data": f"data:image/jpeg;base64,{base64_image}"
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = response.json()

    # Parse and format the response content
    assistant_message = response_data['choices'][0]['message']['content']
    
    # Display the formatted response in the text area
    response_text.delete(1.0, tk.END)
    response_text.insert(tk.END, assistant_message)
    status_text.set("Image analyzed. Click 'Perform Action' to execute the click action.")
    
    return assistant_message

# Function to perform the click action
def perform_click(assistant_message):
    try:
        # Extract the JSON part using regex
        match = re.search(r'```json\s*({[^}]*})\s*```', assistant_message)
        if match:
            json_str = match.group(1)
            coordinates = json.loads(json_str)

            # Extract coordinates from the JSON structure
            left = coordinates['left']
            top = coordinates['top']
            right = coordinates['right']
            bottom = coordinates['bottom']
            text = coordinates.get('text', '')

            # Calculate the center coordinates
            x_coord = (left + right) // 2
            y_coord = (top + bottom) // 2

            # Get the screen resolution
            screen_width, screen_height = pyautogui.size()

            # Get the resolution of the screenshot image
            screenshot_image = ImageGrab.grab()
            screenshot_width, screenshot_height = screenshot_image.size

            # Calculate the scaling factor
            x_scale = screen_width / screenshot_width
            y_scale = screen_height / screenshot_height

            # Adjust coordinates based on the scaling factor
            x_coord = int(x_coord * x_scale)
            y_coord = int(y_coord * y_scale)

            # Debug print statements
            print(f"Original Coordinates: ({left}, {top}, {right}, {bottom})")
            print(f"Screen Resolution: ({screen_width}, {screen_height})")
            print(f"Screenshot Resolution: ({screenshot_width}, {screenshot_height})")
            print(f"Scaling Factors: (x_scale: {x_scale}, y_scale: {y_scale})")
            print(f"Adjusted Coordinates: ({x_coord}, {y_coord})")

            # Validate coordinates
            if 0 <= x_coord <= screen_width and 0 <= y_coord <= screen_height:
                print(f"Moving to coordinates: ({x_coord}, {y_coord})")  # Debug print statement
                pyautogui.moveTo(x_coord, y_coord, duration=2.5)  # Adding duration to see the movement
                pyautogui.click()
                time.sleep(0.5)  # Ensuring click happens
                status_text.set(f"Mouse moved to ({x_coord}, {y_coord}) and clicked.")
                if text:  # If there is text to type
                    perform_typing(text)
            else:
                status_text.set(f"Coordinates ({x_coord}, {y_coord}) are out of screen bounds.")
        else:
            status_text.set("Failed to extract valid coordinates from the response.")
    except Exception as e:
        print(f"Error in perform_click: {e}")
        status_text.set("An error occurred while performing the click action.")

# Function to perform the typing action
def perform_typing(text):
    try:
        pyautogui.typewrite(text, interval=0.1)
        status_text.set(f"Typed text: {text}")
    except Exception as e:
        print(f"Error in perform_typing: {e}")
        status_text.set("An error occurred while typing the text.")

# Function to handle the complete sequence
def perform_action():
    try:
        capture_ui_elements()  # Capture UI elements and save them to a file
        ui_elements_text = read_ui_elements()  # Read the UI elements from the file
        image_path = take_screenshot()
        base64_image = encode_image(image_path)
        assistant_message = analyze_image(base64_image, ui_elements_text)
        perform_click(assistant_message)
    except Exception as e:
        print(f"Error in perform_action: {e}")
        status_text.set("An error occurred while performing the action.")

# Hardcoded part of the text
hardcoded_text = "you have the ability to view screenshots. Decide the most likely next click to achieve the goal. User request: "
hardcoded_text2 = " --approximate x and y boundary box coordinates for the required mouse click in json. text = text to be potentially typed where needed. leave empty if no typing is needed (json{""left"": ,""top"": ,""right"": ,""bottom"": ,""text"": }) Always end the answer with the coordinates make sure to analyze the screenshot and ui_elements thoroughly before proceding. Only mention the next click, not multiple steps required."

# Create the main window
root = tk.Tk()
root.title("Image Analysis Tool")

# Create a label and entry for user input
tk.Label(root, text="What do you want me to do?:").pack(pady=5)
user_input_entry = tk.Entry(root, width=50)
user_input_entry.pack(pady=5)

# Create a button to perform the entire action
tk.Button(root, text="Perform Action", command=perform_action).pack(pady=10)

# Create a scrolled text area to display the response
response_text = scrolledtext.ScrolledText(root, width=80, height=20)
response_text.pack(pady=10)

# Create a label to display status messages
status_text = tk.StringVar()
status_label = tk.Label(root, textvariable=status_text)
status_label.pack(pady=5)

# Run the Tkinter event loop
root.mainloop()
