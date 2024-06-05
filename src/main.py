import binascii
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import hashlib 
import subprocess
import os
import datetime
import sys


class Picture:
    def __init__(self, path) -> None:
        self.path = path
        self.image = Image.open(path)
        self.width, self.height = self.image.size
        self.hexCode = binascii.hexlify(open(path, "rb").read()).decode("utf-8")
        self.wayCode = ""

    
    def get_center_pixel(self):
        return self.image.getpixel((self.width // 2, self.height // 2))
    
    def generate_light_code(self, way, passlength):
        for i in range(way, way + passlength):
            self.wayCode += self.hexCode[i]
        return self.wayCode

class App:
    
    def __init__(self, mode, systemArg = None) -> None:
        self.root = tk.Tk()
        self.uniqueCode = 0
        if mode == 1:
            self.sysArg = systemArg
            if messagebox.askyesno("Warning", "Use the light encoding?"):
                self.light_encoding(22, self.sysArg)
            else:
                self.heavy_encoding(22, self.sysArg)


    def copyToClipboard(self, text):
        process = subprocess.Popen(['clip.exe'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=text)
        
    
    def shufflepassword(self, password, factor,passlen):
        shadpass = hashlib.sha256(password.encode()).hexdigest()[:passlen]
        newpass = ""
        specials = "!@#$%&="
        for i in range(len(shadpass)):
            if i in range(factor):
                if i % 2 == 0:
                    newpass += shadpass[i].upper()
                else:
                    newpass += shadpass[i]
            else:
                if i % 3 == 0:
                    newpass += specials[i % len(specials)]
                else:
                    newpass += shadpass[i]
        return newpass
        
    
    def selectFile(self):
        filePath = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not filePath:
            messagebox.showerror("Error", "No file selected")
            return
        return filePath
    
    def calculateWayAndFactorPixel(self, center_pixel):
        if isinstance(center_pixel, int):
            return center_pixel, center_pixel
        return sum(center_pixel), center_pixel[0]
    
    def guiInit(self):
        self.root.geometry("600x300")
        self.root.title("Bitsology")

        # Entry for password length
        passlengthLabel = tk.Label(self.root, text="Enter password length (3-36):")
        passlengthEntry = tk.Entry(self.root, width=10)
        passlengthLabel.pack(pady=10)
        passlengthEntry.pack(pady=10)

        # Function to validate and get password length
        def get_pass_length():
            try:
                length = int(passlengthEntry.get())
                if 3 <= length <= 36:
                    return length
                else:
                    return 22
            except ValueError:
                return 22

        # Light Encoding button
        lightButton = tk.Button(self.root, text="Light Encoding", command=lambda: self.light_encoding(get_pass_length()))
        lightButton.pack(pady=20)

        # Heavy Encoding button
        heavyButton = tk.Button(self.root, text="Heavy Encoding", command=lambda: self.heavy_encoding(get_pass_length()))
        heavyButton.pack(pady=20)

        deleteButton = tk.Button(self.root, text="Delete custom encoding", command=lambda: self.delete_custom_encoding())
        deleteButton.pack(pady=20)

        self.root.mainloop()
    
    def delete_custom_encoding(self):
        filepath = os.path.expanduser("~/AppData/Roaming/Bitsology/custom_enc.png")
        if os.path.exists(filepath):
            os.remove(filepath)
            messagebox.showinfo("Success", "Custom encoding file deleted")
        else:
            messagebox.showerror("Error", "Custom encoding file not found")

    def light_encoding(self, passlength, externalFile = None):
        if externalFile:
            filePath = externalFile
        else:
            filePath = self.selectFile()
            if not filePath:
                return
        picture = Picture(filePath)
        centerPixel = picture.get_center_pixel()
        way, factorpixel = self.calculateWayAndFactorPixel(centerPixel)
        rawpassword = picture.generate_light_code(way=way, passlength=passlength)
        if factorpixel % 100 > passlength // 3 * 2:
            factor = passlength // 3 * 2
        elif factorpixel % 100 > passlength // 3:
            factor = passlength // 3
        else:
            factor = passlength // 2
        
        passwd = self.shufflepassword(password=rawpassword, factor=factor, passlen=passlength)
        self.copyToClipboard(passwd)
        messagebox.showinfo("Password copied to clipboard", f"Your password is: {passwd}")
    
    def text_to_image(self, text, img_size=(100, 100)):
        text_bytes = hashlib.sha256(text.encode()).digest()
        image = Image.new('RGB', img_size)
        pixels = image.load()
        index = 0
        for i in range(img_size[0]):
            for j in range(img_size[1]):
                if index < len(text_bytes) - 2:
                    pixels[i, j] = (text_bytes[index], text_bytes[index + 1], text_bytes[index + 2])
                    index += 3
                else:
                    index = 0
        
        return image
        
    def getCEncPars(self) -> str:
        string = ""
        string += datetime.datetime.now().strftime("%d%m%Y%H%M%S")
        string += os.getlogin()
        return string
    
    def generate_custom_encoding(self, CEnc):
        parts = [CEnc[i:i+len(CEnc)//16] for i in range(0, len(CEnc), len(CEnc)//16)]
        sums = []
        for part in parts:
            sum = 0
            for ch in part:
                if ch in "0123456789":
                    sum += int(ch)
            sums.append(sum)
        sums = [str(sum) for sum in sums]
        return "".join(sums)
        
    def encode(self, rawpass, cenc):
        newpass = list(rawpass)
        print(cenc)
        for i in cenc:
            if i == "1":
                for q in range(len(newpass)):
                    if q % 2 == 0:
                        newpass[q] = newpass[q].upper()
                    else:
                        newpass[q] = newpass[q].lower()
            elif i == "2":
                newpass = newpass[::-1]
            elif i == "3":
                for q in range(len(newpass)):
                    if newpass[q].isdigit():
                        newpass[q] = str(9 - int(newpass[q]))
            elif i == "4":
                newpass = newpass[::-1]
            elif i == "5":
                newpass = newpass[:len(newpass)//2] + newpass[len(newpass)//2:][::-1]
            elif i == "6":
                newpass = newpass[:len(newpass)//2] + newpass[len(newpass)//2:][::-1]
            elif i == "7":
                newpass = newpass[:len(newpass)//2][::-1] + newpass[len(newpass)//2:]
            elif i == "8":
                newpass = newpass[::-1]
            elif i == "9":
                newpass[-1] = newpass[-2]
            elif i == "0":
                newpass[0] = newpass[-1]
        specials = "!@#$%&="
        for i in range(len(newpass)):
            if newpass[i].isdigit() and i % 3 == 0:
                newpass[i] = specials[i % len(specials)]
        return "".join(newpass)  
        
        
    def heavy_encoding(self, passlength, externalFile = None):
        text = self.getCEncPars()
        if externalFile:
            pathToPicture = externalFile
        else:
            pathToPicture = self.selectFile()
            if not pathToPicture:
                return
        if not pathToPicture:
            return
        picture = Picture(pathToPicture)
        way, _ = self.calculateWayAndFactorPixel(picture.get_center_pixel())
        rawpass = picture.generate_light_code(way=way, passlength=passlength)
        dirpath = os.path.expanduser("~/AppData/Roaming/Bitsology/")
        filepath = os.path.expanduser("~/AppData/Roaming/Bitsology/custom_enc.png")
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        if not os.path.exists(filepath):
            if not messagebox.askokcancel("Warning", "No custom encoding file found, do you want to create a new one?"):
                return
            if isinstance(text, str):
                image = self.text_to_image(text)
            else:
                print("Error: Expected a string from getCEncPars, got:", type(text))
            image.save(filepath)
            
        image = binascii.hexlify(open(filepath, "rb").read()).decode("utf-8")
        encoding = self.generate_custom_encoding(image)
        print(rawpass)
        mypass = self.encode(rawpass=rawpass, cenc=encoding)
        print(mypass)
        self.copyToClipboard(mypass)
        messagebox.showinfo("Password copied to clipboard", f"Your password is: {mypass}")
        

if __name__ == "__main__":
    if len(sys.argv) > 1:
        app = App(1, sys.argv[1])
    else:
        app = App(0)
        app.guiInit()
