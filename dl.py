import tkinter
from tkinter import filedialog
import customtkinter
from pytube import YouTube

def startDownload():
    try:
        ytLink = link.get()
        ytObject = YouTube(ytLink, on_progress_callback=on_progress)

        # Get all available streams
        streams = ytObject.streams.filter(file_extension="mp4")

        # Display available resolutions
        resolutions = [stream.resolution for stream in streams]
        resolution_choice = resolution_combobox.get()

        # Filter streams based on the chosen resolution
        video = streams.filter(resolution=resolution_choice).first()

        title.configure(text=ytObject.title, text_color="white")
        finishLabel.configure(text="")
        progressBar.pack(padx=10, pady=10)  # Show progress bar
        pPercentage.pack()  # Show percentage label

        # Ask the user to choose the download folder
        folder_selected = filedialog.askdirectory()

        # Download the video to the selected folder
        video.download(folder_selected)

        finishLabel.configure(text="Download Complete!", text_color="green")

        # Schedule a function call to reset finishLabel and progressBar after 3 seconds
        app.after(3000, reset_labels)

    except Exception as e:
        finishLabel.configure(text=f"Download Error: {str(e)}", text_color="red")

def reset_labels():
    finishLabel.configure(text="")
    progressBar.set(0)
    pPercentage.configure(text="0%")

    # Hide progress bar and percentage label
    progressBar.pack_forget()
    pPercentage.pack_forget()

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percent = bytes_downloaded / total_size * 100
    per = str(int(percent))
    pPercentage.configure(text=per + "%")
    pPercentage.update()

    progressBar.set(float(percent) / 100)

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("720x480")
app.title("Youtube Downloader")

title = customtkinter.CTkLabel(app, text="Insert a youtube link")
title.pack(padx=10, pady=10)

url_var = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_var)
link.pack()

resolution_label = customtkinter.CTkLabel(app, text="Choose video resolution:")
resolution_label.pack()

# Dropdown menu for selecting resolution
resolutions = ["144p", "240p", "360p", "480p", "720p", "1080p"]
resolution_combobox = customtkinter.CTkOptionMenu(app, values=resolutions)
resolution_combobox.set(resolutions[0])  # Set default resolution
resolution_combobox.pack()

finishLabel = customtkinter.CTkLabel(app, text="")
finishLabel.pack()

pPercentage = customtkinter.CTkLabel(app, text="0%")
pPercentage.pack_forget()

progressBar = customtkinter.CTkProgressBar(app, width=400)
progressBar.set(0)

download = customtkinter.CTkButton(app, text="Download", command=startDownload)
download.pack(padx=10, pady=10)

app.mainloop()
