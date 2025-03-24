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
            await first_message.reply("❌ Batch process cancelled.", quote=True)
            return
        
        f_msg_id = await get_message_id(client, first_message)
        
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote=True)
            continue

    while True:
        try:
            second_message = await client.ask(
                text="Forward the Last Message from DB Channel ⏩ (with Quotes)..\nor Send the DB Channel Post link\nUse /sbatch for stopping.",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception as e:
            print(e)
            return
        
        if second_message.text == "/sbatch":
            await second_message.reply("❌ Batch process cancelled.", quote=True)
            return
        
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote=True)
            continue
        
    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(
        f"<b>🧑‍💻 Here is your code : \n<code>{base64_string}</code></b>\n\n"
        f"<b>🔗 Here is your link :</b>\n{link}",
        quote=True,
        reply_markup=reply_markup
    )

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(
                text="Forward Message from the DB Channel ⏩ (with Quotes)..\nor Send the DB Channel Post link\nType /sgen for stopping.",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception as e:
            print(e)
            return
        
        if channel_message.text == "/sgen":
            await channel_message.reply("❌ Link generation cancelled.", quote=True)
            return
        
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote=True)
            continue
    
    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(
        f"<b>🧑‍💻 Here is your code : \n<code>{base64_string}</code></b>\n\n"
        f"<b>🔗 Here is your link : </b>\n{link}",
        quote=True,
        reply_markup=reply_markup
    )

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('flink'))
async def formatted_link_generator(client: Client, message: Message):
    # Step 1: Get format settings
    while True:
        try:
            format_message = await client.ask(
                text="📌 Send the link format in this style:\n\n`480p = 2, 720p = 2, 1080p = 2`\n\n"
                     "Each value represents the number of messages for that quality.\n"
                     "Type /sflink to cancel.",
                chat_id=message.from_user.id,
                filters=filters.text,
                timeout=60
            )
        except Exception as e:
            print(e)
            return
        
        if format_message.text == "/sflink":
            await format_message.reply("❌ Formatted link generation cancelled.", quote=True)
            return
        
        # Parse the format
        pattern = r"(\d{3,4}p) = (\d+)"
        matches = re.findall(pattern, format_message.text)
        
        if matches:
            format_data = {quality: int(count) for quality, count in matches}
            break
        else:
            await format_message.reply("❌ Invalid format! Use: `480p = 2, 720p = 2, 1080p = 2`", quote=True)
            continue
    
    # Step 2: Get DB channel message
    while True:
        try:
            channel_message = await client.ask(
                text="Forward Message from the DB Channel ⏩ (with Quotes)..\n"
                     "or Send the DB Channel Post link\n"
                     "Type /sflink to cancel.",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception as e:
            print(e)
            return
        
        if channel_message.text == "/sflink":
            await channel_message.reply("❌ Formatted link generation cancelled.", quote=True)
            return
        
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote=True)
            continue
    
    # Generate links
    base_msg_id = msg_id * abs(client.db_channel.id)
    generated_links = []
    buttons = []
    
    for quality, count in format_data.items():
        string = f"get-{base_msg_id}-{count}-{quality}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"
        generated_links.append(f"<b>{quality}</b> - {link}")
        buttons.append([InlineKeyboardButton(quality, url=link)])
    
    # Add share button
    buttons.append([InlineKeyboardButton("🔁 Share All", url=f'https://telegram.me/share/url?url={"\\n".join(generated_links)}')])
    
    reply_text = (
        f"<b>🔗 Formatted Links:</b>\n\n"
        f"{'</b>\n\n<b>'.join(generated_links)}\n\n"
        f"<b>📁 Total Qualities:</b> {len(format_data)}"
    )
    
    await channel_message.reply_text(
        reply_text,
        quote=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
