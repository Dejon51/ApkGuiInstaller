import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, simpledialog
import os
import sys
import platform

ADB_PATH = None

def detect_os_and_set_adb():
    global ADB_PATH
    system = platform.system()
    print(f"[INFO] Detected OS: {system}")

    if system == "Windows":
        ADB_PATH = os.path.join("adbwindows", "adb.exe")
    elif system == "Linux":
        ADB_PATH = os.path.join("adblinux", "adb")
    elif system == "Darwin":  # macOS
        ADB_PATH = os.path.join("adbmac", "adb")
    else:
        messagebox.showerror("Unsupported OS", f"OS not supported: {system}")
        sys.exit(1)

    if not os.path.isfile(ADB_PATH):
        messagebox.showerror("ADB Not Found", f"ADB binary not found at: {ADB_PATH}")
        sys.exit(1)

    # Ensure it's executable (for Unix)
    if system != "Windows":
        os.chmod(ADB_PATH, 0o755)

    print(f"[INFO] Using ADB path: {ADB_PATH}")

def run_adb_command(cmd_args):
    print(f"Running command: {' '.join(cmd_args)}")
    try:
        result = subprocess.run(cmd_args,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("---- STDOUT ----")
        print(result.stdout.strip())
        print("---- STDERR ----")
        print(result.stderr.strip())
        return result.stdout, result.stderr
    except Exception as e:
        print(f"Exception while running command: {e}")
        return "", str(e)

def get_connected_devices():
    stdout, stderr = run_adb_command([ADB_PATH, "devices"])
    devices = []
    if stdout:
        lines = stdout.strip().splitlines()[1:]
        devices = [line.split()[0] for line in lines if "device" in line]
    return devices

def install_apk(device_id, apk_path):
    stdout, stderr = run_adb_command([ADB_PATH, "-s", device_id, "install", "-r", apk_path])
    if "Success" in stdout:
        messagebox.showinfo("Success", f"APK installed on {device_id}")
    else:
        messagebox.showerror("Install Failed", stderr or stdout)

def refresh_devices():
    device_listbox.delete(0, tk.END)
    devices = get_connected_devices()
    for dev in devices:
        device_listbox.insert(tk.END, dev)

def drop_apk():
    apk_path = filedialog.askopenfilename(filetypes=[("APK files", "*.apk")])
    if not apk_path:
        return
    selected = device_listbox.curselection()
    if not selected:
        messagebox.showwarning("Select Device", "Please select a device first.")
        return
    device_id = device_listbox.get(selected[0])
    install_apk(device_id, apk_path)

def connect_wireless():
    ip_port = simpledialog.askstring("Connect Wireless", "Enter device IP:PORT")
    if not ip_port:
        return
    stdout, stderr = run_adb_command([ADB_PATH, "connect", ip_port])
    output = stdout + stderr
    if "connected" in output or "already connected" in output:
        messagebox.showinfo("Success", f"Connected to {ip_port}")
    else:
        messagebox.showerror("Failed", output)
    refresh_devices()

def pair_device():
    ip_port = simpledialog.askstring("Pair Device", "Enter device IP and Pairing Port (e.g. 192.168.1.5:4711)")
    if not ip_port:
        return
    pairing_code = simpledialog.askstring("Pair Device", "Enter pairing code shown on the device")
    if not pairing_code:
        return
    stdout, stderr = run_adb_command([ADB_PATH, "pair", ip_port, pairing_code])
    output = stdout + stderr
    if "Successfully paired" in output:
        messagebox.showinfo("Success", f"Paired with {ip_port}")
    else:
        messagebox.showerror("Pairing Failed", output)
    refresh_devices()

# Start GUI
root = tk.Tk()
root.withdraw()  # Hide root during init
detect_os_and_set_adb()
root.deiconify()  # Show GUI after setup

root.title("ADB APK Installer")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

tk.Label(frame, text="Connected Devices:").pack()

device_listbox = Listbox(frame, width=40, height=6)
device_listbox.pack()

btn_frame = tk.Frame(frame)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="🔄 Refresh", command=refresh_devices).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="📡 Connect IP:PORT", command=connect_wireless).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="🔗 Pair Device", command=pair_device).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="📦 Install APK", command=drop_apk).grid(row=0, column=3, padx=5)

tk.Label(frame, text="Supports wired & wireless ADB, any port, pairing.").pack(pady=(10, 0))

refresh_devices()
root.mainloop()
