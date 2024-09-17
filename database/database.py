from pymongo import MongoClient
from datetime import datetime, timedelta

class SubscriptionDB:
    def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="subscription_db", collection_name="users"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def add_user(self, user_id, subscription_end):
        user_data = {
            "user_id": user_id,
            "subscription_end": subscription_end
        }
        self.collection.insert_one(user_data)
        print(f"User {user_id} added with subscription ending on {subscription_end}")

    def find_user(self, user_id):
        user = self.collection.find_one({"user_id": user_id})
        return user

    def update_subscription(self, user_id, additional_days):
        current_user = self.find_user(user_id)
        if current_user:
            new_end_date = datetime.now() + timedelta(days=additional_days)
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"subscription_end": new_end_date}}
            )
            print(f"Subscription for user {user_id} updated to {new_end_date}")
        else:
            print(f"User {user_id} not found.")

    def check_subscription_status(self, user_id):
        user = self.find_user(user_id)
        if user:
            subscription_end = user.get("subscription_end")
            if subscription_end and subscription_end > datetime.now():
                return True  # Subscription is active
            else:
                return False  # Subscription expired
        else:
            return None  # User not found

    def remove_expired_users(self):
        expired_users = self.collection.find({"subscription_end": {"$lt": datetime.now()}})
        for user in expired_users:
            print(f"Removing expired user: {user['user_id']}")
            self.collection.delete_one({"user_id": user['user_id']})

# Example usage
if __name__ == "__main__":
    db = SubscriptionDB()

    # Add a new user with 30 days subscription
    db.add_user(user_id=12345, subscription_end=datetime.now() + timedelta(days=30))

    # Update an existing user’s subscription by 30 more days
    db.update_subscription(user_id=12345, additional_days=30)

    # Check if a user's subscription is still active
    is_active = db.check_subscription_status(user_id=12345)
    print(f"User 12345 active: {is_active}")

    # Remove all users with expired subscriptions
    db.remove_expired_users()
          
