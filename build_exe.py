import os
import subprocess
import sys
import customtkinter

ctk_path = os.path.dirname(customtkinter.__file__) #customtkinter kütüphanesinin yolu

command = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--icon=icon.ico", #ikon dosyası ekleme
    "--add-data",
    f"icon.ico{os.path.pathsep}.",  # icon.ico dosyasını exe içine gömer
    "--add-data",
    f"{ctk_path}{os.path.pathsep}customtkinter/",
    "--name",
    "ox1 Not Defterim",
    "main.py",
]

print(".exe paketleme başlatılıyor...")
subprocess.run(command)
print("'dist' klasörüne ox1_not_defterim.exe oluşturuldu!")

