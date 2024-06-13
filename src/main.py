import os
import subprocess
import sys
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
from picture import Picture
from encoder import Encoder
import configparser
import binascii
from version import Version


class App:

    def __init__(self, mode, systemArg=None) -> None:
        # pre-start update
        self.version = Version("v.1.3.1-r12")
        self.checkUpdates()
        try:
            if not os.path.exists("settings.properties"):
                self.createsettings()
            # end pre-start update
            # start load settings
            self.loadsettings()
        except PermissionError as e:
            self.rootdirectory = os.path.expanduser("~/AppData/Roaming/Bitsology/custom_enc.png")
        # end load settings
        # start gui init
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.geometry("500x400")

        self.root.title("Bitsology")
        self.encoder = Encoder()
        # end gui init
        # start mode check
        if mode == 1:
            self.systemArg = systemArg
            if messagebox.askquestion(title="Attention.", message="Use heavy encoding?") == "now":
                self.lightEncode(passlen=22, file=self.systemArg)
            else:
                self.heavyEncode(passlen=22, file=self.systemArg)
        else:
            self.systemArg = None
            self.guiInit()
        # end mode check
        

    def checkUpdates(self):
        repoUrl = "https://api.github.com/repos/SOLIDusr/Bitsology/releases/latest"
        try:
            response = requests.get(repoUrl)
            response.raise_for_status()
            latestVersion = Version(response.json()["tag_name"])
            match self.version.__eq__(latestVersion):
                case 5:
                    messagebox.showerror(f"New version available", f"New major version available, please update")
                case 4:
                    messagebox.showerror(f"New version available", f"New version available, please update")
                case 3:
                    messagebox.showerror("New patch available", "New patch available, please update")
                case 2:
                    messagebox.showerror("Warning!", "You are using a beta version.")
                case -1:
                    messagebox.showerror("Warning!", "You are using an unreleased version.")
                case _:
                    pass
            print(f"{self.version} -> {latestVersion}")

        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to check for updates: {e}")

    def createsettings(self):
        file = configparser.ConfigParser()
        file.add_section("Path Variables")
        file.set("Path Variables", "path", "~/AppData/Roaming/Bitsology/custom_enc.png")
        file.set("Path Variables", "root", "C:/Program Files/Bitsology")
        with open("C:/Program Files/Bitsology/settings.properties", "w") as f:
            file.write(f)
            f.close()

    def loadsettings(self):
        file = configparser.ConfigParser()
        file.read("C:/Program Files/Bitsology/settings.properties")
        self.rootdirectory = file.get("Path Variables", "path")

    def saverootdirectory(self):
        file = configparser.ConfigParser()
        file.read("settings.properties")
        file.set("Path Variables", "path", self.rootdirectory)
        with open("settings.properties", "w") as f:
            file.write(f)
            f.close()

    def copyToClipboard(self, text):
        process = subprocess.Popen(['clip.exe'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=text)

    def selectFile(self):
        filePath = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if not filePath:
            messagebox.showerror("Error", "No file selected")
            return
        return filePath

    def calculateWayAndFactorPixel(self, centerPixel):
        if isinstance(centerPixel, int):
            return centerPixel, centerPixel
        return sum(centerPixel), centerPixel[0]

    # GUI init

    def guiInit(self):
        try:
            leftUpperFrame = tk.Frame(self.root)
            leftUpperFrame.place(x=10, y=10, width=200, height=270)
            self.selectedFilePath = None
            self.fileToEncodeLabel = tk.Label(leftUpperFrame, text="Selected file", wraplength=100)
            self.fileToEncodeLabel.pack(pady=5)

            selectFileButton = tk.Button(leftUpperFrame, text="Select", command=self.selectFileButton)
            selectFileButton.pack(pady=5)

            heavyEncodeButton = tk.Button(leftUpperFrame, text="Heavy encode", command=lambda: self.heavyEncode(self.selectedFilePath if self.selectedFilePath else None, passwordLengthSlider.get()))
            heavyEncodeButton.pack(pady=5)

            lightEncodeButton = tk.Button(leftUpperFrame, text="Light encode", command=lambda: self.lightEncode(self.selectedFilePath if self.selectedFilePath else None, passwordLengthSlider.get()))
            lightEncodeButton.pack(pady=5)

            # Left bottom section
            rightFrame = tk.Frame(self.root)
            rightFrame.place(x=260, y=10, width=200, height=270)

            customEncodingKeyLabel = tk.Label(rightFrame, text="Custom Encoding Key")
            customEncodingKeyLabel.pack(pady=5)

            self.CustomKeyPathLabel = tk.Label(rightFrame, text=self.cutpath(self.rootdirectory), wraplength=100)
            self.CustomKeyPathLabel.pack(pady=5)

            selectPathButton = tk.Button(rightFrame, text="Select Path", command=self.selectKeyPathButton)
            selectPathButton.pack(pady=5)

            deleteKeyButton = tk.Button(rightFrame, text="Delete Key", command=self.deleteKey)
            deleteKeyButton.pack(pady=5)

            bottomFrame = tk.Frame(self.root)
            bottomFrame.place(x=10, y=310, width=500, height=100)
            passwordLengthSlider = tk.Scale(bottomFrame, from_=3, to=36, orient=tk.HORIZONTAL, length=200, label="Password length")
            passwordLengthSlider.set(22)
            passwordLengthSlider.pack(pady=5)
            versionLabel = tk.Label(bottomFrame, text=f"Version: {self.version}")
            versionLabel.pack(pady=5)
            self.root.mainloop()
        except tk._tkinter.TclError:
            pass
            
    
    def deleteKey(self):
        filePath = os.path.expanduser("~/AppData/Roaming/Bitsology/custom_enc.png")
        if os.path.exists(filePath):
            os.remove(filePath)
            messagebox.showinfo("Success", "Custom encoding file deleted")
        else:
            messagebox.showerror("Error", "Custom encoding file not found")

    def cutpath(self, path):
        path = os.path.normpath(path)
        if path.startswith(os.path.expanduser("~")):
            return path.replace(os.path.expanduser("~"), "~", 1)
        drive, tail = os.path.splitdrive(path)
        if drive and tail.startswith(os.path.sep + "Users"):
            parts = tail.split(os.path.sep)
            if len(parts) > 2:
                return "~" + os.path.sep + os.path.join(*parts[2:])
        return path

    def heavyEncode(self, file = None, passlen = 22):
        file = self.systemArg if file == None else file
        self.copyToClipboard(self.encoder.heavyEncoding(externalFile=file, passLength=passlen))

    def lightEncode(self, file = None, passlen = 22):
        file = self.systemArg if file == None else file
        self.copyToClipboard(self.encoder.lightEncoding(passlen, file))

    def selectKeyPathButton(self):
        path = filedialog.askopenfilename(
            title="Select Path",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if path:
            self.rootdirectory = path
            self.saverootdirectory()
            self.CustomKeyPathLabel.config(text=self.cutpath(path))
        else:
            messagebox.showerror("Error", "No path selected")

    def selectFileButton(self):
        path = filedialog.askopenfilename(
            title="Select Path",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if path:
            self.selectedFilePath = path
            self.fileToEncodeLabel.config(text=self.cutpath(path))
        else:
            messagebox.showerror("Error", "No path selected")
            

if __name__ == "__main__":
    if len(sys.argv) > 1:
        app = App(1, sys.argv[1])
    else:
        app = App(0)
        app.guiInit()
