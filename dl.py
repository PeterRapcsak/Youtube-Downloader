import tkinter
import customtkinter
import threading
import os
import subprocess
import json
import re
import sys
import shutil

def select_directory():
    selected_dir = customtkinter.filedialog.askdirectory()
    if selected_dir:
        download_directory_var.set(selected_dir)
        directory_label.configure(text=f"Save to: .../{os.path.basename(selected_dir)}")
        download_button.configure(state="normal")

def start_fetch_thread():
    fetch_button.configure(state="disabled", text="Fetching...")
    download_button.configure(state="disabled")
    thread = threading.Thread(target=fetch_resolutions_worker)
    thread.start()

def fetch_resolutions_worker():
    url = link_entry.get()
    if not url:
        update_status("Please enter a YouTube link.", "red")
        reset_ui_state()
        return

    try:
        command = ['yt-dlp', '--dump-json', url]

        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            creationflags=creation_flags
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            error_message = "An unknown yt-dlp error occurred."
            if stderr:
                lines = stderr.strip().splitlines()
                if lines:
                    error_message = lines[-1].strip()

            update_status(f"Error: {error_message}", "red")
            reset_ui_state()
            return

        if not stdout:
            update_status("Error: yt-dlp returned no data.", "red")
            reset_ui_state()
            return

        video_info = json.loads(stdout)
        video_title_var.set(video_info.get('title', 'N/A'))
        title_display_label.configure(text=f"Title: {video_title_var.get()[:50]}...")

        formats = video_info.get('formats', [])
        resolutions = set()
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('acodec') == 'none' and f.get('ext') == 'mp4' and f.get('height'):
                resolutions.add(f'{f["height"]}p')

        sorted_resolutions = sorted(list(resolutions), key=lambda r: int(r[:-1]), reverse=True)

        if not sorted_resolutions:
            update_status("No separate MP4 video streams found.", "orange")
            resolution_combobox.configure(values=["N/A"])
            resolution_combobox.set("N/A")
        else:
            update_status("Resolutions found!", "green")
            resolution_combobox.configure(values=sorted_resolutions)
            resolution_combobox.set(sorted_resolutions[0])

    except FileNotFoundError:
        update_status("yt-dlp not found. Is it installed and in your PATH?", "red")
    except json.JSONDecodeError:
        update_status("Failed to parse video data. Is the link valid?", "red")
    except Exception as e:
        update_status(f"An error occurred: {e}", "red")
    finally:
        reset_ui_state()

def start_download_thread():
    download_button.configure(state="disabled")
    fetch_button.configure(state="disabled")
    thread = threading.Thread(target=download_worker)
    thread.start()

def download_worker():
    if not shutil.which('yt-dlp'):
        update_status("ERROR: yt-dlp is not installed or not in your system's PATH.", "red")
        reset_ui_state()
        return
    if not shutil.which('ffmpeg'):
        update_status("ERROR: FFmpeg is not installed or not in your system's PATH.", "red")
        reset_ui_state()
        return

    url = link_entry.get()
    resolution = resolution_combobox.get()
    download_path = download_directory_var.get()

    if not all([url, resolution, download_path]) or resolution == "N/A":
        update_status("Missing URL, resolution, or directory.", "red")
        reset_ui_state()
        return

    try:

        height = resolution[:-1]
        format_string = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        output_template = os.path.join(download_path, '%(title)s.%(ext)s')

        command = [
            'yt-dlp',
            '-f', format_string,
            '--merge-output-format', 'mp4',
            '-o', output_template,
            '--progress',
            '--no-warnings',
            '--retries', '15',
            '--fragment-retries', '15',
            url
        ]

        update_status(f"Downloading {resolution}...", "dodgerblue")

        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1,
            creationflags=creation_flags
        )

        full_output = []
        for line in iter(process.stdout.readline, ''):
            full_output.append(line)

            match = re.search(r'\[download\]\s+([0-9.]+)%', line)
            if match:
                percentage = float(match.group(1))
                app.after(0, lambda p=percentage: p_percentage.configure(text=f"{p:.1f}%"))
                app.after(0, lambda p=percentage: progress_bar.set(p / 100))

            if "[Merger]" in line:
                app.after(0, lambda: update_status("Merging files...", "orange"))

        process.wait()
        process.stdout.close()





        if process.returncode == 0:
            update_status("Download Complete!", "green")
            app.after(0, lambda: p_percentage.configure(text="100.0%"))
            app.after(0, lambda: progress_bar.set(1.0))
        else:
            error_line = "Unknown error. Check console for details."
            for line in reversed(full_output):
                if line.strip().upper().startswith("ERROR:"):
                    error_line = line.strip().replace("ERROR: ", "")
                    break
            update_status(f"Download failed: {error_line}", "red")




    except Exception as e:
        update_status(f"A Python error occurred: {e}", "red")
    finally:
        reset_ui_state()
        app.after(5000, clear_progress)





