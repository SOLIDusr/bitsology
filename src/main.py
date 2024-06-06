import binascii
import hashlib
import os
import string
import subprocess
import sys
import uuid
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image


class Picture:
    def __init__(self, path) -> None:
        self.path = path
        self.image = Image.open(path)
        self.width, self.height = self.image.size
        self.hexCode = binascii.hexlify(open(path, "rb").read()).decode("utf-8")
        self.wayCode = ""

    def getCenterPixel(self):
        return self.image.getpixel((self.width // 2, self.height // 2))

    def generateLightCode(self, way, passLength):
        self.wayCode = self.hexCode[way:way + passLength]
        return self.wayCode

class App:
    def __init__(self, mode, systemArg=None) -> None:
        self.version = "1.2.0-r"
        try:
            self.checkUpdates()
        except VersionMismatch:
            messagebox.showerror("App outdated.", "New version available, please update.")
        self.root = tk.Tk()
        self.uniqueCode = 0
        if mode == 1:
            self.systemArg = systemArg
            if messagebox.askyesno("Warning", "Use the light encoding?"):
                self.lightEncoding(22, self.systemArg)
            else:
                self.heavyEncoding(22, self.systemArg)

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

    def copyToClipboard(self, text):
        process = subprocess.Popen(['clip.exe'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=text)

    def shufflePassword(self, password, factor, passLen):
        shadPass = hashlib.sha256(password.encode()).hexdigest()[:passLen]
        newPass = ""
        specials = "!@#$%&="
        for i in range(len(shadPass)):
            if i < factor:
                newPass += shadPass[i].upper() if i % 2 == 0 else shadPass[i]
            else:
                newPass += specials[i % len(specials)] if i % 3 == 0 else shadPass[i]
        return newPass

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

    def guiInit(self):
        self.root.geometry("600x300")
        self.root.title("Bitsology")

        passLengthLabel = tk.Label(self.root, text="Enter password length (3-36):")
        passLengthEntry = tk.Entry(self.root, width=10)
        passLengthLabel.pack(pady=10)
        passLengthEntry.pack(pady=10)

        def getPassLength():
            try:
                length = int(passLengthEntry.get())
                return length if 3 <= length <= 36 else 22
            except ValueError:
                return 22

        lightButton = tk.Button(self.root, text="Light Encoding", command=lambda: self.lightEncoding(getPassLength()))
        lightButton.pack(pady=20)
        heavyButton = tk.Button(self.root, text="Heavy Encoding", command=lambda: self.heavyEncoding(getPassLength()))
        heavyButton.pack(pady=20)
        deleteButton = tk.Button(self.root, text="Delete custom encoding", command=lambda: self.deleteCustomEncoding())
        deleteButton.pack(pady=20)
        self.root.mainloop()

    def deleteCustomEncoding(self):
        filePath = os.path.expanduser("~/AppData/Roaming/Bitsology/custom_enc.png")
        if os.path.exists(filePath):
            os.remove(filePath)
            messagebox.showinfo("Success", "Custom encoding file deleted")
        else:
            messagebox.showerror("Error", "Custom encoding file not found")

    def lightEncoding(self, passLength, externalFile=None):
        filePath = externalFile if externalFile else self.selectFile()
        if not filePath:
            return
        picture = Picture(filePath)
        centerPixel = picture.getCenterPixel()
        way, factorPixel = self.calculateWayAndFactorPixel(centerPixel)
        rawPassword = picture.generateLightCode(way=way, passLength=passLength)
        factor = passLength // 3 * 2 if factorPixel % 100 > passLength // 3 * 2 else passLength // 3 if factorPixel % 100 > passLength // 3 else passLength // 2
        password = self.shufflePassword(password=rawPassword, factor=factor, passLen=passLength)
        self.copyToClipboard(password)
        messagebox.showinfo("Password copied to clipboard", f"Your password is: {password}")

    def textToImage(self, text, imgSize=(100, 100)):
        textBytes = hashlib.sha256(text.encode()).digest()
        image = Image.new('RGB', imgSize)
        pixels = image.load()
        index = 0
        for i in range(imgSize[0]):
            for j in range(imgSize[1]):
                if index < len(textBytes) - 2:
                    pixels[i, j] = (textBytes[index], textBytes[index + 1], textBytes[index + 2])
                    index += 3
                else:
                    index = 0
        return image

    def getCEncPars(self) -> str:
        return uuid.uuid1().hex

    def generateCustomEncoding(self, cEnc):
        parts = [cEnc[i:i + len(cEnc) // 16] for i in range(0, len(cEnc), len(cEnc) // 16)]
        sums = [str(sum(int(ch) for ch in part if ch in "0123456789")) for part in parts]
        return "".join(sums)

    def encode(self, rawPass, cEnc):
        if len(cEnc) < len(rawPass):
            cEnc = (cEnc * (len(rawPass) // len(cEnc) + 1))[:len(rawPass)]

        hashedKey = hashlib.sha256(cEnc.encode()).digest()
        allowedChars = string.ascii_letters + string.digits + "!@#$%&="
        allowedCharsLen = len(allowedChars)

        encodedChars = []
        for i in range(len(rawPass)):
            xorResult = ord(rawPass[i]) ^ hashedKey[i % len(hashedKey)]
            encodedChar = allowedChars[xorResult % allowedCharsLen]
            encodedChars.append(encodedChar)

        encodedText = ''.join(encodedChars)
        specials = "!@#$%&="
        passList = list(encodedText)
        for i in range(len(passList)):
            if passList[i].isdigit() and i % 5 == 0:
                passList[i] = specials[i % len(specials)]
            elif passList[i].isalpha() and i % 4 == 0:
                passList[i] = passList[i].upper()
            elif passList[i].isalpha() and i % 6 == 0:
                passList[i] = specials[(i + 5) % len(specials)]
            if passList[i].isalpha() and i > len(passList) // 2 and i % 3 == 0:
                passList[i] = "0123456789"[i % 10]

        return "".join(passList)

    def heavyEncoding(self, passLength, externalFile=None):
        text = self.getCEncPars()
        print(text)
        filePath = externalFile if externalFile else self.selectFile()
        if not filePath:
            return
        picture = Picture(filePath)
        way, _ = self.calculateWayAndFactorPixel(picture.getCenterPixel())
        rawPass = picture.generateLightCode(way=way, passLength=passLength)
        dirPath = os.path.expanduser("~/AppData/Roaming/Bitsology/")
        filePath = os.path.expanduser("~/AppData/Roaming/Bitsology/custom_enc.png")
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
        if not os.path.exists(filePath):
            if not messagebox.askokcancel("Warning", "No custom encoding file found, do you want to create a new one?"):
                return
            image = self.textToImage(text)
            image.save(filePath)

        imageHex = binascii.hexlify(open(filePath, "rb").read()).decode("utf-8")
        encoding = self.generateCustomEncoding(imageHex)
        password = self.encode(rawPass=rawPass, cEnc=encoding)
        self.copyToClipboard(password)
        messagebox.showinfo("Password copied to clipboard", f"Your password is: {password}")

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