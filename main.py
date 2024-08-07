import logging
from pyrogram import Client
from handlers import register_handlers
from scheduler import run_scheduler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your API ID, API hash, and bot token
from config import API_ID, API_HASH, BOT_TOKEN

# Create a Pyrogram Client
app = Client("subscription_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

if __name__ == "__main__":
    # Register command and message handlers
    register_handlers(app)

    # Start the Pyrogram client
    app.start()

    # Run the scheduler in a separate thread and pass the app instance
    import threading
    scheduler_thread = threading.Thread(target=run_scheduler, args=(app,))
    scheduler_thread.start()

    # Run the bot
    app.idle()
