import logging
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN

# Create a Pyrogram Client
app = Client("get_file_id_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.photo)
def get_file_id(client, message):
    file_id = message.photo.file_id
    print(f"File ID: {file_id}")
    message.reply_text(f"File ID: {file_id}")

if __name__ == "__main__":
    app.run()
