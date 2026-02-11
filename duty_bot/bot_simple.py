import telebot
import json
import random

# ЗАМЕНИ НА СВОЙ ТОКЕН ОТ @BotFather
TOKEN = "8362260678:AAGF1ObDqQuCdDXhpIiPISf3Zqv-qL6wnlY"

bot = telebot.TeleBot(TOKEN)

# Подгруппа 1
GROUP1 = [
    {"name": "Афанасьева Илона Андреевна", "count": 0},
    {"name": "Архипушкин Денис", "count": 12},
    {"name": "Березин Дмитрий Сергеевич", "count": 2},
    {"name": "Бетке Кирилл Антонович", "count": 0},
    {"name": "Бакулев Даниил", "count": 3},
    {"name": "Гребенева Ольга Владимировна", "count": 2},
    {"name": "Демакова Александра Андреевна", "count": 0},
    {"name": "Дранишников Александр Олегович", "count": 41},
    {"name": "Ермохина Дарья Дмитриевна", "count": 0},
    {"name": "Жукова Светлана Алексеевна", "count": 1},
    {"name": "Котовщиков Дмитрий Вадимович", "count": 0},
    {"name": "Андреев Александр Александрович", "count": 0},  # Новый ученик
]

# Подгруппа 2
GROUP2 = [
    {"name": "Лучинин Владислав Николаевич", "count": 9},
    {"name": "Лопарев Владислав Павлович", "count": 5},
    {"name": "Назарова Лайло Бахтиёрджоновна", "count": 0},
    {"name": "Папанов Иван Денисович", "count": 12},
    {"name": "Пахомов Кирилл Артурович", "count": 0},
    {"name": "Прохорова Александра Алексеевна", "count": 0},
    {"name": "Савин Иван Аркадьевич", "count": 11},
    {"name": "Спасельников Эрик Павлович", "count": 5},
    {"name": "Струлева Вера Игоревна", "count": 12},
    {"name": "Твердякова Марина Андреевна", "count": 0},
    {"name": "Шишеня Мария Григорьевна", "count": 0},
    {"name": "Янковская Венера Васильевна", "count": 6},
]

def load_data():
    try:
        with open('duty_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['group1'], data['group2']
    except:
        return [s.copy() for s in GROUP1], [s.copy() for s in GROUP2]

def save_data(group1, group2):
    with open('duty_data.json', 'w', encoding='utf-8') as f:
        json.dump({'group1': group1, 'group2': group2}, f, ensure_ascii=False, indent=2)

group1, group2 = load_data()
user_data = {}

def main_menu():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("📝 Создать дежурство", callback_data='create'),
        telebot.types.InlineKeyboardButton("📊 Статистика", callback_data='stats'),
        telebot.types.InlineKeyboardButton("📋 Списки", callback_data='list'),
        telebot.types.InlineKeyboardButton("❓ Помощь", callback_data='help')
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
        "👋 Привет! Я бот для дежурств.\n\nКаждый день дежурит по 2 человека:\n• 1 человек из подгруппы 1\n• 1 человек из подгруппы 2\n\nВыбери действие:", 
        reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    if call.data == 'create':
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("5 дней", callback_data='days_5'),
            telebot.types.InlineKeyboardButton("6 дней", callback_data='days_6'),
            telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='back')
        )
        bot.edit_message_text("📅 Выбери количество дней:", chat_id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith('days_'):
        days = int(call.data.split('_')[1])
        user_data[chat_id] = {
            'days': days, 
            'absent1': [], 
            'absent2': [],
            'step': 1
        }
        show_absent_group1(call)
    
    elif call.data.startswith('abs1_'):
        name = call.data[5:]
        if name in user_data[chat_id]['absent1']:
            user_data[chat_id]['absent1'].remove(name)
        else:
            user_data[chat_id]['absent1'].append(name)
        show_absent_group1(call)
    
    elif call.data.startswith('abs2_'):
        name = call.data[5:]
        if name in user_data[chat_id]['absent2']:
            user_data[chat_id]['absent2'].remove(name)
        else:
            user_data[chat_id]['absent2'].append(name)
        show_absent_group2(call)
    
    elif call.data == 'next_group2':
        show_absent_group2(call)
    
    elif call.data == 'generate':
        generate(call)
    
    elif call.data == 'save':
        save_schedule(call)
    
    elif call.data == 'regen':
        generate(call)
    
    elif call.data == 'stats':
        show_stats(call)
    
    elif call.data == 'list':
        show_lists(call)
    
    elif call.data == 'help':
        show_help(call)
    
    elif call.data == 'back':
        bot.edit_message_text("👋 Главное меню\n\nВыбери действие:", 
            chat_id, call.message.message_id, reply_markup=main_menu())

def show_absent_group1(call):
    chat_id = call.message.chat.id
    absent = user_data[chat_id]['absent1']
    days = user_data[chat_id]['days']
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(telebot.types.InlineKeyboardButton("📋 ПОДГРУППА 1:", callback_data='noop'))
    
    for student in group1:
        status = "❌" if student["name"] in absent else "✅"
        markup.add(telebot.types.InlineKeyboardButton(
            f"{status} {student['name']}", 
            callback_data=f'abs1_{student["name"]}'
        ))
    
    markup.add(telebot.types.InlineKeyboardButton("➡️ Далее (Подгруппа 2)", callback_data='next_group2'))
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='back'))
    
    text = f"👥 Отметь отсутствующих в ПОДГРУППЕ 1:\n✅ - на месте\n❌ - отсутствует\n\nДней: {days}"
    bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)

