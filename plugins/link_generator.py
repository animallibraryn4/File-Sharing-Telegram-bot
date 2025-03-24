from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id
import re

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            user_msg = await client.ask(
                text="🔗 Send me ANY link (channel/post/URL)\nType /cancel to stop",
                chat_id=message.from_user.id,
                filters=filters.text,
                timeout=60
            )
            if user_msg.text == "/cancel":
                return

            # Store the original link exactly as sent by user
            original_link = user_msg.text.strip()
            
            # Always generate link (no DB channel checks)
            string = f"redirect-{original_link}"
            base64_string = await encode(string)  # Ensure your encode() handles URLs
            bot_link = f"https://t.me/{client.username}?start={base64_string}"

            # Response to admin
            await user_msg.reply_text(
                f"**Generated Link:**\n{bot_link}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Share", url=f'https://t.me/share/url?url={bot_link}')]
                ]),
                quote=True
            )
            break

        except Exception as e:
            print(e)
            await message.reply("❌ Error, try again")
            break
