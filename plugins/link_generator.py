from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id
import re

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(
                text="Forward the First Message from DB Channel ⏩ (with Quotes)..\n\nor Send the DB Channel Post Link\nUse /sbatch for stopping.",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception as e:
            print(e)
            return
        if first_message.text == "/sbatch":
            return
            
        # Extract original link if provided
        original_link = None
        if not first_message.forward_from_chat and first_message.text:
            original_link = first_message.text.strip()
        
        f_msg_id = await get_message_id(client, first_message)
        
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote=True)
            continue

    while True:
        try:
            second_message = await client.ask(
                text="Forward the Last Message from DB Channel ⏩ (with Quotes)..\nor Send the DB Channel Post link\nUse /sbatch for stopping.",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return
        if second_message.text == "/sbatch":
            return
            
        # For second message, only update original_link if it wasn't set before
        if not original_link and not second_message.forward_from_chat and second_message.text:
            original_link = second_message.text.strip()
        
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote=True)
            continue
        
    # Create the encoded string with original link if available
    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    if original_link:
        string += f"-link_{original_link}"
    
    base64_string = await encode(string)
    bot_link = f"https://t.me/{client.username}?start={base64_string}"
    
    reply_text = f"""<b>🧑‍💻 Generated Code:</b>
<code>{base64_string}</code>

<b>🔗 Your Link:</b>
{bot_link}"""
    
    if original_link:
        reply_text += f"\n\n<b>📢 Original Link:</b>\n{original_link}"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={bot_link}')]
    ])
    
    await second_message.reply_text(reply_text, quote=True, reply_markup=reply_markup)

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(
                text="Forward Message from DB Channel ⏩ (with Quotes) or Send ANY Link\nType /cancel to stop",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception:
            return
        if channel_message.text == "/cancel":
            return
            
        # Store the original link exactly as sent by user
        original_link = None
        if not channel_message.forward_from_chat and channel_message.text:
            original_link = channel_message.text.strip()
        
        # Get message ID (only required for forwarded messages)
        msg_id = await get_message_id(client, channel_message)
        
        if msg_id or original_link:
            break
        else:
            await channel_message.reply("❌ Error\n\nFor forwarded messages: Not from DB Channel\nFor links: Invalid format", quote=True)
            continue
    
    # Create the encoded string
    if msg_id:
        string = f"get-{msg_id * abs(client.db_channel.id)}"
    else:
        string = f"redirect-{original_link}"
    
    if original_link and msg_id:
        string += f"-link_{original_link}"
    
    base64_string = await encode(string)
    bot_link = f"https://t.me/{client.username}?start={base64_string}"
    
    reply_text = f"""<b>🧑‍💻 Generated Code:</b>
<code>{base64_string}</code>

<b>🔗 Your Link:</b>
{bot_link}"""
    
    if original_link:
        reply_text += f"\n\n<b>📢 Original Link:</b>\n{original_link}"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={bot_link}')]
    ])
    
    await channel_message.reply_text(reply_text, quote=True, reply_markup=reply_markup)
