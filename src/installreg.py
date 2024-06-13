import winreg as reg
import os
import shutil
import sys
import tkinter as tk
from tkinter import messagebox
import win32com.client as client


def add_to_context_menu():
    exe_files = ["main.exe"]
    target_dir = r"C:\Program Files\Bitsology"
    os.makedirs(target_dir, exist_ok=True)

    for exe in exe_files:
        source_path = os.path.join(os.getcwd(), exe)
        target_path = os.path.join(target_dir, "Bitsology.exe")
        if os.path.exists(target_path):
            os.remove(target_path)
        if os.path.exists(source_path):
            shutil.move(source_path, target_path)
            shortcut_path = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Bitsology.lnk')
            shell = client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target_path
            shortcut.WorkingDirectory = os.path.dirname(target_path)
            shortcut.save()
            messagebox.showinfo("Success", "main.exe moved and renamed to Bitsology.exe successfully in Program Files.")
        else:
            messagebox.showerror("Error", "main.exe does not exist in the current directory.")
    
    app_path = os.path.join(target_dir, "Bitsology.exe")
    key_path = r"SystemFileAssociations\image\shell\Open in Bitsology"
    command = f'"{app_path}" "%1"'
    try:
        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, key_path)
        reg.SetValue(key, 'command', reg.REG_SZ, command)
        reg.CloseKey(key)
        messagebox.showinfo("Success", "Context menu item added successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add context menu item: {e}")

    # Move this script to the program folder
    self_path = os.path.abspath(sys.argv[0])
    new_self_path = os.path.join(target_dir, os.path.basename(self_path))
    shutil.move(self_path, new_self_path)

def remove_from_context_menu():
    key_path = r"SystemFileAssociations\image\shell\Open in Bitsology"
    try:
        reg.DeleteKey(reg.HKEY_CLASSES_ROOT, key_path + r'\command')
        reg.DeleteKey(reg.HKEY_CLASSES_ROOT, key_path)
        messagebox.showinfo("Success", "Context menu item removed successfully.")
    except FileNotFoundError:
        messagebox.showwarning("Warning", "Context menu item not found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to remove context menu item: {e}")

def remove_application():
    target_path = r"C:\Program Files\Bitsology\Bitsology.exe"
    target_path2 = r"C:\Program Files\Bitsology\installreg.exe"
    shortcut_path = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Bitsology.lnk')

    try:
        if os.path.exists(target_path):
            os.remove(target_path)
            shutil.rmtree(os.path.dirname(target_path), ignore_errors=True)
            messagebox.showinfo("Success", "Bitsology.exe removed successfully from Program Files.")
        else:
            messagebox.showwarning("Warning", "Bitsology.exe not found in Program Files.")
        if os.path.exists(target_path2):
            os.remove(target_path2)
            shutil.rmtree(os.path.dirname(target_path2), ignore_errors=True)
            messagebox.showinfo("Success", "installreg.exe removed successfully from Program Files.")
        else:
            messagebox.showwarning("Warning", "installreg.exe not found in Program Files.")
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to remove Bitsology.exe: {e}")

    try:
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            messagebox.showinfo("Success", "Shortcut removed successfully from Start Menu.")
        else:
            messagebox.showwarning("Warning", "Shortcut not found in Start Menu.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to remove shortcut: {e}")

def on_install():
    add_to_context_menu()

def on_uninstall():
    remove_from_context_menu()
    remove_application()

def create_gui():
    root = tk.Tk()
    root.title("Bitsology Setup")

    install_button = tk.Button(root, text="Install/Update", command=on_install)
    install_button.pack(pady=10)

    uninstall_button = tk.Button(root, text="Uninstall", command=on_uninstall)
    uninstall_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()