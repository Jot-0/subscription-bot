import schedule
import time
from datetime import datetime, timedelta
from pyrogram import Client
from config import OWNER_ID
from state import subscribed_users

def check_subscriptions(app: Client):
    today = datetime.now().date()
    two_days_later = today + timedelta(days=2)
    
    for user_id, user_info in subscribed_users.items():
        plan_end_date = datetime.strptime(user_info['plan_end_date'], "%d/%m/%Y").date()
        start_date = user_info.get('start_date', 'N/A')

        if plan_end_date == two_days_later:
            # Send reminder 2 days before end date
            message_text = (
                f"Reminder: Your subscription plan started on {start_date} and will end in 2 days on {plan_end_date.strftime('%d/%m/%Y')}. "
                f"Please contact @Sam_Dude2 to renew your subscription."
            )
            app.send_message(user_id, message_text)
            app.send_message(OWNER_ID, f"Reminder: {user_info['first_name']}'s subscription started on {start_date} and will end in 2 days.")

        if plan_end_date == today:
            # Send notification on the end date
            message_text = (
                f"Your subscription plan started on {start_date} and ends today. Please contact @Sam_Dude2 to renew your subscription."
            )
            app.send_message(user_id, message_text)
            app.send_message(OWNER_ID, f"Notification: {user_info['first_name']}'s subscription started on {start_date} and ends today.")

# Schedule the job daily at 12:00 PM
def run_scheduler(app: Client):
    schedule.every().day.at("12:00").do(check_subscriptions, app)

    while True:
        schedule.run_pending()
        time.sleep(1)