def clear_progress():
    """Resets progress indicators after a delay."""
    update_status("", "white")
    p_percentage.configure(text="0.0%")
    progress_bar.set(0)

def update_status(message, color):
    """Updates the status label text and color safely from any thread."""
    def do_update():
        status_label.configure(text=message, text_color=color)
    app.after(0, do_update)

def reset_ui_state():
    """Resets the UI buttons to their default state after an operation."""
    is_dir_selected = bool(download_directory_var.get())
    is_res_selected = resolution_combobox.get() != "N/A"
    


    download_state = "normal" if is_dir_selected and is_res_selected else "disabled"
    
    app.after(0, lambda: download_button.configure(state=download_state))
    app.after(0, lambda: fetch_button.configure(state="normal", text="Fetch Resolutions"))


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("720x580")
app.title("yt-dlp Downloader")




download_directory_var = tkinter.StringVar()
video_title_var = tkinter.StringVar()



title_frame = customtkinter.CTkFrame(app)
title_frame.pack(padx=20, pady=20, fill="x")

link_entry = customtkinter.CTkEntry(title_frame, placeholder_text="Enter YouTube link here", width=350, height=40)
link_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))

fetch_button = customtkinter.CTkButton(title_frame, text="Fetch Resolutions", command=start_fetch_thread, height=40)
fetch_button.pack(side="left", padx=(5, 10))

title_display_label = customtkinter.CTkLabel(app, text="Title: (fetch a video first)", font=("Arial", 12), text_color="gray")
title_display_label.pack(padx=20, pady=(0, 10), anchor="w")

options_frame = customtkinter.CTkFrame(app)
options_frame.pack(padx=20, pady=10, fill="x")

directory_button = customtkinter.CTkButton(options_frame, text="Select Save Directory", command=select_directory)
directory_button.pack(side="left", padx=10, pady=10)

directory_label = customtkinter.CTkLabel(options_frame, text="No directory selected")
directory_label.pack(side="left", padx=10, pady=10)

resolution_label = customtkinter.CTkLabel(options_frame, text="Resolution:")
resolution_label.pack(side="left", padx=(20, 5), pady=10)

resolution_combobox = customtkinter.CTkOptionMenu(options_frame, values=["N/A"])
resolution_combobox.set("N/A")
resolution_combobox.pack(side="left", padx=10, pady=10)

progress_frame = customtkinter.CTkFrame(app)
progress_frame.pack(padx=20, pady=10, fill="x")

p_percentage = customtkinter.CTkLabel(progress_frame, text="0.0%")
p_percentage.pack(pady=(10, 0))

progress_bar = customtkinter.CTkProgressBar(progress_frame, width=400)
progress_bar.set(0)
progress_bar.pack(padx=20, pady=10)

status_label = customtkinter.CTkLabel(progress_frame, text="", font=("Arial", 12))
status_label.pack(pady=(0, 10))

download_button = customtkinter.CTkButton(app, text="Download", command=start_download_thread, height=40, font=("Arial", 16, "bold"))
download_button.pack(padx=20, pady=20, fill="x")
download_button.configure(state="disabled")

app.mainloop()