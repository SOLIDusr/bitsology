import winreg as reg
from tkinter import messagebox
import win32com.client as client


def add_to_context_menu():
    # Path to your application
    import shutil
    import os

    # Locate main.exe in the current working directory
    source_path = os.path.join(os.getcwd(), "main.exe")
    # Define the target path in Program Files and rename to Bitsology.exe
    target_path = r"C:\Program Files\Bitsology\Bitsology.exe"
    # Check if Bitsology.exe already exists at the target path and delete if present
    if os.path.exists(target_path):
        os.remove(target_path)
    # Move and rename main.exe to Bitsology.exe in the target directory
    if os.path.exists(source_path):
        # Ensure the target directory exists, create if not
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        # Move and rename the file
        shutil.move(source_path, target_path)
        # Create a shortcut in the Start Menu Programs directory for easy access via Windows Search
        shortcut_path = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Bitsology.lnk')
        shell = client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.save()
        os.makedirs(os.path.dirname(target_path), exist_ok=True) 
        messagebox.showinfo("Success", "main.exe moved and renamed to Bitsology.exe successfully in Program Files.")
    else:
        messagebox.showerror("Error", "main.exe does not exist in the current directory.")
    app_path = r"C:\Program Files\Bitsology\Bitsology.exe"  # Update this to the path of your .exe
    
    # Registry key paths
    key_path = r"SystemFileAssociations\image\shell\Open in Bitsology"

    # Command to execute (open your app with the file as an argument)
    command = f'"{app_path}" "%1"'

    # Open the registry key and add values
    try:
        # Connect to the registry and create new keys
        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, key_path)
        reg.SetValue(key, 'command', reg.REG_SZ, command)
        reg.CloseKey(key)
        messagebox.showinfo("Success", "Context menu item added successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add context menu item: {e}")

if __name__ == "__main__":
    add_to_context_menu()