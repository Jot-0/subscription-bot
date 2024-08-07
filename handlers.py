import schedule
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import OWNER_ID
from scheduler import check_subscriptions
from state import subscribed_users, awaiting_utr, awaiting_plan, awaiting_new_plan

# Dictionary to store custom messages
custom_messages = {
    'start': ('⭐️ Powered By ❤️ AJxLeech Mirror\n\n'
              '➡️ UNZIP ALLOWED ✅\n'
              '➡️ ZIP ALLOW ✅\n'
              '➡️ PRIMUM LEECH 4GB ✅\n'
              '➡️ MIRROR ALLOWED ✅\n'
              '➡️ CLONE ALLOWED ✅\n'
              '➡️ YTDL LEECH ALLOWED ✅\n'
              '➡️ TORRENT SEARCH ✅\n'
              '➡️ METADATA SUPPORT ✅\n'
              '➡️ TERA BOX LINK SUPPORT ✅\n'
              '➡️ JIO DRIVE LINK SUPPORT ✅\n'
              '➡️ MEGA LINK SUPPORT ✅\n'
              '➡️ Support YouTube playlist & Link ✅\n'
              '➡️ TeamDrive and Gdrive link Support ✅\n'
              '➡️ NSFW ALLOW ✅\n'
              '➡️ Bot Run 24/7 ✅\n'
              '➡️ 1TB Bot Storage ✅\n'
              '➡️ Log Or Dump Access ✅\n'
              '➡️ Instant Released Ott Movies Web Series Files ✅\n\n'
              'Note - Slots are available on a first-come, first-served basis. Once all slots are filled, the timing for the next available slot is unknown.\n\n'
              '🔹 Cheap Price 2️⃣\n\n'
              '💯 Contact @Sam_Dude2 🐼\n\n'
              '➡️ Proof - @All_ott_Primium_proof\n\n'
              '➡️ https://t.me/All_Ott_Premium01'),
    'start_image': 'AgACAgUAAxkBAAMtZrMErIvhuIiSpnM7AAFU9QI9o2RUAAIqwDEbNWOZVQ-9vsXDAAEOcgAIAQADAgADeQAHHgQ'  # Replace with the correct file ID
}

