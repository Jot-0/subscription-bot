import time
from datetime import datetime, timedelta
from pyrogram import Client
from config import OWNER_ID
from state import subscribed_users

def check_subscriptions(client: Client):
    while True:
        current_date = datetime.now().date()
        for user_id, user in list(subscribed_users.items()):
            plan_end_date = datetime.strptime(user['plan_end_date'], "%d/%m/%Y").date()
            if plan_end_date == current_date:
                client.send_message(user_id, f"Your plan ends today.please renew your plan nor and for renew contact @Sam_Dude2.\nStart Date: {user['start_date']}\nEnd Date: {user['plan_end_date']}")
                client.send_message(OWNER_ID, f"User {user['first_name']} ({user_id})'s plan ends today.\nStart Date: {user['start_date']}\nEnd Date: {user['plan_end_date']}")
                print(f"DEBUG: Sent end date notification for user_id: {user_id}")
            elif plan_end_date == current_date + timedelta(days=2):
                client.send_message(user_id, f"Your plan will end in 2 days.please renew your plan after 2 days and for renew contact @Sam_Dude2.\nStart Date: {user['start_date']}\nEnd Date: {user['plan_end_date']}")
                client.send_message(OWNER_ID, f"User {user['first_name']} ({user_id})'s plan will end in 2 days.\nStart Date: {user['start_date']}\nEnd Date: {user['plan_end_date']}")
                print(f"DEBUG: Sent 2 days before end date notification for user_id: {user_id}")
        time.sleep(86400)  # Check once a day

def start_scheduler(client: Client):
    client.loop.run_in_executor(None, check_subscriptions, client)
