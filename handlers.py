from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.exceptions import TelegramAPIError
from aiogram.types import (Message, Chat)

from filter_media import SupportedMediaFilter
from settings import settings

GROUP_ID = settings.GROUP_ID
GROUP_TYPE = settings.GROUP_TYPE

router = Router()


def extract_user_id(message: Message) -> int:
    if message.text:
        text = message.text
    else:
        text = message.caption
    user_id = int(text.split(sep='#id')[-1])
    return user_id


@router.message(Command(commands=["start"]))
async def command_start(message: Message) -> None:
    await message.answer(
        "Привет! Это служба поддержки «А-Склад». Если у вас есть вопрос, "
        "напишите нам, мы с радостью на него ответим.\n"
        "Мы работаем по будням с 9:00 до 18:00, но можем ответить и в другое "
        "время, если не будем заняты:)",
    )


@router.message(F.chat.type == 'private', F.text)
async def send_message_to_group(message: Message, bot: Bot):
    if len(message.text) > 4000:
        return await message.reply(text='Сообщение не должно быть длиннее 4000 символов')
    await bot.send_message(
        chat_id=GROUP_ID,
        text=(
            f'{message.text}\n\n'
            f"Username: @{message.from_user.username}\n"
            f'id{message.from_user.id}\n'
            f'#id{message.from_user.id}'
                    ),
        parse_mode='HTML'
    )


@router.message(Command(commands="info"),
                F.chat.type == GROUP_TYPE,
                F.reply_to_message)
async def get_user_info(message: Message, bot: Bot):
    def get_name(chat: Chat):
        if not chat.first_name:
            return ""
        if not chat.last_name:
            return chat.first_name
        return f"{chat.first_name} {chat.last_name}"

    try:
        user_id = extract_user_id(message.reply_to_message)
    except ValueError as err:
        return await message.reply(str(err))

    try:
        user = await bot.get_chat(user_id)
    except TelegramAPIError as err:
        await message.reply(
            text=(f'Невозможно найти пользователя с таки Id. Текст ошибки:\n'
                  f'{err.message}')
        )
        return

    username = f"@{user.username}" if user.username else "отсутствует"
    await message.reply(text=f'Имя: {get_name(user)}\n'
                             f'Id: {user.id}\n'
                             f'username: {username}')


@router.message(F.chat.type == GROUP_TYPE, F.reply_to_message)
async def send_message_answer(message: Message):
    try:
        chat_id = extract_user_id(message.reply_to_message)
        await message.copy_to(chat_id)
    except ValueError as err:
        await message.reply(text=f'Не могу извлечь Id.  Возможно он '
                                 f'некорректный. Текст ошибки:\n'
                                 f'{str(err)}')


@router.message(SupportedMediaFilter(), F.chat.type == 'private')
async def supported_media(message: Message):
    if message.caption and len(message.caption) > 1000:
        return await message.reply(text='Слишком длинное описание. Описание '
                                        'не может быть больше 1000 символов')
    else:
        await message.copy_to(
            chat_id=GROUP_ID,
            caption=((f"{message.caption}\n\n" or "") + f"""
Username: @{message.from_user.username}
id{message.from_user.id}
#id{message.from_user.id}
"""),
            parse_mode="HTML"
        )
