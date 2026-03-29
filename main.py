import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from config import Config

app = Client("HostingBot", 
             api_id=Config.API_ID, 
             api_hash=Config.API_HASH, 
             bot_token=Config.BOT_TOKEN)

# User session store karne ke liye
user_state = {}

# --- Step 1: Subscribe Check ---
async def check_sub(client, user_id):
    for channel in Config.CHANNELS:
        try:
            await client.get_chat_member(channel, user_id)
        except UserNotParticipant:
            return False
    return True

@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    if not await check_sub(client, user_id):
        buttons = [
            [InlineKeyboardButton("Main Channel", url=f"https://t.me/{Config.CHANNELS[0]}")],
            [InlineKeyboardButton("Secondary Channel", url=f"https://t.me/{Config.CHANNELS[1]}")],
            [InlineKeyboardButton("Joined ✅", callback_data="verify")]
        ]
        await message.reply("❌ Pehle dono channels join karein!", reply_markup=InlineKeyboardMarkup(buttons))
        return
    
    await message.reply("✅ Step 2: Apni bot files (.py ya .zip) yahan upload karein.")
    user_state[user_id] = "waiting_for_file"

# --- Step 2: File Upload ---
@app.on_message(filters.document | filters.video_document)
async def handle_file(client, message):
    user_id = message.from_user.id
    if user_state.get(user_id) == "waiting_for_file":
        await message.download(file_name=f"downloads/{user_id}/")
        await message.reply("📁 File received! \n\n**Step 3:** Ab apna Bot Token enter karein.")
        user_state[user_id] = "waiting_for_token"

# --- Step 3: Token Entry ---
@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def handle_text(client, message):
    user_id = message.from_user.id
    if user_state.get(user_id) == "waiting_for_token":
        token = message.text
        user_state[user_id] = {"token": token, "status": "ready"}
        
        run_btn = [[InlineKeyboardButton("🚀 Run Bot 24x7", callback_data="run_now")]]
        await message.reply("✅ Token Saved! \n\n**Step 4:** Neeche click karke lifetime free host karein.", 
                            reply_markup=InlineKeyboardMarkup(run_btn))

# --- Step 4: Run Bot ---
@app.on_callback_query(filters.regex("run_now"))
async def run_bot_logic(client, callback):
    await callback.message.edit("⚙️ Processing... Aapka bot 24x7 lifetime ke liye host ho gaya hai! \n\nAgar band ho jaye toh `/restart` likhein.")

@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await message.reply(f"Contact Admin: {Config.ADMIN_ID}")

print("Bot is running...")
app.run()
