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
            channel_message = await client.ask(
                text="Forward Message from DB Channel (with Quotes) or Send Post Link\nType /cancel to stop",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception:
            return
            
        if channel_message.text == "/cancel":
            return
        
        # Extract channel info
        channel_link = None
        channel_id = None
        post_id = None
        
        # If message contains a link
        if not channel_message.forward_from_chat and channel_message.text:
            match = re.search(r't\.me/(?:c/)?([a-zA-Z0-9_]+)/(\d+)', channel_message.text)
            if match:
                channel_id = match.group(1)
                post_id = match.group(2)
                channel_link = f"https://t.me/c/{channel_id}/{post_id}"
        
        # Get message ID from forwarded message or link
        msg_id = await get_message_id(client, channel_message)
        
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error: Not from DB Channel or invalid link", quote=True)
            continue
    
    # Create the encoded string with channel info if available
    string = f"get-{msg_id * abs(client.db_channel.id)}"
    if channel_id and post_id:
        string += f"-chnl_{channel_id}_{post_id}"
    
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    # Prepare response with buttons
    reply_text = f"""<b>Generated Link:</b>
{link}

<b>Original Channel:</b> {channel_link if channel_link else "Not specified"}

<i>Share this link with others!</i>"""
    
    buttons = [
        [InlineKeyboardButton("🔗 Share Link", url=f'https://telegram.me/share/url?url={link}')]
    ]
    
    # Add Join button if channel link available
    if channel_link:
        buttons.append([InlineKeyboardButton("📢 Join Channel", url=channel_link)])
    
    await channel_message.reply_text(
        reply_text,
        quote=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
