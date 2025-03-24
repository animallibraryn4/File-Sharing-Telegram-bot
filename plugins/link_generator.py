from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(text = "Forward the First Message from DB Channel ⏩ (with Quotes)..\n\nor Send the DB Channel Post Link\nUse /sbatch for stopping.", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except Exception as e:
            print(e)
            return
        if first_message.text == "/sbatch":
            return
        f_msg_id = await get_message_id(client, first_message)
        
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue
    while True:
        try:
            second_message = await client.ask(text = "Forward the Last Message from DB Channel ⏩ (with Quotes)..\nor Send the DB Channel Post link\nUse /sbatch for stopping.", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        if second_message.text == "/sbatch":
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue
        
    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<b>🧑‍💻 Here is your code : \n<code>{base64_string}</code></b>\n\n<b>🔗 Here is your link :</b>\n{link}", quote=True, reply_markup=reply_markup)

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    # Check if the command is a reply to a message
    if not message.reply_to_message:
        await message.reply_text("⚠️ Please reply to a file/message with /genlink command")
        return
    
    replied_message = message.reply_to_message
    msg_id = await get_message_id(client, replied_message)
    
    if not msg_id:
        await message.reply_text("❌ Error: Could not generate link for this message")
        return
    
    # Generate link and code
    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await message.reply_text(f"<b>🧑‍💻 Here is your code : \n<code>{base64_string}</code></b>\n\n<b>🔗 Here is your link : </b>\n{link}", quote=True, reply_markup=reply_markup)
