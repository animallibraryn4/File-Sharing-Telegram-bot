from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id
import base64

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(text = "Forward Message from the DB Channel ⏩ (with Quotes)\n\nor Send the DB Channel Post link\nType /sgen for stopping.", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except Exception:
            return
        
        if channel_message.text == "/sgen":
            return
        
        if channel_message.text.startswith("https://t.me/"):
            channel_link = channel_message.text.strip()
            encoded_link = base64.urlsafe_b64encode(channel_link.encode()).decode()
            generated_link = f"https://t.me/{client.username}?start=join_{encoded_link}"
            await channel_message.reply_text(f"<b>🔗 Here is your generated channel link:</b>\n{generated_link}")
            return
        
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote = True)
            continue
    
    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<b>🧑‍💻 Here is your code : \n<code>{base64_string}</code></b>\n\n<b>🔗 Here is your link : </b>\n{link}", quote=True, reply_markup=reply_markup)

@Bot.on_message(filters.regex(r'^/start join_(.*)'))
async def join_channel(client: Client, message: Message):
    encoded_link = message.matches[0].group(1)
    try:
        channel_link = base64.urlsafe_b64decode(encoded_link).decode()
        join_button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Join Channel", url=channel_link)]]
        )
        await message.reply("Here is your link! Click below to proceed:", reply_markup=join_button)
    except Exception as e:
        await message.reply("Invalid link or error occurred.")
        
