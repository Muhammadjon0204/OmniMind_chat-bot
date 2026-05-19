import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ЗАМЕНИ ТОКЕН: После того как аннулируешь старый в @BotFather
TOKEN = "8715806698:AAHLZqpK-ip9Tj26biuKfo6Lv1gd5e7HQqc"

ai_client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

# УЖЕСТОЧЕННЫЙ ПРОМПТ:
# Мы добавляем четкий запрет на темы, не связанные с кулинарией.
SYSTEM_PROMPT = """Ты — строгий, но дружелюбный профессиональный шеф-повар.
Твоя область знаний — ТОЛЬКО кулинария, рецепты, продукты и кухонная техника.

ПРАВИЛО: Если пользователь задает вопрос НЕ на кулинарную тему (программирование, политика, математика, ремонт и т.д.), 
ты должен вежливо, но твердо отказаться отвечать. 
Скажи, что ты мастер половника и ножа, а в других делах не разбираешься.
Используй кулинарные метафоры и эмодзи. 👨‍🍳🔥"""

chat_histories = {}

def get_main_menu():
    buttons = [
        ["🍎 Рецепт из того, что есть", "🍰 Идея для выпечки"],
        ["🍲 Как варить борщ?", "⏱️ Быстрый ужин"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def ask_ai(user_id, user_message):
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    
    chat_histories[user_id].append({"role": "user", "content": user_message})
    
    # Ограничение истории, чтобы модель не забывала системную роль
    if len(chat_histories[user_id]) > 6:
        chat_histories[user_id] = chat_histories[user_id][-6:]
    
    try:
        response = ai_client.chat.completions.create(
            model="qwen2.5-3b-instruct", # Укажи ID модели из LM Studio, если нужно
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *chat_histories[user_id]
            ],
            temperature=0.5, # Чуть снизили температуру для большей серьезности
            max_tokens=150
        )
        ai_answer = response.choices[0].message.content
        chat_histories[user_id].append({"role": "assistant", "content": ai_answer})
        return ai_answer
    except Exception as e:
        print(f"Ошибка AI: {e}")
        return "👨‍🍳 Ой! У меня соус убежал на сервер. Попробуй написать чуть позже, когда я приберусь на кухне!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍🍳 Привет! Я твой персональный Шеф-повар.\n\n"
        "Я мастер ножа и половника. Спрашивай меня о рецептах, соусах или о том, как спасти пересоленный суп!\n"
        "На другие темы я не общаюсь — на кухне слишком много работы. 😉",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    ai_response = ask_ai(user_id, user_text)
    
    await update.message.reply_text(ai_response, reply_markup=get_main_menu())

if name == "main":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Шеф-повар на посту и следит за порядком!")
    app.run_polling()