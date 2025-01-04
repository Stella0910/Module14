from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
kb_starter = ReplyKeyboardMarkup(resize_keyboard=True).add(button1, button2).row(button3)

button_inline1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_inline2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_inline = InlineKeyboardMarkup(resize_keyboard=True).add(button_inline1, button_inline2)


class Product:
    def __init__(self, name, description, price):
        self.name = name
        self.description = description
        self.price = price


product1 = Product("Solgar Цитрат магния", "Таблетки массой 1540 мг 60 шт", 1403)
product2 = Product("NOW Vitamin D2", "D2 1000 IU (120 вег. капс.)", 1090)
product3 = Product("Maxler 100% Golden Whey", "Протеин сывороточный 907г. Молочный шоколад", 4000)
product4 = Product("Maxler Creatine", "100% rреатин моногидрат 500г", 3070)

products = [product1, product2, product3, product4]

button_product1 = InlineKeyboardButton(text=f'{product1.name}', callback_data='product_buying')
button_product2 = InlineKeyboardButton(text=f'{product2.name}', callback_data='product_buying')
button_product3 = InlineKeyboardButton(text=f'{product3.name}', callback_data='product_buying')
button_product4 = InlineKeyboardButton(text=f'{product4.name}', callback_data='product_buying')
kb_products = InlineKeyboardMarkup().add(button_product1, button_product2).add(button_product3, button_product4)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer(f'Привет, {message.from_user.username}! Я бот помогающий твоему здоровью.',
                         reply_markup=kb_starter)


@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb_inline)


@dp.message_handler(text=['Информация'])
async def main_menu(message):
    await message.answer('Информация о боте')


@dp.message_handler(text=['Купить'])
async def get_buying_list(message):
    k = 0
    for i in products:
        if k <= len(products):
            await message.answer(f'Название: {i.name}| Описание: {i.description} | Цена: {i.price}')
            k += 1
            with open(f'{k}.png', 'rb') as img:
                await message.answer_photo(img)
        else:
            break
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


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
