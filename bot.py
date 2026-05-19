import asyncio
import html
import logging
import re
import time

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from config import load_config
from memory import MemoryStorage
from modes import UserModes
from prompts import (
    SYSTEM_PROMPT,
    GENIUS_MODE_PROMPT,
    CREATIVE_MODE_PROMPT,
    TEACHER_MODE_PROMPT,
    SHORT_MODE_PROMPT,
)
from services.llm_service import LLMService


logging.basicConfig(level=logging.INFO)

config = load_config()
bot = Bot(token=config.bot_token)
dp = Dispatcher()

memory = MemoryStorage(max_messages=config.max_history_messages)
modes = UserModes()

llm_service = LLMService(
    base_url=config.base_url,
    model_name=config.model_name,
)


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎭 Create Persona"), KeyboardButton(text="📚 Examples")],
            [KeyboardButton(text="⚡ Genius Mode"), KeyboardButton(text="🧩 Creative Mode")],
            [KeyboardButton(text="🎓 Teacher Mode"), KeyboardButton(text="✂️ Short Mode")],
            [KeyboardButton(text="💬 Memory"), KeyboardButton(text="ℹ️ About")],
            [KeyboardButton(text="🧹 Reset AI")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Напиши сообщение или выбери режим...",
    )


def format_ai_answer(text: str) -> str:
    text = html.escape(text)

    text = re.sub(
        r"```(.*?)```",
        lambda m: f"<pre><code>{m.group(1).strip()}</code></pre>",
        text,
        flags=re.DOTALL,
    )

    text = re.sub(
        r"\\\[(.*?)\\\]",
        lambda m: f"<pre>{m.group(1).strip()}</pre>",
        text,
        flags=re.DOTALL,
    )

    text = re.sub(
        r"\\\((.*?)\\\)",
        lambda m: f"<code>{m.group(1).strip()}</code>",
        text,
        flags=re.DOTALL,
    )

    return text


def start_text():
    return (
        "🧠 <b>OmniMind activated</b>\n\n"
        "Ман <b>локальный AI ассистент</b> ҳастам, ки тавассути "
        "<b>LM Studio / Ollama</b> кор мекунам.\n\n"
        "✨ <b>Асосӣ:</b>\n"
        "ту худат муайян мекунӣ, ки AI кӣ бошад ва чӣ хел ҷавоб диҳад.\n\n"
        "AI метавонад шавад:\n"
        "🎓 муаллим\n"
        "💻 программист\n"
        "🧬 биолог\n"
        "📚 таърихшинос\n"
        "🎨 дизайнер\n"
        "🧠 консультант\n"
        "✍️ муҳаррири матн\n\n"
        "🎭 Барои танзими характер ва нақши бот — <b>Create Persona</b>-ро пахш кун."
    )


def about_text():
    return (
        "ℹ️ <b>OmniMind — Dynamic Local AI System</b>\n\n"
        "Ин Telegram-боти оддӣ нест.\n"
        "Ин интерфейс ба <b>локальная LLM</b> бо dynamic persona мебошад.\n\n"
        "<pre>"
        "Telegram User\n"
        "   ↓\n"
        "Aiogram Async Bot\n"
        "   ↓\n"
        "Reply Keyboard UI\n"
        "   ↓\n"
        "Persona Engine\n"
        "   ↓\n"
        "Memory Layer\n"
        "   ↓\n"
        "Prompt Orchestrator\n"
        "   ↓\n"
        "OpenAI-compatible API\n"
        "   ↓\n"
        "LM Studio Local Server\n"
        "   ↓\n"
        "Local LLM Model"
        "</pre>\n\n"
        "⚙️ <b>Stack:</b>\n"
        "• Python 3.11\n"
        "• aiogram 3.x\n"
        "• OpenAI SDK\n"
        "• LM Studio / Ollama\n"
        "• In-memory context\n"
        "• Dynamic persona system"
    )


