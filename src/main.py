import binascii
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import hashlib 
import subprocess
import os


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
    
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.uniqueCode = 0

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

        self.root.mainloop()
    
    def light_encoding(self, passlength):
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
    
    def getCEncPars(self):
        
    
    
    def heavy_encoding(self, passlength):
        
        dirpath = os.path.expanduser("~/AppData/Roaming/Bitsology/")
        filepath = os.path.expanduser("~/AppData/Roaming/Bitsology/custom_enc.png")
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        else:
            print("Dir Found")
        if not os.path.exists(filepath):
            if not messagebox.askokcancel("Warning", "No custom encoding file found, do you want to create a new one?"):
                return
            
            
            
        # print(customEnc)
        # if not filePath:
        #     return
        # picture = Picture(filePath)
        # centerPixel = picture.get_center_pixel()
        # way, factorpixel = self.calculateWayAndFactorPixel(centerPixel)
        

if __name__ == "__main__":
    app = App()
    app.guiInit()
