from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio

from crud_functions2 import *

get_all_products()
connection_products = sqlite3.connect('Products.db')
cursor_products = connection_products.cursor()

product1 = ["Solgar Цитрат магния", "Таблетки массой 1540 мг 60 шт", 1403]
product2 = ["NOW Vitamin D2", "D2 1000 IU (120 вег. капс.)", 1090]
product3 = ["Maxler 100% Golden Whey", "Протеин сывороточный 907г. Молочный шоколад", 4000]
product4 = ["Maxler Creatine", "100% креатин моногидрат 500г", 3070]

products = [product1, product2, product3, product4]
for product in products:
    if is_included_product(f'{product[0]}') is False:
        add_product(f"{product[0]}", f"{product[1]}", f"{product[2]}")
    else:
        pass

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
button4 = KeyboardButton(text='Регистрация')
kb_starter = ReplyKeyboardMarkup(resize_keyboard=True).add(button1, button2).add(button3, button4)

button_inline1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_inline2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_inline = InlineKeyboardMarkup(resize_keyboard=True).add(button_inline1, button_inline2)

button_product1 = InlineKeyboardButton(text=f'{product1[0]}', callback_data='product_buying')
button_product2 = InlineKeyboardButton(text=f'{product2[0]}', callback_data='product_buying')
button_product3 = InlineKeyboardButton(text=f'{product3[0]}', callback_data='product_buying')
button_product4 = InlineKeyboardButton(text=f'{product4[0]}', callback_data='product_buying')
kb_products = InlineKeyboardMarkup().add(button_product1, button_product2).add(button_product3, button_product4)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000


@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer(f'Привет, {message.from_user.username}! Я бот помогающий твоему здоровью.',
                         reply_markup=kb_starter)


@dp.message_handler(text=['Регистрация'])
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if is_included(message.text) is False:
        await state.update_data(username=message.text)
        data_users = await state.get_data()
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()
    else:
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    data_users = await state.get_data()
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data_users = await state.get_data()
    add_user(data_users['username'], data_users['email'], data_users['age'])
    await message.answer('Регистрация прошла успешно!', reply_markup=kb_starter)
    await state.finish()


@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb_inline)


@dp.message_handler(text=['Информация'])
async def main_menu(message):
    await message.answer('Информация о боте')


@dp.message_handler(text=['Купить'])
async def get_buying_list(message):
    all_products = get_all_products()
    for one in all_products:
        await message.answer(f'Название: {one[0]} | Описание: {one[1]} | Цена: {one[2]}')
        number_photo = 1 + all_products.index(one)
        with open(f'./{number_photo}.png', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup=kb_products)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Упрощенный вариант формулы Миффлина-Сан Жеора:\n\n'
                              'для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;\n'
                              'для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    data = await state.get_data()
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    norm_women = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) - 161
    norm_men = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5
    await message.answer(f'Норма калорий для женщины:  {norm_women}\n'
                         f'Норма калорий для мужчины:  {norm_men}')
    await state.finish()


@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


connection_products.close()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