def register_handlers(app: Client):
    @app.on_message(filters.command("start"))
    def start(client: Client, message: Message):
        client.send_photo(chat_id=message.chat.id, photo=custom_messages['start_image'], caption=custom_messages['start'])

    @app.on_message(filters.command("set_start") & filters.user(OWNER_ID))
    def set_start(client: Client, message: Message):
        if len(message.command) > 1:
            custom_messages['start'] = ' '.join(message.command[1:])
            message.reply_text('Start message updated!')
        else:
            message.reply_text('Please provide a new start message.')

    @app.on_message(filters.command("add_user") & filters.user(OWNER_ID))
    def add_user(client: Client, message: Message):
        if len(message.command) > 1:
            user_id = int(message.command[1])
            try:
                user = client.get_users(user_id)
                # Automatically set the start date
                start_date = datetime.now().strftime("%d/%m/%Y")
                subscribed_users[user.id] = {
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'start_date': start_date  # Save the start date
                }
                awaiting_utr[user.id] = True
                message.reply_text(f'User {user.first_name} ({user.username}) added successfully! Please send their UTR number.')
                print(f"User {user.id} added. Awaiting UTR.")
            except Exception as e:
                message.reply_text(f'Failed to add user: {e}')
        else:
            message.reply_text('Please provide a user ID.')

    @app.on_message(filters.text & filters.user(OWNER_ID))
    def collect_utr(client: Client, message: Message):
        user_id = message.from_user.id
        print(f"collect_utr triggered for user_id: {user_id}")  # Debug print
        if user_id in awaiting_utr:
            print(f"awaiting_utr found for user_id: {user_id}")  # Debug print
            subscribed_users[user_id]['utr_number'] = message.text
            print(f"UTR number {message.text} saved for user_id: {user_id}")  # Debug print
            del awaiting_utr[user_id]
            awaiting_plan[user_id] = True
            message.reply_text('UTR number saved! Now please send the subscription plan end date (DD/MM/YYYY).')
        elif user_id in awaiting_plan:
            print(f"awaiting_plan found for user_id: {user_id}")  # Debug print
            try:
                plan_end_date = datetime.strptime(message.text, "%d/%m/%Y").strftime("%d/%m/%Y")
                subscribed_users[user_id]['plan_end_date'] = plan_end_date
                print(f"Plan end date {plan_end_date} saved for user_id: {user_id}")  # Debug print
                del awaiting_plan[user_id]
                message.reply_text('Subscription plan end date saved! User has been fully registered.')
                send_confirmation_message(client, user_id)
            except ValueError:
                message.reply_text('Invalid date format. Please use DD/MM/YYYY.')
        elif user_id in awaiting_new_plan:
            print(f"awaiting_new_plan found for user_id: {user_id}")  # Debug print
            try:
                plan_end_date = datetime.strptime(message.text, "%d/%m/%Y").strftime("%d/%m/%Y")
                subscribed_users[user_id]['plan_end_date'] = plan_end_date
                print(f"New plan end date {plan_end_date} saved for user_id: {user_id}")  # Debug print
                del awaiting_new_plan[user_id]
                message.reply_text('Subscription plan end date updated!')
            except ValueError:
                message.reply_text('Invalid date format. Please use DD/MM/YYYY.')

    def send_confirmation_message(client: Client, user_id: int):
        user = subscribed_users.get(user_id)
        if user:
            start_date = user.get('start_date', 'N/A')
            plan_end_date = user.get('plan_end_date', 'N/A')
            message_text = (
                f"Your subscription plan has started on {start_date}. It will end on {plan_end_date}. "
                f"Please contact @Sam_Dude2 if you have any questions."
            )
            client.send_message(user_id, message_text)
            print(f"Confirmation message sent to user_id: {user_id}")  # Debug print

    @app.on_message(filters.command("all_users") & filters.user(OWNER_ID))
    def all_users(client: Client, message: Message):
        if subscribed_users:
            buttons = [
                [InlineKeyboardButton(f"{user['first_name']} ({user_id})", callback_data=str(user_id))]
                for user_id, user in subscribed_users.items()
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            message.reply_text("List of all users:", reply_markup=reply_markup)
        else:
            message.reply_text("No users found.")

    @app.on_message(filters.command("help") & filters.user(OWNER_ID))
    def help_command(client: Client, message: Message):
        help_text = (
            "/start - Start the bot and see the welcome message\n"
            "/set_start <message> - Set a new start message (Owner only)\n"
            "/add_user <user_id> - Add a user by their Telegram ID (Owner only)\n"
            "/remove_user <user_id> - Remove a user by their Telegram ID (Owner only)\n"
            "/all_users - List all users with inline buttons (Owner only)\n"
            "/user_info <user_id> - Get user information and actions (Owner only)\n"
            "/help - Show this help message"
        )
        message.reply_text(help_text)

    @app.on_message(filters.command("remove_user") & filters.user(OWNER_ID))
    def remove_user(client: Client, message: Message):
        if len(message.command) > 1:
            user_id = int(message.command[1])
            if user_id in subscribed_users:
                del subscribed_users[user_id]
                message.reply_text(f'User with ID {user_id} has been removed successfully.')
                print(f"User with ID {user_id} removed.")  # Debug print
            else:
                message.reply_text(f'User with ID {user_id} not found.')
        else:
            message.reply_text('Please provide a user ID.')

    @app.on_message(filters.command("user_info") & filters.user(OWNER_ID))
    def user_info(client: Client, message: Message):
        if len(message.command) > 1:
            user_id = int(message.command[1])
            user = subscribed_users.get(user_id)
            if user:
                details = (
                    f"User Details:\n"
                    f"First Name: {user['first_name']}\n"
                    f"Last Name: {user['last_name']}\n"
                    f"Username: {user['username']}\n"
                    f"UTR Number: {user.get('utr_number', 'N/A')}\n"
                    f"Start Date: {user.get('start_date', 'N/A')}\n"
                    f"Subscription End Date: {user.get('plan_end_date', 'N/A')}"
                )
                buttons = [
                    [InlineKeyboardButton("Remove User", callback_data=f"remove_{user_id}"),
                     InlineKeyboardButton("Edit Plan", callback_data=f"edit_{user_id}")]
                ]
                reply_markup = InlineKeyboardMarkup(buttons)
                message.reply_text(details, reply_markup=reply_markup)
            else:
                message.reply_text("User not found.")
        else:
            message.reply_text('Please provide a user ID.')

    @app.on_callback_query()
    def callback_query_handler(client: Client, callback_query: CallbackQuery):
        data = callback_query.data
        if data.startswith("remove_"):
            user_id = int(data.split("_")[1])
            if user_id in subscribed_users:
                del subscribed_users[user_id]
                callback_query.message.edit_text(f'User with ID {user_id} has been removed successfully.')
            else:
                callback_query.message.edit_text('User not found.')
        elif data.startswith("edit_"):
            user_id = int(data.split("_")[1])
            awaiting_new_plan[user_id] = True
            callback_query.message.edit_text(f'Please send the new subscription plan end date for user ID {user_id} (DD/MM/YYYY).')

    @app.on_message(filters.text & filters.user(OWNER_ID))
    def collect_new_plan_date(client: Client, message: Message):
        user_id = message.from_user.id
        print(f"collect_new_plan_date triggered for user_id: {user_id}")  # Debug print
        if user_id in awaiting_new_plan:
            print(f"awaiting_new_plan found for user_id: {user_id}")  # Debug print
            try:
                # Convert date to desired format
                plan_end_date = datetime.strptime(message.text, "%d/%m/%Y").strftime("%d/%m/%Y")
                subscribed_users[user_id]['plan_end_date'] = plan_end_date
                del awaiting_new_plan[user_id]
                message.reply_text('Subscription plan end date updated!')
            except ValueError:
                message.reply_text('Invalid date format. Please use DD/MM/YYYY.')

def main():
    app = Client("my_bot")
    register_handlers(app)
    app.run()

if __name__ == "__main__":
    main()
