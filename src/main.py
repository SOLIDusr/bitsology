import binascii
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os

def select_image_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    return file_path

def get_center_pixel(image):
    width, height = image.size
    return image.getpixel((width // 2, height // 2))

def calculate_way_and_factorpixel(center_pixel):
    if isinstance(center_pixel, int):
        return center_pixel, center_pixel
    return sum(center_pixel), center_pixel[0]

def generate_password(hex_content, way, passlen=22):
    password = ""
    for i in range(way, way + passlen):
        password += hex_content[i]
    return password

def transform_password(password, factorpixel, passlen=22):
    if factorpixel % 100 > passlen // 3 * 2:
        factor = passlen // 3 * 2
    elif factorpixel % 100 > passlen // 3:
        factor = passlen // 3
    else:
        factor = passlen // 2

    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    special_symbols = '!@#$%&*'
    password_list = list(password)

    for i in range(len(password_list)):
        if i < factor:
            if password_list[i].isdigit():
                password_list[i] = alphabet[int(password_list[i]) % 26]
            if (i + 1) % 3 == 0:
                password_list[i] = password_list[i].upper()
        else:
            if password_list[i].isdigit():
                if (i - factor) % 2 == 0:
                    password_list[i] = special_symbols[int(password_list[i]) % len(special_symbols)]

    return ''.join(password_list)

def main():
    file_path = select_image_file()
    if not file_path:
        print("No file selected.")
        return

    try:
        image = Image.open(file_path)
        center_pixel = get_center_pixel(image)
        way, factorpixel = calculate_way_and_factorpixel(center_pixel)

        with open(file_path, "rb") as file:
            content = file.read()
            hex_content = binascii.hexlify(content).decode('utf-8')

        password = generate_password(hex_content, way)
        new_password = transform_password(password, factorpixel)
        print(new_password)

        with open(f"{new_password}.txt", "w") as f:
            f.write("")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
