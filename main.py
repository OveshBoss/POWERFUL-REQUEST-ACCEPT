from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This helper converts ascii letters to small-caps-like Unicode.
SMALL_CAPS_MAP = {
    'a': 'ᴀ','b': 'ʙ','c': 'ᴄ','d': 'ᴅ','e': 'ᴇ','f': 'ꜰ','g': 'ɢ','h': 'ʜ','i': 'ɪ','j': 'ᴊ',
    'k': 'ᴋ','l': 'ʟ','m': 'ᴍ','n': 'ɴ','o': 'ᴏ','p': 'ᴘ','q': 'ǫ','r': 'ʀ','s': 's','t': 'ᴛ',
    'u': 'ᴜ','v': 'ᴠ','w': 'ᴡ','x': 'x','y': 'ʏ','z': 'ᴢ',
    'A': 'ᴀ','B': 'ʙ','C': 'ᴄ','D': 'ᴅ','E': 'ᴇ','F': 'ꜰ','G': 'ɢ','H': 'ʜ','I': 'ɪ','J': 'ᴊ',
    'K': 'ᴋ','L': 'ʟ','M': 'ᴍ','N': 'ɴ','O': 'ᴏ','P': 'ᴘ','Q': 'ǫ','R': 'ʀ','S': 's','T': 'ᴛ',
    'U': 'ᴜ','V': 'ᴠ','W': 'ᴡ','X': 'x','Y': 'ʏ','Z': 'ᴢ',
}

def to_small_caps(text: str) -> str:
    """Convert ASCII letters into small-caps-like Unicode characters where possible.
    Characters without a mapping are left unchanged.
    """
    return ''.join(SMALL_CAPS_MAP.get(ch, ch) for ch in text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Respond to /start with a small-caps welcome and buttons."""
    bot = context.bot
    me = await bot.get_me()
    start_text = to_small_caps(
        "WELCOME! — YOUR FRIENDLY AUTO-ACCEPT BOT IS ONLINE.

"
        "I'LL AUTOMATICALLY ACCEPT JOIN REQUESTS FOR GROUPS WHERE I'M AN ADMIN."
    )

    keyboard = [
        [
            InlineKeyboardButton(to_small_caps("ADD ME TO YOUR GROUP"), url=f"https://t.me/{me.username}?startgroup=true"),
        ],
        [
            InlineKeyboardButton(to_small_caps("ADD ME TO YOUR CHANNEL"), url=f"https://t.me/{me.username}?startchannel=true"),
            InlineKeyboardButton(to_small_caps("MOVIE GROUP"), callback_data="movie_group"),
        ],
        [InlineKeyboardButton(to_small_caps("HELP"), callback_data="help")],
    ]

    await update.effective_chat.send_message(text=start_text, reply_markup=InlineKeyboardMarkup(keyboard))


async def help_button_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "help":
        help_text = to_small_caps(
            "COMMANDS:
"
            "/start - STARTUP MESSAGE AND BUTTONS
"
            "THIS BOT AUTO-APPROVES JOIN REQUESTS WHEN IT HAS THE PROPER ADMIN RIGHTS.
"
            "IF YOU NEED TO CHANGE TEXTS, EDIT THE ENVIRONMENT OR MODIFY main.py."
        )
        await query.message.reply_text(help_text)
    elif data == "movie_group":
        movie_text = to_small_caps(
            "TO INVITE ME TO YOUR MOVIE GROUP, USE THE 'ADD ME TO YOUR GROUP' BUTTON ABOVE."
        )
        await query.message.reply_text(movie_text)


async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-approve incoming chat join requests and send a friendly personal message.

    NOTE: Bot must be an administrator in the target chat with the proper privileges.
    """
    req = update.chat_join_request
    if not req:
        return

    chat = req.chat
    user = req.from_user
    bot = context.bot

    logger.info("Received join request from %s to chat %s", user.id, chat.id)

    try:
        # Approve the join request
        await bot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        logger.info("Approved join request of user %s for chat %s", user.id, chat.id)

        # Personal message to the user
        personal = to_small_caps(
            "YOUR REQUEST HAS BEEN ACCEPTED — WELCOME!
"
            "IF YOU NEED HELP, PRESS THE HELP BUTTON IN THE GROUP OR MESSAGE THE ADMINS."
        )
        try:
            await bot.send_message(chat_id=user.id, text=personal)
        except Exception as e:
            # User may have privacy settings preventing PMs; just log it
            logger.warning("Could not send PM to user %s: %s", user.id, e)

        # Group welcome message with buttons
        me = await bot.get_me()
        welcome_text = to_small_caps(
            f"WELCOME {user.full_name}! — YOUR REQUEST WAS ACCEPTED.
"
            "ENJOY THE GROUP AND READ THE RULES."
        )

        keyboard = [
            [InlineKeyboardButton(to_small_caps("ADD ME TO YOUR GROUP"), url=f"https://t.me/{me.username}?startgroup=true")],
            [InlineKeyboardButton(to_small_caps("ADD ME TO YOUR CHANNEL"), url=f"https://t.me/{me.username}?startchannel=true")],
            [InlineKeyboardButton(to_small_caps("MOVIE GROUP"), callback_data="movie_group")],
            [InlineKeyboardButton(to_small_caps("HELP"), callback_data="help")],
        ]

        await bot.send_message(chat_id=chat.id, text=welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as err:
        logger.exception("Failed to handle join request: %s", err)


async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is required")

    app = ApplicationBuilder().token(token).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))

    # Callback buttons
    app.add_handler(CallbackQueryHandler(help_button_cb))

    # Chat join request handler (auto-approve)
    app.add_handler(ChatJoinRequestHandler(handle_join_request))

    # Run the bot (long polling)
    logger.info("Bot starting (polling)...")
    await app.run_polling()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

---
