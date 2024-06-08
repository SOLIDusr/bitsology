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


class App:

    def __init__(self, mode, systemArg=None) -> None:
        # pre-start update
        self.version = "1.2.0-r"
        try:
            self.checkUpdates()
        except VersionMismatch:
            messagebox.showerror("App outdated.", "New version available, please update.")
        if not os.path.exists("settings.properties"):
            self.createsettings()
        # end pre-start update
        # start load settings
        self.loadsettings()
        # end load settings
        # start gui init
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.geometry("1000x600")
        self.root.title("Bitsology")
        self.encoder = Encoder()
        # end gui init
        # start mode check
        if mode == 1:
            self.systemArg = systemArg
            if messagebox.askyesno("Warning", "Use the light encoding?"):
                self.lightEncoding(22, self.systemArg)
            else:
                self.heavyEncoding(22, self.systemArg)
        else:
            self.systemArg = None
            self.guiInit()
        # end mode check
        

    def checkUpdates(self):
        repoUrl = "https://api.github.com/repos/SOLIDusr/Bitsology/releases/latest"
        try:
            response = requests.get(repoUrl)
            response.raise_for_status()
            latestVersion = response.json()["tag_name"]
            if self.version != latestVersion:
                print(f"Current version: {self.version}, Latest version: {latestVersion}")
                raise VersionMismatch(f"Current version: {self.version}, Latest version: {latestVersion}")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to check for updates: {e}")

    def createsettings(self):
        file = configparser.ConfigParser()
        file.add_section("Path Variables")
        file.set("Path Variables", "path", "~/AppData/Roaming/Bitsology/custom_enc.png")
        with open("settings.properties", "w") as f:
            file.write(f)
            f.close()

    def loadsettings(self):
        file = configparser.ConfigParser()
        file.read("settings.properties")
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
        # Left upper section
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

        openEditorButton = tk.Button(leftUpperFrame, text="Open In Editor", command=lambda: self.openEditor(self.selectedFilePath if self.selectedFilePath else None))
        openEditorButton.pack(pady=5)
        
        passwordLengthSlider = tk.Scale(leftUpperFrame, from_=3, to=36, orient=tk.HORIZONTAL, length=200, label="Password length")
        passwordLengthSlider.set(22)
        passwordLengthSlider.pack(pady=5)

        # Left bottom section
        leftBottomFrame = tk.Frame(self.root)
        leftBottomFrame.place(x=10, y=350, width=200, height=230)

        customEncodingKeyLabel = tk.Label(leftBottomFrame, text="Custom Encoding Key")
        customEncodingKeyLabel.pack(pady=5)

        self.CustomKeyPathLabel = tk.Label(leftBottomFrame, text=self.cutpath(self.rootdirectory), wraplength=100)
        self.CustomKeyPathLabel.pack(pady=5)

        selectPathButton = tk.Button(leftBottomFrame, text="Select Path", command=self.selectKeyPathButton)
        selectPathButton.pack(pady=5)

        deleteKeyButton = tk.Button(leftBottomFrame, text="Delete Key", command=self.deleteKey)
        deleteKeyButton.pack(pady=5)

        # Right section
        rightFrame = tk.Frame(self.root)
        rightFrame.place(x=220, y=10, width=760, height=580)

        editorLabel = tk.Label(rightFrame, text="Editor")
        editorLabel.pack(pady=5)

        self.editorEntry = tk.Text(rightFrame, height=30, width=90)
        self.editorEntry.pack(pady=5)

        saveButton = tk.Button(rightFrame, text="Save", command=self.save)
        saveButton.pack(pady=5)

        self.root.mainloop()
    
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
        self.encoder.heavyEncoding(passlen, file)

    def lightEncode(self, file = None, passlen = 22):
        file = self.systemArg if file == None else file
        self.encoder.lightEncoding(passlen, file)

    def openEditor(self, file: str):
        messagebox.showinfo("Info", "WIP")
        return
        if not file:
            return
        pic = Picture(file)
        way, _ = self.encoder.calculateWayAndFactorPixel(pic.getCenterPixel())
        self.hex = pic.hexCode
        if self.hex[way:][:3] == "<Type>":
            textToInsert = ""
            i = way+6
            while True:
                if self.hex[i:i+7] == "</Type>":
                    break
                textToInsert += self.hex[i]
                i += 1

            self.editorEntry.insert(1.0, textToInsert)
        else:
            self.editorEntry.insert(1.0, "Blank")

    def save(self):
        messagebox.showinfo("Info", "WIP")
        return
        content = self.editorEntry.get("1.0", tk.END).replace(" ", "").replace("\n", "")
        pic = Picture(self.selectedFilePath)
        way, _ = self.encoder.calculateWayAndFactorPixel(pic.getCenterPixel())
        self.hex = pic.hexCode
        writedata = self.hex + content
        file = open(self.selectedFilePath, "wb")
        file.write(writedata.encode("utf-8"))
        file.close()

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


class VersionMismatch(Exception):
    def __init__(self, message="Version mismatch error"):
        self.message = message
        super().__init__(self.message)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        app = App(1, sys.argv[1])
    else:
        app = App(0)
        app.guiInit()