@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        start_text(),
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@dp.message(Command("persona"))
async def persona_command(message: Message):
    if message.from_user is None:
        return

    modes.start_persona_setup(message.from_user.id)

    await message.answer(
        "🎭 <b>Create Custom Persona</b>\n\n"
        "Опиши, каким должен быть AI.\n\n"
        "Пример:\n"
        "<code>Ты строгий преподаватель биологии. "
        "Объясняй простым языком, пошагово, с примерами.</code>",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@dp.message(Command("clear"))
async def clear_command(message: Message):
    if message.from_user is None:
        return

    memory.clear_history(message.from_user.id)

    await message.answer(
        "🧹 <b>Memory cleared</b>",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


async def handle_menu_command(message: Message, user_id: int, user_text: str) -> bool:
    if user_text == "🎭 Create Persona":
        modes.start_persona_setup(user_id)
        await message.answer(
            "🎭 <b>Create Custom Persona</b>\n\n"
            "Напиши, каким должен быть AI:\n\n"
            "• роль\n"
            "• характер\n"
            "• стиль ответа\n"
            "• уровень сложности\n"
            "• формат ответа\n\n"
            "Пример:\n"
            "<code>Ты преподаватель математики. Объясняй просто, пошагово, с примерами.</code>",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return True

    if user_text == "📚 Examples":
        await message.answer(
            "📚 <b>Persona Examples</b>\n\n"
            "<code>Ты учитель биологии. Объясняй просто и с примерами.</code>\n\n"
            "<code>Ты Senior Python Developer. Отвечай коротко, строго, с кодом.</code>\n\n"
            "<code>Ты дизайнер брендов. Предлагай креативные идеи.</code>\n\n"
            "<code>Ты историк. Рассказывай интересно и по фактам.</code>\n\n"
            "<code>Ты мой личный наставник. Объясняй спокойно и мотивирующе.</code>",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return True

    if user_text == "⚡ Genius Mode":
        modes.set_mode(user_id, "genius")
        await message.answer(
            "⚡ <b>Genius Mode activated</b>\n\n"
            "Ҷавобҳо амиқтар, таҳлилӣ ва қавитар мешаванд.",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return True

    if user_text == "🧩 Creative Mode":
        modes.set_mode(user_id, "creative")
        await message.answer(
            "🧩 <b>Creative Mode activated</b>\n\n"
            "Ҷавобҳо креативӣ ва ғайристандартӣ мешаванд.",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return True

    if user_text == "🎓 Teacher Mode":
        modes.set_mode(user_id, "teacher")
        await message.answer(
            "🎓 <b>Teacher Mode activated</b>\n\n"
            "AI мисли муаллим қадам ба қадам мефаҳмонад.",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return True

    if user_text == "✂️ Short Mode":
        modes.set_mode(user_id, "short")
        await message.answer(
            "✂️ <b>Short Mode activated</b>\n\n"
            "Ҷавобҳо кӯтоҳ ва бе об мешаванд.",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return True

    if user_text == "💬 Memory":
        persona = modes.get_persona(user_id)
        await message.answer(
            "💬 <b>Memory Status</b>\n\n"
            f"🎛 <b>Mode:</b> {modes.get_mode(user_id)}\n"
            f"💬 <b>Messages:</b> {len(memory.get_history(user_id))}/{config.max_history_messages}\n"
            f"🧠 <b>Model:</b> {config.model_name}\n"
            f"🎭 <b>Persona:</b> {'enabled' if persona else 'not set'}",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return True

    if user_text == "ℹ️ About":
        await message.answer(
            about_text(),
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return True

    if user_text == "🧹 Reset AI":
        memory.clear_history(user_id)
        modes.clear_persona(user_id)
        modes.set_mode(user_id, "normal")
        await message.answer(
            "♻️ <b>AI reset completed</b>\n\n"
            "• память очищена\n"
            "• persona удалена\n"
            "• режим сброшен",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return True

    return False


@dp.message(F.text)
async def chat_handler(message: Message):
    if message.from_user is None or message.text is None:
        return

    user_id = message.from_user.id
    user_text = message.text.strip()

    if not user_text:
        await message.answer("Напиши сообщение.", reply_markup=main_menu())
        return

    if await handle_menu_command(message, user_id, user_text):
        return

    if modes.is_waiting_persona(user_id):
        modes.set_persona(user_id, user_text)

        await message.answer(
            "✅ <b>Persona saved</b>\n\n"
            "Теперь AI будет отвечать с учётом твоих требований.\n\n"
            "Можешь начать диалог.",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return

    await bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING,
    )

    memory.add_message(
        user_id=user_id,
        role="user",
        content=user_text,
    )

    current_mode = modes.get_mode(user_id)
    extra_prompt = ""

    if current_mode == "genius":
        extra_prompt = GENIUS_MODE_PROMPT
    elif current_mode == "creative":
        extra_prompt = CREATIVE_MODE_PROMPT
    elif current_mode == "teacher":
        extra_prompt = TEACHER_MODE_PROMPT
    elif current_mode == "short":
        extra_prompt = SHORT_MODE_PROMPT
    elif current_mode == "custom":
        extra_prompt = f"""
User-defined persona:
{modes.get_persona(user_id)}

Follow this persona carefully.
"""

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n\n" + extra_prompt,
        },
        *memory.get_history(user_id),
    ]

    start_time = time.time()
    answer = await llm_service.generate_response(messages)
    elapsed = round(time.time() - start_time, 2)

    memory.add_message(
        user_id=user_id,
        role="assistant",
        content=answer,
    )

    safe_answer = format_ai_answer(answer)

    final_answer = (
        f"{safe_answer}\n\n"
        f"━━━━━━━━━━━━━━\n"
        f"⚡ <b>Response time:</b> {elapsed}s\n"
        f"🧠 <b>Model:</b> {html.escape(config.model_name)}\n"
        f"🎛 <b>Mode:</b> {html.escape(current_mode)}"
    )

    await message.answer(
        final_answer,
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


async def main():
    logging.info("Starting OmniMind bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())