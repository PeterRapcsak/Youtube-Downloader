import tkinter
from tkinter import filedialog
import customtkinter
from pytube import YouTube

def selectDirectory():
    global download_directory
    download_directory = filedialog.askdirectory()
    directoryLabel.configure(text=f"Download Directory: {download_directory}")

def selectResolution(choice):
    global selected_resolution
    selected_resolution.set(choice)

def startDownload():
    try:
        ytLink = link.get()
        ytObject = YouTube(ytLink, on_progress_callback=on_progress)

        # Get the stream with the selected resolution
        video = ytObject.streams.filter(res=selected_resolution.get()).first()

        # Use the selected download directory
        video.download(download_directory)

        finishLabel.configure(text="Downloaded!", text_color="green")

        # Schedule the reset function to be called after 3 seconds
        app.after(3000, reset)
    except:
        finishLabel.configure(text="Download Error", text_color="red")
        app.after(1000, reset)

def reset():
    finishLabel.configure(text="")
    pPercentage.configure(text="0%")
    progressBar.set(0)

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    per = str(int(percentage_of_completion))

    pPercentage.configure(text=per + "%")
    pPercentage.update()

    progressBar.set(float(percentage_of_completion) / 100)

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("720x480")
app.title("Youtube Downloader")


download_directory = ""  # Global variable to store the download directory
selected_resolution = tkinter.StringVar(value="360p")  # Initial resolution


title = customtkinter.CTkLabel(app, text="Insert a youtube link")
title.pack(padx=10, pady=10)

url_var = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_var)
link.pack()

directoryLabel = customtkinter.CTkLabel(app, text="Download Directory: ")
directoryLabel.pack()

selectDirectoryButton = customtkinter.CTkButton(app, text="Select Directory", command=selectDirectory)
selectDirectoryButton.pack(padx=10, pady=10)

resolution_label = customtkinter.CTkLabel(app, text="Select Resolution:")
resolution_label.pack()

# Create an option menu for resolution selection
resolution_combobox = customtkinter.CTkOptionMenu(
    master=app,
    values=["144p", "240p", "360p", "480p", "720p", "1080p"],
    command=selectResolution,
    variable=selected_resolution
)
resolution_combobox.pack()

finishLabel = customtkinter.CTkLabel(app, text="")
finishLabel.pack()

pPercentage = customtkinter.CTkLabel(app, text="0%")
pPercentage.pack()

progressBar = customtkinter.CTkProgressBar(app, width=400)
progressBar.set(0)
progressBar.pack(padx=10, pady=10)

download = customtkinter.CTkButton(app, text="Download", command=startDownload)
download.pack(padx=10, pady=10)

app.mainloop()
