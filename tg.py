from aiogram import types, Bot, Dispatcher
from aiogram.filters import Command
import asyncio
import aiogram.exceptions

TOKEN = "7617093251:AAGP5Oq1yiRa110KZV-9HwWoqfBuypcPyx0"
channel_name = "@zayavkalarkanali"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}


@dp.message()
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data or message.text == '/start' or message.text == "Zayavka qoldirish":
        await start(message)
    elif 'name' not in user_data[user_id]:
        await ask_phone(message)
    elif 'phone' not in user_data[user_id]:
        await ask_age(message)
    elif 'kitob' not in user_data[user_id]:
        await kitob(message)
    elif message.text == "Kitob buyurtma qilish":
        await kitoblar(message)
    elif message.text == "Sariq def":
        await buyurtma(message)
    elif message.answer == "Mahsulot {item} savatga muvaffaqiyatli qo'shildi ✅":
        await total_info(message)



@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    await message.answer("Assalomu alaykum! \nIltimos ismingizni kiriting:")
    print(user_data)


async def ask_phone(message: types.Message):
    user_id = message.from_user.id
    name = message.text
    user_data[user_id]["name"] = name
    button = [
        [types.KeyboardButton(text="Raqam jo'natish", request_contact=True)]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)
    await message.answer("Iltimos telefon raqamingizni kiritng:", reply_markup=keyboard)
    print(user_data)


async def ask_age(message: types.Message):
    user_id = message.from_user.id
    if message.contact is not None:
        phone = message.contact.phone_number
    else:
        phone = message.text
    user_data[user_id]['phone'] = phone
    await message.answer("Iltimos yoshingizni kiriting:")
    print(user_data)


async def kitob(message: types.Message):
    user_id = message.from_user.id
    kitob = message.text
    user_data[user_id]['kitob'] = kitob
    button = [
        [types.KeyboardButton(text="Kitob buyurtma qilish")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)
    await message.answer("Kitob buyurtma qilish",reply_markup=keyboard)
    print(user_data)

async def kitoblar(message: types.Message):
    user_id = message.from_user.id
    kitoblar = message.text
    user_data[user_id]['kitoblar'] = kitoblar
    button = [
        [types.KeyboardButton(text='Sariq def')]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)
    await message.answer('Nimadan boshlaymiz?', reply_markup=keyboard)
    print(user_data)


async def buyurtma(message: types.Message):
    user_id = message.from_user.id
    item = message.text
    user_data[user_id]['buyurtma'] = item
    price = 20000
    button = [
        [types.InlineKeyboardButton(text="-", callback_data=f"minus_{item}"),
         types.InlineKeyboardButton(text="1", callback_data=f"miqdor_{item}"),
         types.InlineKeyboardButton(text="+", callback_data=f"plus_{item}")],
        [types.InlineKeyboardButton(text="📥 Savatga qo'shish ✅", callback_data=f"add_{item}")]
    ]
    buttons = [
        [types.KeyboardButton(text='👈🏻Ortga'), types.KeyboardButton(text="📥 Savatga qo'shish ✅")]
    ]
    keyboards = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=button, resize_keyboard=True)
    file_path = "image/kombo.jpg"
    caption_text = (f"{item}\n"
                    "Fri kartoshkasiCoca-cola 0.5\n"
                    f"Narxi:{price} so'm")
    await message.answer("Miqdorini belgilang", reply_markup=keyboards)
    await message.reply_photo(caption=caption_text, photo=types.FSInputFile(path=file_path), parse_mode='Markdown',
                              reply_markup=keyboard)
    # await message.answer("", reply_markup=keyboard)
    print(user_data)


count = 1
@dp.callback_query(lambda c: c.data.startswith(('plus', 'minus', 'add')))
async def checkcallback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    narx = callback.data
    price = 20000
    description = "Fri kartoshkasiCoca-cola 0.5\n"
    command, item = callback.data.split('_')
    global count
    # global price

    if command == 'plus':
        count += 1
    elif command == 'minus':
        if count > 1:
            count -= 1
    elif command == 'add':
        if 'basket' not in user_data[user_id]:
            user_data[user_id]['basket'] = {item: count}
        else:
            if item in user_data[user_id]['basket']:
                user_data[user_id]['basket'][item] += count
            else:
                user_data[user_id]['basket'][item] = count

        count = 1  # Reset count after adding item to the basket
        await callback.message.answer(f"Mahsulot {item} savatga muvaffaqiyatli qo'shildi ✅")
        await callback.message.answer(f"Davom etamizmi?")

    print(f"Count:{count}")
    button = [
        [types.InlineKeyboardButton(text=f"-", callback_data=f"minus_{item}"),
         types.InlineKeyboardButton(text=f"{count}", callback_data=f"miqdor_{item}"),
         types.InlineKeyboardButton(text=f"+", callback_data=f"plus_{item}"), ],
        [types.InlineKeyboardButton(text=f"📥Savatga qo'shish✅", callback_data=f"add_{item}"), ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=button, resize_keyboard=True)
    price = price * count  # Update the price based on count
    try:
        print(user_data)
        await callback.message.edit_caption(
            caption="Kombo set\n"
                    f"{description}"
                    f"Narxi: {price} so'm",
            reply_markup=keyboard
        )
    except aiogram.exceptions.TelegramBadRequest as e:
        if "message is not modified" in str(e):
            print("Xabar o'zgarmaganligi sababli yangilash o'tkazib yuborildi.")
        else:
            print(f"Xato yuz berdi: {e}")

async def total_info(message: types.Message):
    user_id = message.from_user.id
    age = message.text
    user_data[user_id]['age'] = age
    button = [
        [types.KeyboardButton(text="Zayavka qoldirish")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)
    name = user_data[user_id]['name']
    phone = user_data[user_id]['phone']
    message_text = (f"Ismingiz: {name}\n"
                    f"Yoshingiz: {age}\n"
                    f"Telefon raqamingiz: {phone}")
    await message.answer(f"Zayavkangiz qabul qilindi\n{message_text}", reply_markup=keyboard)
    await bot.send_message(channel_name, message_text)
    print(user_data)
    del user_data[user_id]
    print(user_data)


async def main():
    await dp.start_polling(bot)


print("The bot is running...")
asyncio.run(main())
