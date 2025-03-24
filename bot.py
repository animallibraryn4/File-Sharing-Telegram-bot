from aiohttp import web
from database.database import full_adminbase
from plugins import web_server
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import ADMINS, API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2, CHANNEL_ID, PORT, OWNER_ID

class Bot(Client):
    def __init__(self):
        super().__init__(
            name=":memory:",  # In-memory session
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
            in_memory=True  # Disable session persistence
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        
        # Force Sub Channel 1
        if FORCE_SUB_CHANNEL:
            try:
                self.invitelink = await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
            except Exception as a:
                self.LOGGER.warning(f"Force Sub Channel 1 Error: {a}")
                sys.exit(1)

        # Force Sub Channel 2
        if FORCE_SUB_CHANNEL2:
            try:
                self.invitelink2 = await self.export_chat_invite_link(FORCE_SUB_CHANNEL2)
            except Exception as a:
                self.LOGGER.warning(f"Force Sub Channel 2 Error: {a}")
                sys.exit(1)

        # Verify DB Channel
        try:
            self.db_channel = await self.get_chat(CHANNEL_ID)
            test = await self.send_message(chat_id=CHANNEL_ID, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER.error(f"DB Channel Error: {e}")
            sys.exit(1)

        # Load admins
        initadmin = await full_adminbase()
        ADMINS.extend(x for x in initadmin if x not in ADMINS)

        await self.send_message(chat_id=OWNER_ID, text="✅ Bot Started Successfully")
        self.set_parse_mode(ParseMode.HTML)
        self.username = usr_bot_me.username

        # Start web server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER.info("Bot stopped.")
