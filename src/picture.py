from PIL import Image
import binascii


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