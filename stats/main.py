import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd

def connect_to_mongo(uri):
    client = MongoClient(uri)
    db = client['telegram_stats']
    return db

def fetch_messages(db):
    messages = db.messages.find()
    return list(messages)

def fetch_users(db):
    users = db.users.find()
    return list(users)

def plot_message_stats(messages):
    now = datetime.now()
    week_ago = now - timedelta(weeks=1)
    month_ago = now - timedelta(days=30)

    week_data = [msg for msg in messages if msg['date'] > week_ago]
    month_data = [msg for msg in messages if msg['date'] > month_ago]

    def group_by_day(data):
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df.resample('D').size().cumsum() + 246

    week_stats = group_by_day(week_data)
    month_stats = group_by_day(month_data)
    all_time_stats = group_by_day(messages)

    fig, axs = plt.subplots(3, 1, figsize=(10, 15))

    axs[0].plot(week_stats.index, week_stats.values, label='Messages per day (week)')
    axs[0].set_title('Messages per day (last week)')
    axs[0].set_xlabel('Date')
    axs[0].set_ylabel('Messages')

    axs[1].plot(month_stats.index, month_stats.values, label='Messages per day (month)', color='orange')
    axs[1].set_title('Messages per day (last month)')
    axs[1].set_xlabel('Date')
    axs[1].set_ylabel('Messages')

    axs[2].plot(all_time_stats.index, all_time_stats.values, label='Messages per day (all time)', color='green')
    axs[2].set_title('Messages per day (all time)')
    axs[2].set_xlabel('Date')
    axs[2].set_ylabel('Messages')

    plt.tight_layout()
    fig.savefig('/tmp/message_stats.png')

def plot_user_growth(users):
    now = datetime.now()
    week_ago = now - timedelta(weeks=1)
    month_ago = now - timedelta(days=30)

    users_with_joined_at = [user for user in users if "joined_at" in user]

    week_users = [user for user in users_with_joined_at if user['joined_at'] > week_ago]
    month_users = [user for user in users_with_joined_at if user['joined_at'] > month_ago]

    def group_by_day(data):
        df = pd.DataFrame(data)
        df['joined_at'] = pd.to_datetime(df['joined_at'])
        df.set_index('joined_at', inplace=True)
        return df.resample('D').size().cumsum()

    week_growth = group_by_day(week_users)
    month_growth = group_by_day(month_users)
    all_time_growth = group_by_day(users_with_joined_at)

    fig, axs = plt.subplots(3, 1, figsize=(10, 15))

    axs[0].plot(week_growth.index, week_growth.values, label='Cumulative User Growth (Week)')
    axs[0].set_title('Cumulative User Growth (last week)')
    axs[0].set_xlabel('Date')
    axs[0].set_ylabel('Total Users')

    axs[1].plot(month_growth.index, month_growth.values, label='Cumulative User Growth (Month)', color='orange')
    axs[1].set_title('Cumulative User Growth (last month)')
    axs[1].set_xlabel('Date')
    axs[1].set_ylabel('Total Users')

    axs[2].plot(all_time_growth.index, all_time_growth.values, label='Cumulative User Growth (All Time)', color='green')
    axs[2].set_title('Cumulative User Growth (all time)')
    axs[2].set_xlabel('Date')
    axs[2].set_ylabel('Total Users')

    plt.tight_layout()
    fig.savefig('/tmp/user_growth.png')



def generate_statistics(uri):
    db = connect_to_mongo(uri)
    messages = fetch_messages(db)
    users = fetch_users(db)

    plot_message_stats(messages)
    plot_user_growth(users)
