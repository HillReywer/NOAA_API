import telegram
import requests
from telegram.ext import ConversationHandler

TOKEN = 'YOUR_BOT_TOKEN'
ENTER_PROMPT = range(1)

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Привет, я бот! Для начала введите команду '/расскажи'.")

def tell_story_start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Введите prompt для генерации истории:")
    return ENTER_PROMPT

def tell_story_end(update, context):
    response = requests.get('https://api.openai.com/v1/engines/davinci-codex/completions', 
                           headers={
                               'Content-Type': 'application/json',
                               'Authorization': 'Bearer YOUR_API_KEY'
                           },
                           json={
                               'prompt': context.user_data['prompt'],
                               'max_tokens': 50
                           })
    context.bot.send_message(chat_id=update.message.chat_id, text=response.json()['choices'][0]['text'])
    return ConversationHandler.END

def cancel(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Отменено.")
    return ConversationHandler.END

def main():
    updater = telegram.Updater(token=TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[telegram.CommandHandler('tell_story', tell_story_start)],
        states={
            ENTER_PROMPT: [telegram.MessageHandler(telegram.Filters.text & ~telegram.Filters.command, tell_story_end)]
        },
        fallbacks=[telegram.CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(telegram.CommandHandler('start', start))
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
