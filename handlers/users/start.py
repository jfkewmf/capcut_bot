from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import dp, bot
from database.database import db
from keyboards.reply.admin import cancel_markup, admin, cancel_skip_markup
from data.config import CHANNEL_ID, ADMINS
from aiogram.utils.markdown import hbold, hlink, hitalic
from datetime import datetime
from aiogram.dispatcher.filters import Text

class AddTemplate(StatesGroup):
    name = State()
    category = State()
    description = State()
    media = State()
    link = State()

async def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

async def send_template_to_channel(template_data: dict):
    try:
        caption = (
            f"{hbold('🎬 ' + template_data['name'])}\n\n"
            f"{hitalic(template_data.get('description', 'Tavsif kiritilmagan'))}\n"
            f"📂 Kategoriya: {template_data['category']}\n"
            f"🔗 {hlink('Shablon linki', template_data['link'])}\n\n"
            f"📆 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            f"👤 @{template_data.get('username', 'admin')}"
        )

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("📥 Yuklab olish", url=template_data['link']))

        if 'media_file_id' in template_data and template_data['media_file_id']:
            if template_data['media_type'] == 'photo':
                await bot.send_photo(CHANNEL_ID, template_data['media_file_id'], caption=caption, reply_markup=keyboard, parse_mode='HTML')
            elif template_data['media_type'] == 'video':
                await bot.send_video(CHANNEL_ID, template_data['media_file_id'], caption=caption, reply_markup=keyboard, parse_mode='HTML')
        else:
            await bot.send_message(CHANNEL_ID, caption, reply_markup=keyboard, parse_mode='HTML')
        return True
    except Exception as e:
        print(f"Kanalga yuborishda xato: {e}")
        return False

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    if await is_admin(message.from_user.id):
        await message.answer("Assalomu alaykum! Admin paneliga xush kelibsiz.", reply_markup=admin)
    else:
        await message.answer("Sizga ruxsat yo'q!")

@dp.message_handler(text="Shablon qo'shish ➕")
async def start_adding_template(message: types.Message):
    if await is_admin(message.from_user.id):
        await message.answer("Shablon nomini kiriting:", reply_markup=cancel_markup)
        await AddTemplate.name.set()
    else:
        await message.answer("Sizga ruxsat yo'q!")

@dp.message_handler(state=AddTemplate.name)
async def process_name(message: types.Message, state: FSMContext):
    if message.text == "Bekor qilish ❌":
        await state.finish()
        await message.answer("✅ Amal bekor qilindi", reply_markup=admin)
        return

    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer("Shablon kategoriyasini kiriting:", reply_markup=cancel_markup)
    await AddTemplate.next()

@dp.message_handler(state=AddTemplate.category)
async def process_category(message: types.Message, state: FSMContext):
    if message.text == "Bekor qilish ❌":
        await state.finish()
        await message.answer("✅ Amal bekor qilindi", reply_markup=admin)
        return

    async with state.proxy() as data:
        data['category'] = message.text
    await message.answer("Shablon haqida qisqacha tavsif (agar kerak bo'lsa):", reply_markup=cancel_skip_markup)
    await AddTemplate.next()

@dp.message_handler(state=AddTemplate.description)
async def process_description(message: types.Message, state: FSMContext):
    if message.text == "Bekor qilish ❌":
        await state.finish()
        await message.answer("✅ Amal bekor qilindi", reply_markup=admin)
        return

    async with state.proxy() as data:
        data['description'] = message.text if message.text != "O‘tkazib yuborish ⏭️" else "Tavsif kiritilmagan"
    await message.answer("Shablon uchun video yoki rasm yuboring (agar kerak bo'lsa):", reply_markup=cancel_skip_markup)
    await AddTemplate.next()

@dp.message_handler(content_types=['photo', 'video'], state=AddTemplate.media)
async def process_media(message: types.Message, state: FSMContext):
    if message.caption == "Bekor qilish ❌" or message.text == "Bekor qilish ❌":
        await state.finish()
        await message.answer("✅ Amal bekor qilindi", reply_markup=admin)
        return

    async with state.proxy() as data:
        if message.photo:
            data['media_file_id'] = message.photo[-1].file_id
            data['media_type'] = 'photo'
        elif message.video:
            data['media_file_id'] = message.video.file_id
            data['media_type'] = 'video'
    await message.answer("Endi shablon linkini yuboring:", reply_markup=cancel_markup)
    await AddTemplate.next()

@dp.message_handler(Text(equals="O‘tkazib yuborish ⏭️"), state=AddTemplate.media)
async def skip_media(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['media_file_id'] = None
        data['media_type'] = None
    await message.answer("Shablon linkini yuboring:", reply_markup=cancel_markup)
    await AddTemplate.next()

@dp.message_handler(state=AddTemplate.link)
async def process_link(message: types.Message, state: FSMContext):
    if message.text == "Bekor qilish ❌":
        await state.finish()
        await message.answer("✅ Amal bekor qilindi", reply_markup=admin)
        return

    if not message.text.startswith(('http://', 'https://')):
        await message.answer("Iltimos, to'g'ri link yuboring!")
        return

    async with state.proxy() as data:
        template_data = {
            'name': data['name'],
            'description': data['description'],
            'category': data['category'],
            'link': message.text,
            'username': message.from_user.username,
            'media_file_id': data.get('media_file_id'),
            'media_type': data.get('media_type')
        }

        await db.add_template(
            user_id=message.from_user.id,
            name=data['name'],
            category=data['category'],
            description=data['description'],
            link=message.text,
            media_file_id=data.get('media_file_id'),
            media_type=data.get('media_type')
        )

        await send_template_to_channel(template_data)
        await message.answer("✅ Shablon muvaffaqiyatli qo'shildi va kanalga yuborildi!", reply_markup=admin)

    await state.finish()