from urllib.parse import parse_qs, urlparse
import telepot
import os
import yt_dlp

# Replace 'YOUR_BOT_TOKEN' with the token you got from the BotFather
TOKEN = '6667935998:AAEis9NZuMpgyAAjFJ9efdqhseu-XA2IBcw'

# Specify the folder where you want to save the downloaded files
download_folder = r'D:\TelegramBot\download'

# Replace 'v_downloadMasterHub' with your Telegram channel username
CHANNEL_USERNAME = '@v_downloadMasterHub'

# Function to check if the user is a member of the channel
def is_user_member(user_id):
    try:
        # Use the getChatMember method to check if the user is a member of the channel
        member_status = bot.getChatMember(CHANNEL_USERNAME, user_id)['status']
        return member_status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking user membership: {str(e)}")
        return False

# Function to handle incoming messages
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == 'text':
        command = msg['text'].lower()

        if command == '/start':
            user_name = msg['from']['first_name']
            welcome_message = f"Hello {user_name}! Welcome to your bot.\n" \
                              "Available commands:\n" \
                              "/start - Welcome message\n" \
                              "/help - Display available commands\n" \
                              "/download - Download a YouTube video"

            bot.sendMessage(chat_id, welcome_message)

        elif command == '/help':
            help_message = f"To use the download feature, please join our channel: {CHANNEL_USERNAME}\n" \
                           "After joining, use the /download command to download a YouTube video."

            bot.sendMessage(chat_id, help_message)

        elif command == '/download':
            # Check if the user is a member of the channel
            if is_user_member(chat_id):
                bot.sendMessage(chat_id, "Please provide the YouTube link you want to download.")
                # Set the user state to 'waiting_for_link'
                user_states[chat_id] = 'waiting_for_link'
            else:
                bot.sendMessage(chat_id, f"To use the download feature, please join our channel: {CHANNEL_USERNAME}")

        elif user_states.get(chat_id) == 'waiting_for_link':
            # Display a 'Please wait a moment' message
            bot.sendMessage(chat_id, "Please wait a moment...")

            # Assume the user is providing a YouTube link
            youtube_link = msg['text']

            # Extract video ID from the link
            video_id = extract_video_id(youtube_link)

            if video_id:
                try:
                    # Display a 'Downloading in process...' message
                    bot.sendMessage(chat_id, "Downloading in process...")

                    # Ask the user for quality options
                    quality_options = [
                        'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                        'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                        'best[ext=mp4]',
                    ]
                    keyboard = {
                        'keyboard': [[f'/quality_{i+1}' for i, _ in enumerate(quality_options)]],
                        'one_time_keyboard': True,
                    }
                    bot.sendMessage(chat_id, "Select the quality option:", reply_markup=keyboard)

                    # Set the user state to 'waiting_for_quality'
                    user_states[chat_id] = 'waiting_for_quality'
                    user_data[chat_id] = {'youtube_link': youtube_link, 'video_id': video_id}

                except Exception as e:
                    bot.sendMessage(chat_id, f"Error: {str(e)}")
            else:
                bot.sendMessage(chat_id, "Error: Invalid YouTube link format.")

        elif user_states.get(chat_id) == 'waiting_for_quality':
            # Assume the user is selecting a quality option
            selected_option = msg['text'].split('_')[-1]
            quality_options = [
                'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                'best[ext=mp4]',
            ]

            try:
                # Display a 'Downloading in process...' message
                bot.sendMessage(chat_id, "Downloading in process...")
                bot.sendMessage(chat_id, "If Download Failed or any error Then please try Other qualities also Thank You......... ")

                ydl_opts = {
                    'format': quality_options[int(selected_option) - 1],
                    'outtmpl': os.path.join(download_folder, f"{user_data[chat_id]['video_id']}.%(ext)s"),
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(user_data[chat_id]['youtube_link'], download=True)
                    file_path = ydl.prepare_filename(info_dict)

                # Send the downloaded video
                bot.sendVideo(chat_id, open(file_path, 'rb'), caption="Here is your video!")

                # Remove the downloaded file after sending
                os.remove(file_path)

            except Exception as e:
                bot.sendMessage(chat_id, f"Error: {str(e)}")

            # Reset the user state
            del user_states[chat_id]
            del user_data[chat_id]

        else:
            bot.sendMessage(chat_id, 'I do not understand that command. Available commands: /start, /help, /download')

def extract_video_id(link):
    parsed_url = urlparse(link)
    video_id = None

    if 'youtu.be' in parsed_url.netloc:
        video_id = parsed_url.path[1:]
    elif 'youtube.com' in parsed_url.netloc:
        query = parse_qs(parsed_url.query)
        video_id = query.get('v', [None])[0]

    return video_id if video_id else None

# Create a bot instance
bot = telepot.Bot(TOKEN)

# Register the message handler
bot.message_loop(handle)

# Dictionary to keep track of users in the process of downloading
user_states = {}
user_data = {}

print('Bot is running. Press Ctrl+C to stop.')

# Keep the program running
while True:
    pass
