from telebot.handler_backends import State, StatesGroup
#1. Имя
#2. Возраст
#3. Страна
#4. Город
#5. Номер телефона
#6. Кол-во отелей необходимо вывести
#7. Необходимость фотографий
#8. Диапазон цен
#9. Диапазон расстояния, на котором находится отель от центра
class UserInfoState(StatesGroup):
    name = State()
    age = State()
    country = State()
    city = State()
    phone_number = State()
    number_of_hotel = State()
    need_photo = State()
    price_range = State()
    distance_range = State()
    low_city = State()
    low_number_of_hotel = State()
    lowprice_choice_photo = State()
    result = State()
    photo_count = State()
    photo_yes = State()
    photo_no = State()
    checkin = State()
    checkout = State()