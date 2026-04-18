import certifi
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import yt_dlp
import os
import threading
import shutil
import platform
def get_ffmpeg_path():
    
    path = shutil.which("ffmpeg")
    if path:
        return path
    
    if platform.system() == "Darwin" and os.path.exists("/opt/homebrew/bin/ffmpeg"):
        return "/opt/homebrew/bin/ffmpeg"
    # 3️⃣ macOS Intel Brew
    if platform.system() == "Darwin" and os.path.exists("/usr/local/bin/ffmpeg"):
        return "/usr/local/bin/ffmpeg"
    windows_paths = [
        "C:\\ffmpeg\\bin\\ffmpeg.exe",
        "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
        "C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe"
    ]
    for p in windows_paths:
        if os.path.exists(p):
            return p
    
    linux_paths = [
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/snap/bin/ffmpeg"
    ]
    for p in linux_paths:
        if os.path.exists(p):
            return p
   
    return "ffmpeg"  

stop_download = False
save_path = os.path.join(os.path.expanduser("~"), "Downloads")


def start_download():
    global stop_download
    stop_download = False

    url = entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please paste a YouTube link")
        return

    if not save_path_var.get():
        messagebox.showerror("Error", "Please choose save location")
        return

    download_btn.config(state="disabled")
    cancel_btn.config(state="normal")
    progress_bar["value"] = 0
    status_label.config(text="Fetching video info...")

    threading.Thread(target=download_video, daemon=True).start()

def cancel_download():
    global stop_download
    stop_download = True
    status_label.config(text="Cancelling...")

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        save_path_var.set(folder)

def download_video():
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        quality = quality_var.get()
        download_dir = save_path_var.get()

     
        if quality == "360p":
            format_code = "bestvideo[height<=360]+bestaudio/best"
        elif quality == "720p":
            format_code = "bestvideo[height<=720]+bestaudio/best"
        elif quality == "1080p":
            format_code = "bestvideo[height<=1080]+bestaudio/best"
        elif quality == "4K":
            format_code = "bestvideo[height<=2160]+bestaudio/best"
        else:  
            format_code = "bestaudio/best"

        def progress_hook(d):
            if stop_download:
                raise Exception("Download cancelled")

            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded = d.get("downloaded_bytes", 0)
                if total:
                    percent = downloaded / total * 100
                    root.after(0, update_progress, percent)
                    ssl._create_default_https_context = ssl._create_unverified_context

        ydl_opts = {
    "format": format_code,                             
    "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
    "noplaylist": False,
    "progress_hooks": [progress_hook],
    
   
    "merge_output_format": "mp4",

  
    "postprocessors": [
        {
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"                    
        }
    ] if quality != "Audio only" else [
        {
           
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }
    ],

   
    "cacert": certifi.where(),

    
    "ffmpeg_location":get_ffmpeg_path()
}
        

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(entry.get().strip(), download=False)
            root.after(0, update_title, info.get("title", "Unknown Title"))
            ydl.download([entry.get().strip()])

        root.after(0, download_success)

    except Exception as e:
        if "cancelled" in str(e).lower():
            root.after(0, download_cancelled)
        else:
            root.after(0, download_error, str(e))

def update_progress(value):
    progress_bar["value"] = value
    status_label.config(text=f"Downloading... {int(value)}%")

def update_title(title):
    title_label.config(text=title)

def download_success():
    reset_ui()
    messagebox.showinfo("Success", "Download completed!")

def download_cancelled():
    reset_ui()
    messagebox.showinfo("Cancelled", "Download cancelled")

def download_error(msg):
    reset_ui()
    messagebox.showerror("Error", msg)

def reset_ui():
    progress_bar["value"] = 0
    download_btn.config(state="normal")
    cancel_btn.config(state="disabled")
    status_label.config(text="")


root = tk.Tk()
root.title("URL Downloader")
root.geometry("520x460")

tk.Label(root, text="URL Downloader", font=("Helvetica", 15, "bold")).pack(pady=8)

title_label = tk.Label(
    root,
    text="Video title will appear here",
    wraplength=480,
    fg="#ffd500",
    font=("Helvetica", 12, "bold"),
    underline=True
)
title_label.pack(pady=4)

tk.Label(root, text="Paste YouTube Link").pack(pady=6)

entry = tk.Entry(root, width=65)
entry.pack()

tk.Label(root, text="Select Quality").pack(pady=6)
quality_var = tk.StringVar(value="720p")
tk.OptionMenu(
    root, quality_var, "360p", "720p", "1080p", "4K", "Audio only"
).pack()

tk.Label(root, text="Save to").pack(pady=6)

save_path_var = tk.StringVar(value=save_path)
save_frame = tk.Frame(root)
save_frame.pack()

tk.Entry(save_frame, textvariable=save_path_var, width=42).pack(side="left", padx=5)
tk.Button(save_frame, text="Browse", command=choose_folder).pack(side="left")

progress_bar = ttk.Progressbar(
    root, orient="horizontal", length=420, mode="determinate"
)
progress_bar.pack(pady=18)

status_label = tk.Label(root, text="", fg="green")
status_label.pack()

download_btn = tk.Button(root, text="Download", width=15, command=start_download)
download_btn.pack(pady=6)

cancel_btn = tk.Button(
    root, text="Cancel", width=15, command=cancel_download, state="disabled"
)
cancel_btn.pack(pady=4)

root.mainloop()

