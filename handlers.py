from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import OWNER_ID
from state import subscribed_users, awaiting_utr, awaiting_plan
from datetime import datetime

def register_handlers(app: Client):

    @app.on_message(filters.command("start"))
    def start(client: Client, message: Message):
        message.reply_text("Bot is working!")

    @app.on_message(filters.command("help"))
    def help_command(client: Client, message: Message):
        help_text = (
            "Available commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/add_user <user_id> - Add a user\n"
            "/remove_user <user_id> - Remove a user\n"
            "/all_users - List all users\n"
            "/user_info <user_id> - Get user information\n"
        )
        message.reply_text(help_text)

    @app.on_message(filters.command("add_user") & filters.user(OWNER_ID))
    def add_user(client: Client, message: Message):
        if len(message.command) > 1:
            user_id = int(message.command[1])
            try:
                user = client.get_users(user_id)
                start_date = datetime.now().strftime("%d/%m/%Y")
                subscribed_users[user.id] = {
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'start_date': start_date
                }
                awaiting_utr[user.id] = True
                message.reply_text(f"User {user.first_name} ({user.username}) added successfully! Please send their UTR number.")
                print(f"DEBUG: User {user.id} added. Awaiting UTR.")
                print(f"DEBUG: awaiting_utr: {awaiting_utr}")
            except Exception as e:
                message.reply_text(f"Failed to add user: {e}")
                print(f"DEBUG: Error adding user: {e}")
        else:
            message.reply_text("Please provide a user ID.")

    @app.on_message(filters.text & filters.user(OWNER_ID) & filters.create(lambda _, __, message: bool(awaiting_utr) or bool(awaiting_plan)))
    def collect_utr(client: Client, message: Message):
        user_id = next(iter(awaiting_utr), None) or next(iter(awaiting_plan), None)
        print(f"DEBUG: collect_utr triggered for user_id: {user_id}")
        print(f"DEBUG: awaiting_utr before check: {awaiting_utr}")
        print(f"DEBUG: awaiting_plan before check: {awaiting_plan}")

        if user_id and user_id in awaiting_utr:
            print(f"DEBUG: awaiting_utr found for user_id: {user_id}")
            subscribed_users[user_id]['utr_number'] = message.text
            print(f"DEBUG: UTR number {message.text} saved for user_id: {user_id}")
            del awaiting_utr[user_id]
            awaiting_plan[user_id] = True
            message.reply_text('UTR number saved! Now please send the subscription plan end date (DD/MM/YYYY).')
            print(f"DEBUG: awaiting_plan: {awaiting_plan}")
        elif user_id and user_id in awaiting_plan:
            print(f"DEBUG: awaiting_plan found for user_id: {user_id}")
            try:
                plan_end_date = datetime.strptime(message.text, "%d/%m/%Y").strftime("%d/%m/%Y")
                subscribed_users[user_id]['plan_end_date'] = plan_end_date
                print(f"DEBUG: Plan end date {plan_end_date} saved for user_id: {user_id}")
                del awaiting_plan[user_id]
                message.reply_text('Subscription plan end date saved! User has been fully registered.')
                
                # Send confirmation messages
                client.send_message(user_id, f"Your subscription has been registered.\nStart Date: {subscribed_users[user_id]['start_date']}\nEnd Date: {plan_end_date}")
                client.send_message(OWNER_ID, f"User {subscribed_users[user_id]['first_name']} ({user_id}) subscription registered.\nStart Date: {subscribed_users[user_id]['start_date']}\nEnd Date: {plan_end_date}")
                
            except ValueError:
                print(f"DEBUG: ValueError for date {message.text}")
                message.reply_text('Invalid date format. Please use DD/MM/YYYY.')
        else:
            print(f"DEBUG: user_id {user_id} not found in awaiting_utr or awaiting_plan")
            message.reply_text("No user is currently awaiting input. Please start by adding a user.")

    @app.on_message(filters.command("all_users") & filters.user(OWNER_ID))
    def all_users(client: Client, message: Message):
        if subscribed_users:
            buttons = [
                [InlineKeyboardButton(f"{user['first_name']} ({user_id})", callback_data=f"info_{user_id}")]
                for user_id, user in subscribed_users.items()
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            message.reply_text("List of all users:", reply_markup=reply_markup)
        else:
            message.reply_text("No users found.")

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
            message.reply_text("Please provide a user ID.")

    @app.on_message(filters.command("remove_user") & filters.user(OWNER_ID))
    def remove_user(client: Client, message: Message):
        if len(message.command) > 1:
            user_id = int(message.command[1])
            if user_id in subscribed_users:
                del subscribed_users[user_id]
                message.reply_text(f"User {user_id} has been removed.")
                print(f"DEBUG: User {user_id} removed.")
            else:
                message.reply_text("User not found.")
        else:
            message.reply_text("Please provide a user ID.")

    @app.on_callback_query()
    def callback_query_handler(client: Client, callback_query: CallbackQuery):
        data = callback_query.data
        user_id = int(data.split("_")[1])
        if data.startswith("info_"):
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
                callback_query.message.edit_text(details, reply_markup=reply_markup)
            else:
                callback_query.answer("User not found.")
        elif data.startswith("remove_"):
            if user_id in subscribed_users:
                del subscribed_users[user_id]
                callback_query.answer("User removed successfully.")
                callback_query.message.edit_text(f"User {user_id} has been removed.")
            else:
                callback_query.answer("User not found.")
        elif data.startswith("edit_"):
            callback_query.message.reply_text("Please send the new subscription plan end date (DD/MM/YYYY).")
            awaiting_plan[user_id] = True

def main():
    app.run()

if __name__ == "__main__":
    main()