def show_absent_group2(call):
    chat_id = call.message.chat.id
    absent = user_data[chat_id]['absent2']
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(telebot.types.InlineKeyboardButton("📋 ПОДГРУППА 2:", callback_data='noop'))
    
    for student in group2:
        status = "❌" if student["name"] in absent else "✅"
        markup.add(telebot.types.InlineKeyboardButton(
            f"{status} {student['name']}", 
            callback_data=f'abs2_{student["name"]}'
        ))
    
    markup.add(telebot.types.InlineKeyboardButton("✔️ Готово", callback_data='generate'))
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад (Подгруппа 1)", callback_data='days_' + str(user_data[chat_id]['days'])))
    
    text = "👥 Отметь отсутствующих в ПОДГРУППЕ 2:\n✅ - на месте\n❌ - отсутствует"
    bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)

def generate(call):
    chat_id = call.message.chat.id
    days = user_data[chat_id]['days']
    absent1 = user_data[chat_id]['absent1']
    absent2 = user_data[chat_id]['absent2']
    
    available1 = [s for s in group1 if s["name"] not in absent1]
    available2 = [s for s in group2 if s["name"] not in absent2]
    
    if len(available1) < days or len(available2) < days:
        bot.edit_message_text("❌ Ошибка: недостаточно учеников в одной из подгрупп!", 
            chat_id, call.message.message_id, reply_markup=main_menu())
        return
    
    schedule = []
    used1 = set()
    used2 = set()
    
    for day in range(1, days + 1):
        # Выбираем из подгруппы 1
        candidates1 = [s for s in available1 if s["name"] not in used1]
        if not candidates1:
            used1 = set()
            candidates1 = available1
        min_count1 = min(s["count"] for s in candidates1)
        best1 = [s for s in candidates1 if s["count"] == min_count1]
        selected1 = random.choice(best1)
        
        # Выбираем из подгруппы 2
        candidates2 = [s for s in available2 if s["name"] not in used2]
        if not candidates2:
            used2 = set()
            candidates2 = available2
        min_count2 = min(s["count"] for s in candidates2)
        best2 = [s for s in candidates2 if s["count"] == min_count2]
        selected2 = random.choice(best2)
        
        schedule.append({
            "day": day,
            "person1": {"name": selected1["name"], "count": selected1["count"]},
            "person2": {"name": selected2["name"], "count": selected2["count"]}
        })
        used1.add(selected1["name"])
        used2.add(selected2["name"])
    
    user_data[chat_id]['schedule'] = schedule
    
    text = f"📋 Расписание на {days} дней:\n\n"
    for item in schedule:
        text += f"📅 День {item['day']}:\n"
        text += f"   👤 {item['person1']['name']} (гр.1, {item['person1']['count']} раз)\n"
        text += f"   👤 {item['person2']['name']} (гр.2, {item['person2']['count']} раз)\n\n"
    
    if absent1 or absent2:
        text += "🚫 Отсутствуют:\n"
        if absent1:
            text += f"   Гр.1: {', '.join(absent1)}\n"
        if absent2:
            text += f"   Гр.2: {', '.join(absent2)}\n"
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ Сохранить", callback_data='save'),
        telebot.types.InlineKeyboardButton("🔄 Пересоздать", callback_data='regen'),
        telebot.types.InlineKeyboardButton("❌ Отмена", callback_data='back')
    )
    
    bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)

def save_schedule(call):
    chat_id = call.message.chat.id
    schedule = user_data[chat_id]['schedule']
    
    for item in schedule:
        # Обновляем счётчики в группе 1
        for student in group1:
            if student["name"] == item['person1']['name']:
                student["count"] += 1
                break
        # Обновляем счётчики в группе 2
        for student in group2:
            if student["name"] == item['person2']['name']:
                student["count"] += 1
                break
    
    save_data(group1, group2)
    
    text = "✅ Сохранено!\n\n📊 Статистика по подгруппам:\n\n📋 Подгруппа 1:\n"
    for student in sorted(group1, key=lambda x: x['count']):
        text += f"{student['name'][:28]}: {student['count']}\n"
    
    text += "\n📋 Подгруппа 2:\n"
    for student in sorted(group2, key=lambda x: x['count']):
        text += f"{student['name'][:28]}: {student['count']}\n"
    
    bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=main_menu())

def show_stats(call):
    text = "📊 Статистика дежурств:\n\n"
    
    text += "📋 Подгруппа 1:\n"
    for student in sorted(group1, key=lambda x: x['count'], reverse=True):
        bar = "█" * min(student['count'], 10)
        text += f"{student['name'][:22]}: {student['count']} {bar}\n"
    
    text += "\n📋 Подгруппа 2:\n"
    for student in sorted(group2, key=lambda x: x['count'], reverse=True):
        bar = "█" * min(student['count'], 10)
        text += f"{student['name'][:22]}: {student['count']} {bar}\n"
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='back'))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

def show_lists(call):
    text = "📋 Списки учеников:\n\n"
    
    text += "📋 Подгруппа 1 ({} чел.):\n".format(len(group1))
    for i, student in enumerate(group1, 1):
        text += f"{i}. {student['name']} ({student['count']} раз)\n"
    
    text += "\n📋 Подгруппа 2 ({} чел.):\n".format(len(group2))
    for i, student in enumerate(group2, 1):
        text += f"{i}. {student['name']} ({student['count']} раз)\n"
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='back'))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

def show_help(call):
    text = ("❓ Помощь:\n\n"
            "📝 Создать дежурство — расписание на 5 или 6 дней\n"
            "👥 Каждый день дежурит 2 человека (по одному из каждой подгруппы)\n"
            "✅ Отмечай отсутствующих в обеих подгруппах\n"
            "🔄 Бот автоматически выбирает тех, кто дежурил меньше")
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='back'))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

print("Бот запущен! Напиши /start в Telegram")
bot.polling(none_stop=True)