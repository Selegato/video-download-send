# Download video, Send Telegram Bot

## Project Overview

"This is a simple automation project for downloading videos or audio from YouTube. It allows file conversion to smaller sizes if needed and offers the option to save them locally or send them directly to a private chat with my bot on Telegram."

## Objective

"Automate the process of downloading, converting, and sending audio from YouTube directly to Telegram quickly and efficiently."

## General User Flow

1. The user enters the YouTube video link in the input field.
2. Selects whether they want to download the video or just the audio.
3. Chooses whether to save the file locally or send it to Telegram.
4. Clicks the "Download" button to start the process.
5. The application downloads the video/audio from YouTube.
6. If the file is larger than 50MB, it is converted to a smaller size.
7. The file is either saved locally or sent to the Telegram chat, based on the user's choice.
8. The user receives a notification about the status of the download/conversion/sending process.

# Requirements and Features

## Front-End
- **customtkinter**

## Back-End
- **Python**

## Libraries
 - `moviepy` - for audio and video manipulation.
 - `pytubefix` - for download from youtube.
 - `python-telegram-bot` - integration with telegram.
 - `dotenv` - secrets management.

## Project Setup

### Prerequisites
- Python 3.10.11
- Pip (Python packet manager)
- Telegram App
- Telegram Bot





### Installation Instructions

#### Telegram Setup
1. Download, install, and set up your Telegram account on your app.
2. Create a New Bot:
   - Open Telegram and search for the “BotFather” (username: @BotFather).
   - Start a chat with BotFather and send the command `/newbot`.
   - Follow the prompts to choose a name and username for your bot.
   - Once completed, BotFather will provide you with an API token. Keep this token secure, as it’s used to control your bot.
3. Send a message to your bot.
4. Access the following URL with your bot token to get updates: `https://api.telegram.org/bot<YOUR BOT TOKEN>/getUpdates`
5. Copy the `id` **value** from the response, which looks like: `"message":{"message_id":42,"from":{"id":6030105186}}`
6. Save the variables in the `.env` file with the names `MY_CHAT_ID` and `BOT_TOKEN`.



#### Python Setup
1. Clone the repository and navigate to the root directory:
    ```sh
    git clone https://github.com/your-username/video-download-send.git
    cd video-helper
    ```
2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root of the project and add your Telegram credentials:
    ```env
    BOT_TOKEN="your_bot_token"
    MY_CHAT_ID="your_chat_id"
    ```


### Running the Application
To start the application, run the following command:
```sh
python [app.py](http://_vscodecontentref_/0)
```

### FAQ Problems

If you receive an input warning in the terminal asking for VisitorData and po_token, read and follow the procedures in this link:
It's a bot protection from YouTube.
[YouTube Bot Protection](https://github.com/JuanBindez/pytubefix/pull/209)