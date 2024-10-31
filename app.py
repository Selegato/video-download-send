import asyncio
import math
import os
import threading
import tkinter as tk
from pathlib import Path

import customtkinter as ctk
from dotenv import load_dotenv
from moviepy.editor import AudioFileClip, VideoFileClip
from proglog import ProgressBarLogger
from pytubefix import YouTube
from pytubefix.exceptions import RegexMatchError, VideoUnavailable
from telegram import Bot

load_dotenv()

# check https://github.com/JuanBindez/pytubefix/pull/209
# youtube visitor obscure data bots
# visitor data = "Cgt5N2ZWSVFWdjZYNCjOooO5BjIKCgJVQRIEGgAgRw%3D%3D"
# TOKEN = "MnQJfFUsWeQ_4wlEmqVkmS-nClTE45T2HqUo_bYi3cYqpJVauW-iv2BiTI4OfQBJKVoGTDcdHn5Ecr2ErUhvyGd0M7M5JPvupPrJkB0R6JK_xg_VcgvKkWbYUKxEyZY4ZwI3Bzk-BHqMchV3Ir6TTEgbDJHQ3A=="


# Configurations
MAX_SIZE = 50  # max size of files in MB
VIDEO_SCALE = 0.5  # scale of the video to be resized
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_CHAT_ID = os.getenv("MY_CHAT_ID")


class MyBarLogger(ProgressBarLogger):
    def bars_callback(self, bar, attr, value, old_value=None) -> None:
        """Callback function to update the progress bar while is converting"""
        percentage = (value / self.bars[bar]["total"]) * 100
        processed_per_con = "{:.2f}".format(percentage)
        text_percentage.configure(text=f"Converting: {processed_per_con}%")
        text_percentage.update_idletasks()
        download_progress.set(round(float(percentage), 2) / 100)


