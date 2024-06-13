import hashlib
import string
import uuid
from PIL import Image
import binascii
import os
from tkinter import messagebox
from PIL import Image
from picture import Picture


class Encoder:
    def __init__(self):
        pass

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

    def calculateWayAndFactorPixel(self, centerPixel):
        if isinstance(centerPixel, int):
            return centerPixel, centerPixel
        return sum(centerPixel), centerPixel[0]

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

    def lightEncoding(self, passLength, externalFile=None):
        filePath = externalFile
        if not filePath:
            messagebox.showerror("Error", "No image selected")
            return
        picture = Picture(filePath)
        centerPixel = picture.getCenterPixel()
        way, factorPixel = self.calculateWayAndFactorPixel(centerPixel)
        rawPassword = picture.generateLightCode(way=way, passLength=passLength)
        factor = passLength // 3 * 2 if factorPixel % 100 > passLength // 3 * 2 else passLength // 3 if factorPixel % 100 > passLength // 3 else passLength // 2
        password = self.shufflePassword(password=rawPassword, factor=factor, passLen=passLength)
        messagebox.showinfo("Password copied to clipboard", f"Your password is: {password}")
        return password

    def heavyEncoding(self, passLength, externalFile=None):
        text = self.getCEncPars()
        filePath = externalFile
        if not filePath:
            messagebox.showerror("Error", "No image selected")
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
        messagebox.showinfo("Password copied to clipboard", f"Your password is: {password}")
        return password
    
