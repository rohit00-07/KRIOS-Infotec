# automation.py
import time
import os
import pyautogui
import pyperclip
from pywinauto.application import Application
from pywinauto.findwindows import ElementNotFoundError

POWERBI_EXE_PATTERNS = [
    r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe",
    r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop_x64.exe"
]

def find_powerbi_exe():
    for p in POWERBI_EXE_PATTERNS:
        if os.path.exists(p):
            return p
    return None

def open_powerbi():
    exe = find_powerbi_exe()
    if not exe:
        raise FileNotFoundError("Cannot find Power BI Desktop exe. Update POWERBI_EXE_PATTERNS in automation.py.")
    Application().start(exe)
    time.sleep(8)  # wait for startup

def open_pbix(pbix_path):
    # Opens an existing PBIX using pywinauto or fallback to keyboard
    try:
        app = Application(backend="uia").connect(path="PBIDesktop.exe")
        window = app.top_window()
        window.set_focus()
        # Ctrl+O to open file
        pyautogui.hotkey('ctrl','o')
        time.sleep(1)
        # type path and press Enter
        pyperclip.copy(pbix_path)
        pyautogui.hotkey('ctrl','v')
        pyautogui.press('enter')
        time.sleep(5)
    except ElementNotFoundError:
        # fallback: open using os.startfile
        os.startfile(pbix_path)
        time.sleep(5)

def refresh_data():
    # Uses keyboard shortcut to refresh: Ctrl+R for Refresh?
    # (Power BI doesn't have universal Ctrl+R, so we do Home -> Refresh using keyboard)
    # Fallback: use Ribbon keys (Alt sequences)
    pyautogui.hotkey('alt','h')  # go to Home tab (may vary)
    time.sleep(0.5)
    # The exact key to refresh may vary; instruct user to calibrate if not working
    # We'll instead send Ctrl+F5 as a "refresh" attempt
    pyautogui.hotkey('ctrl','f5')
    time.sleep(3)

def load_csv_into_model(csv_path):
    # Simple approach: open Get Data dialog via Ribbon -> Text/CSV
    # Use Alt shortcut sequence: Alt H -> Get Data isn't consistent, so we use UI coordinates
    # USER MUST CALIBRATE coordinates for 'Get data' -> 'Text/CSV'
    # Replace these with actual coordinates for your machine.
    GET_DATA_BUTTON = (200, 95)  # example coords (x,y) — calibrate
    TEXT_CSV_ITEM = (300, 300)   # example coords in the dialog — calibrate
    OPEN_BUTTON = (1200, 900)    # example coords for file dialog -> Open button

    # Click Get Data
    pyautogui.click(GET_DATA_BUTTON)
    time.sleep(0.8)
    pyautogui.click(TEXT_CSV_ITEM)
    time.sleep(1.0)
    # In file dialog, paste path and press enter
    pyperclip.copy(csv_path)
    pyautogui.hotkey('ctrl','v')
    pyautogui.press('enter')
    time.sleep(2)

def create_bar_chart(x_column, y_column, dataset=None):
    """
    MVP approach:
     - Assumes dataset is loaded and visible in Fields pane on the right.
     - Steps:
       1. Click blank report canvas.
       2. Click "Clustered bar chart" visual icon in Visualizations pane (coordinate)
       3. Drag fields (or click checkboxes) in Fields pane to add to Axis and Values.
    """
    # Coordinates to be calibrated per machine:
    BLANK_CANVAS = (600, 400)
    VISUAL_BAR_ICON = (1100, 220)   # location of stacked/clustered bar icon in Visualizations pane
    FIELDS_PANE_REGION = (1400, 200) # rough area of Fields pane
    # Click canvas
    pyautogui.click(BLANK_CANVAS)
    time.sleep(0.4)
    # Click bar chart icon
    pyautogui.click(VISUAL_BAR_ICON)
    time.sleep(0.6)

    # The easiest reliable method: use search in Fields pane, select field via clicks
    # We'll open the Fields search (coordinates need calibration)
    FIELD_SEARCH = (1380, 120)
    pyautogui.click(FIELD_SEARCH)
    time.sleep(0.2)
    pyperclip.copy(x_column)
    pyautogui.hotkey('ctrl','v')
    time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(0.2)
    # First click found field (coordinate tuned)
    FIRST_FIELD_POS = (1380, 160)
    pyautogui.click(FIRST_FIELD_POS)  # this should add as a field (or click checkbox)
    time.sleep(0.4)

    # Add Y column similarly
    pyautogui.click(FIELD_SEARCH)
    pyperclip.copy(y_column)
    pyautogui.hotkey('ctrl','v')
    pyautogui.press('enter')
    time.sleep(0.2)
    pyautogui.click(FIRST_FIELD_POS)
    time.sleep(0.8)

    # If needed: move fields to Axis/Values via drag; but that's advanced — calibrate later.

def apply_filter(field, operator, value):
    # MVP: open Filters pane and type search — complex; left as placeholder
    print(f"apply_filter called: {field} {operator} {value}")
    # Implementation dependent on report layout; use pyautogui sequences here
    time.sleep(0.5)