class MaxSizeFile(Exception):
    """Raised when the file is larger than 50MB"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def convert_file(input_path: str) -> str:
    """convert a file to a smaller resolution/size"""
    logger = MyBarLogger()
    if input_path.endswith(".m4a"):
        file_name = Path(input_path).stem
        audio = AudioFileClip(input_path)
        resized_filename = f"{file_name}_resized.m4a"
        audio.write_audiofile(
            resized_filename, codec="aac", bitrate="50k", logger=logger
        )
        return resized_filename
    elif input_path.endswith(".mp4"):
        file_name = Path(input_path).stem
        clip = VideoFileClip(input_path)
        resized_clip = clip.resize(VIDEO_SCALE)
        resized_filename = f"{file_name}_resized.mp4"
        resized_clip.write_videofile(resized_filename, threads=4, logger=logger)
        return resized_filename


async def send_to_telegram(file_path: str) -> None:
    """Sends a file to a telegram chat"""
    with open(file_path, "rb") as file:
        bot = Bot(BOT_TOKEN)
        if file_path.endswith(".mp4"):
            await bot.send_video(MY_CHAT_ID, file)
        if file_path.endswith(".m4a"):
            await bot.send_audio(MY_CHAT_ID, file)


def download_handler(url_vid: str, loc_send: str, aud_vid: str) -> None:
    """Starts the download process in a new thread"""
    threading.Thread(target=fetch_video, args=(url_vid, loc_send, aud_vid)).start()


def check_size(file_path) -> int:
    """Check the size of a file in MB"""
    file_size = Path(file_path).stat().st_size
    file_size_mb = math.floor(file_size / (1024 * 1024))
    return file_size_mb


def on_download_progress(stream, chunk, bytes_remaining) -> None:
    """Callback function to update the progress bar while is downloading"""
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    processed_per = str(int(percentage))
    text_percentage.configure(text=f"Downloading: {processed_per}%")
    text_percentage.update_idletasks()
    download_progress.set(float(processed_per) / 100)


def sending_telegram_message() -> None:
    """Update the title label to show the current status sending to telegram"""
    title_label.configure(text="Sending to telegram", text_color="green")
    title_label.update_idletasks()


def check_telegram_message() -> None:
    """Update the title label to show the current status check telegram"""
    title_label.configure(text="Check your Telegram", text_color="green")
    title_label.update_idletasks()


def conversion_finished_message() -> None:
    """Update the title label to show the current status conversion finished"""
    title_label.configure(text="Conversion finished", text_color="green")
    title_label.update_idletasks()


def file_large_message() -> None:
    title_label.configure(
        text="File is larger than 50MB.Converting... Please Wait.",
        text_color="yellow",
    )
    title_label.update_idletasks()


def fetch_video(url, selector_loc_send, selector_aud_vid):
    # update the title label to show the current status
    title_label.configure(
        text=f"{selector_aud_vid.capitalize()} - Trying to Download..."
    )
    title_label.update_idletasks()
    try:
        # create a YouTube object
        yt = YouTube(url, use_po_token=True, on_progress_callback=on_download_progress)

        # selector audio
        if selector_aud_vid == "audio":
            # selector of save location
            if selector_loc_send == "local":
                yt.streams.get_audio_only().download()
                title_label.configure(text="Audio downloaded")
                return
            else:  # selector of send location
                audio_path = yt.streams.get_audio_only().download()
                # check size of file
                file_size_mb = check_size(audio_path)
                # if file is smaller than MAXSIZE, send to telegram
                if file_size_mb < MAX_SIZE:
                    # update the title label to show the current status
                    sending_telegram_message()
                    # send to telegram
                    asyncio.run(send_to_telegram(audio_path))
                    # delete the file
                    Path(audio_path).unlink()
                    # update the title label to show the current status
                    check_telegram_message()
                    return
                else:  # file is bigger than MAXSIZE
                    # update the title label to show the current status
                    file_large_message()
                    # convert the file
                    resized_filename = convert_file(audio_path)
                    # update the title label to show the current status
                    conversion_finished_message()
                    # check the size of the file
                    audio_size_mb = check_size(resized_filename)
                    # if the file is smaller than MAXSIZE, send to telegram
                    if audio_size_mb < MAX_SIZE:
                        # update the title label to show the current status
                        sending_telegram_message()
                        # send to telegram
                        asyncio.run(send_to_telegram(resized_filename))
                        # update the title label to show the current status
                        check_telegram_message()
                        # delete the files
                        Path(audio_path).unlink()
                        Path(resized_filename).unlink()
                        return
                    else:
                        # after 2 convertions if the file is still bigger than MAXSIZE, raise an exception
                        raise MaxSizeFile("Audio file is larger than 50MB")
        else:  # selector video
            # selector of save location
            if selector_loc_send == "local":
                yt.streams.get_highest_resolution().download()
                title_label.configure(text="Video downloaded")
            else:  # selector of send location
                video_path = yt.streams.get_highest_resolution().download()
                # check the size of the file
                file_size_mb = check_size(video_path)
                # if the file is smaller than MAXSIZE, send to telegram
                if file_size_mb < MAX_SIZE:
                    # update the title label to show the current status
                    sending_telegram_message()
                    # send to telegram
                    asyncio.run(send_to_telegram(video_path))
                    # delete the file
                    Path(video_path).unlink()
                    check_telegram_message()
                    return
                else:  # file is bigger than MAXSIZE
                    file_large_message()
                    # convert the file
                    resized_filename = convert_file(video_path)
                    # update the title label to show the current status
                    title_label.configure(text="Conversion finished")
                    title_label.update_idletasks()
                    # check the size of the file
                    file_size_mb = check_size(resized_filename)
                    # if the file is smaller than MAXSIZE, send to telegram
                    if file_size_mb < MAX_SIZE:
                        # update the title label to show the current status
                        sending_telegram_message()
                        # send to telegram
                        asyncio.run(send_to_telegram(resized_filename))
                        # update the title label to show the current status
                        check_telegram_message()
                        # delete the files
                        Path(video_path).unlink()
                        Path(resized_filename).unlink()
                        return
                    else:  # file is still bigger than MAXSIZE second convertion
                        title_label.configure(
                            text="File still too big, converting again",
                            text_color="yellow",
                        )
                        title_label.update_idletasks()
                        # convert the file
                        resized_resized_filename = convert_file(resized_filename)
                        # update the title label to show the current status
                        conversion_finished_message()
                        # check the size of the file
                        file_size_mb = check_size(resized_resized_filename)
                        # if the file is smaller than MAXSIZE, send to telegram
                        if file_size_mb < MAX_SIZE:
                            # update the title label to show the current status
                            sending_telegram_message()
                            # send to telegram
                            asyncio.run(send_to_telegram(resized_resized_filename))
                            # update the title label to show the current status
                            check_telegram_message()
                            # delete the files
                            Path(video_path).unlink()
                            Path(resized_filename).unlink()
                            Path(resized_resized_filename).unlink()
                            return
                        else:  # file is still bigger than MAXSIZE give up
                            Path(resized_filename).unlink()
                            Path(resized_resized_filename).unlink()
                            raise MaxSizeFile(
                                "Video file is larger than 50MB, Cant be send"
                            )

    except MaxSizeFile:
        title_label.configure(
            text="Error: Video file is still larger than 50MB.", text_color="red"
        )
    except RegexMatchError:
        title_label.configure(text="Error: URL inválida", text_color="red")

    except VideoUnavailable:
        title_label.configure(text="Error: Vídeo não disponível", text_color="red")

    except Exception as e:
        title_label.configure(text="Error", text_color="red")


def main():
    global title_label, text_percentage, download_progress

    # Interface
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Frame
    app = ctk.CTk()
    app.geometry("650x300")
    app.title("Video Helper - Paulo Selegato")

    # Title
    main_title = ctk.CTkLabel(app, text="My Video Helper", font=("Arial", 24, "bold"))
    main_title.pack(padx=20, pady=(20, 10))

    # Frame Input
    input_frame = ctk.CTkFrame(app)
    input_frame.pack(padx=20, pady=20)

    # Link input
    url_vid = tk.StringVar()
    link_field = ctk.CTkEntry(
        input_frame, width=450, height=40, font=("Arial", 16), textvariable=url_vid
    )
    link_field.pack(side="left", padx=20, pady=20)

    # Download button
    download_button = ctk.CTkButton(
        input_frame,
        text="Download",
        font=("Arial", 16, "bold"),
        command=lambda: download_handler(
            url_vid.get(), selector_loc_send.get(), selector_aud_vid.get()
        ),
    )
    download_button.pack(side="left", padx=(0, 5))

    # Frame for Audio/Video Radio Buttons
    frame_aud_vid = ctk.CTkFrame(app)
    frame_aud_vid.pack(side="left", padx=(20, 10), pady=(0, 0))

    selector_aud_vid = tk.StringVar(value="video")  # Default value
    rad_vid = ctk.CTkRadioButton(
        frame_aud_vid, text="Video", variable=selector_aud_vid, value="video"
    )
    rad_aud = ctk.CTkRadioButton(
        frame_aud_vid, text="Audio", variable=selector_aud_vid, value="audio"
    )
    rad_vid.pack(pady=5)
    rad_aud.pack(pady=5)

    # Frame for Local/Send Radio Buttons
    frame_loc_send = ctk.CTkFrame(app)
    frame_loc_send.pack(side="left", padx=(10, 20), pady=(0, 0))

    selector_loc_send = tk.StringVar(value="send")  # Default value
    rad_send = ctk.CTkRadioButton(
        frame_loc_send, text="Send", variable=selector_loc_send, value="send"
    )
    rad_loc = ctk.CTkRadioButton(
        frame_loc_send, text="Local", variable=selector_loc_send, value="local"
    )
    rad_send.pack(pady=5)
    rad_loc.pack(pady=5)

    # Label to show the video title or error message
    title_label = ctk.CTkLabel(app, text="", font=("Arial", 12))
    title_label.pack(padx=20, pady=10)

    # Text percentage download
    text_percentage = ctk.CTkLabel(app, text="0%", font=("Arial", 15))
    text_percentage.pack(padx=20, pady=0)

    # Progress bar
    download_progress = ctk.CTkProgressBar(app, width=400, height=20)
    download_progress.set(0)
    download_progress.pack(padx=20, pady=0)

    app.mainloop()


if __name__ == "__main__":
    main()
