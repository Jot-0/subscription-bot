from pyrogram import Client, filters
from pyrogram.types import Message
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

    @app.on_message(filters.text & filters.user(OWNER_ID))
    def collect_utr(client: Client, message: Message):
        user_id = message.from_user.id  # Correctly use the sender's user ID
        print(f"DEBUG: collect_utr triggered for user_id: {user_id}")
        print(f"DEBUG: awaiting_utr before check: {awaiting_utr}")
        if user_id in awaiting_utr:
            print(f"DEBUG: awaiting_utr found for user_id: {user_id}")
            subscribed_users[user_id]['utr_number'] = message.text
            print(f"DEBUG: UTR number {message.text} saved for user_id: {user_id}")
            del awaiting_utr[user_id]
            awaiting_plan[user_id] = True
            message.reply_text('UTR number saved! Now please send the subscription plan end date (DD/MM/YYYY).')
            print(f"DEBUG: awaiting_plan: {awaiting_plan}")
        elif user_id in awaiting_plan:
            print(f"DEBUG: awaiting_plan found for user_id: {user_id}")
            try:
                plan_end_date = datetime.strptime(message.text, "%d/%m/%Y").strftime("%d/%m/%Y")
                subscribed_users[user_id]['plan_end_date'] = plan_end_date
                print(f"DEBUG: Plan end date {plan_end_date} saved for user_id: {user_id}")
                del awaiting_plan[user_id]
                message.reply_text('Subscription plan end date saved! User has been fully registered.')
            except ValueError:
                message.reply_text('Invalid date format. Please use DD/MM/YYYY.')
        else:
            print(f"DEBUG: user_id {user_id} not found in awaiting_utr or awaiting_plan")

def main():
    app.run()

if __name__ == "__main__":
    main()
