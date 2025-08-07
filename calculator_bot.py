import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
# Get the token from environment variables for security
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# Enable logging to see errors and bot activity
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# --- Bot Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user_name = update.message.from_user.first_name
    welcome_message = (
        f"👋 Hello, {user_name}!\n\n"
        "I am your friendly calculator bot. Just send me a simple math expression "
        "and I'll solve it for you.\n\n"
        "For example: `10 * 5` or `100 / 2.5`\n\n"
        "I can handle addition (+), subtraction (-), multiplication (*), and division (/)."
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a help message when the /help command is issued."""
    help_text = (
        "Need help? Here's how to use me:\n\n"
        "1. Send a mathematical expression like `50 + 50`.\n"
        "2. I will calculate the result and send it back to you.\n\n"
        "Supported operations:\n"
        "`+` : Addition\n"
        "`-` : Subtraction\n"
        "`*` : Multiplication\n"
        "`/` : Division"
    )
    await update.message.reply_text(help_text)


# --- Main Logic ---

def calculate_expression(expression: str) -> str:
    """Safely evaluates a simple mathematical expression."""
    try:
        # A list of allowed characters for security.
        # This prevents users from running malicious code.
        allowed_chars = "0123456789.+-*/() "
        if not all(char in allowed_chars for char in expression):
            return "Error: Invalid characters in expression."

        # Using eval() can be risky, but we've limited the allowed characters
        # to make it safer for this simple use case.
        result = eval(expression)
        return str(result)
    except ZeroDivisionError:
        return "Error: Cannot divide by zero. That's not possible! 🧐"
    except Exception as e:
        logger.error(f"Error evaluating expression '{expression}': {e}")
        return "Error: I couldn't understand or calculate that. Please check your expression."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles regular messages and performs calculations."""
    user_message = update.message.text
    logger.info(f"Received message from {update.message.from_user.first_name}: {user_message}")

    # Calculate the result
    result = calculate_expression(user_message)

    # Send the result back to the user
    await update.message.reply_text(f"The result is: {result}")


# --- Main Bot Function ---

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    # Disable job queue to avoid timezone issues
    from telegram.ext import ApplicationBuilder
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).job_queue(None).build()
    logger.info("Bot application created.")

    # Register the command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Register the message handler for calculations
    # This will respond to any text message that is NOT a command
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    # The bot will keep running until you press Ctrl-C
    logger.info("Starting bot polling...")
    application.run_polling()
    logger.info("Bot has stopped.")


if __name__ == "__main__":
    main()