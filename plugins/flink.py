from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import re
from bot import Bot  # Ensure this matches your bot instance
from config import ADMINS  # Ensure this is a list

flink_formats = {}

@Bot.on_message(filters.command("flink") & filters.user(ADMINS))
async def flink_command(client, message: Message):
    chat_id = message.chat.id
    flink_formats[chat_id] = {}  # Reset format for new request
    
    buttons = [
        [InlineKeyboardButton("🔗 Set Format", callback_data="set_format")],
        [InlineKeyboardButton("⚡ Start Process", callback_data="start_process")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    await message.reply_text(
        "**🔗 FORMATTED LINK:**\n\n"
        "📌 **Current Format:** Not Set\n"
        "➖➖➖➖➖➖➖➖➖",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Bot.on_callback_query(filters.regex("set_format"))
async def set_format_callback(client, query):
    await query.message.edit_text(
        "📌 Send the link format in this style:\n\n"
        "`480p = 2, 720p = 2, 1080p = 2`\n\n"
        "Each value represents the number of messages for that quality."
    )

@Bot.on_message(filters.text & filters.user(ADMINS))
async def save_format(client, message: Message):
    chat_id = message.chat.id
    if chat_id in flink_formats:
        format_text = message.text
        pattern = r"(\d{3,4}p) = (\d+)"
        matches = re.findall(pattern, format_text)

        if matches:
            flink_formats[chat_id] = {quality: int(count) for quality, count in matches}
            await message.reply_text(f"✅ **Format Saved:**\n{format_text}")
        else:
            await message.reply_text("❌ Invalid format! Use: `480p = 2, 720p = 2, 1080p = 2`")

@Bot.on_callback_query(filters.regex("start_process"))
async def start_process(client, query):
    chat_id = query.message.chat.id
    if chat_id not in flink_formats or not flink_formats[chat_id]:
        await query.answer("⚠️ Set format first!", show_alert=True)
        return

    await query.message.edit_text(
        "📌 Send the post link from the database channel."
    )

@Bot.on_message(filters.text & filters.regex(r"https://t\.me/c/\d+/\d+") & filters.user(ADMINS))
async def generate_formatted_links(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in flink_formats or not flink_formats[chat_id]:
        await message.reply_text("⚠️ You need to set the format first using `Set Format` button.")
        return
    
    base_link = message.text
    format_data = flink_formats[chat_id]
    
    generated_links = []
    for quality, count in format_data.items():
        encoded_text = f"{quality} = {count}".encode("utf-8").hex()
        link = f"https://t.me/tgfilex2bot?start={encoded_text}"
        generated_links.append(f"**{quality}** - {link}")

    reply_text = "**🔗 BELOW IS THE FORMATTED LINK:**\n\n" + " | ".join(generated_links)

    buttons = [[InlineKeyboardButton(quality, url=link)] for quality, link in zip(format_data.keys(), generated_links)]
    
    await message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(buttons))
