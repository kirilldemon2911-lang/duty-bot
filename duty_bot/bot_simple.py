import telebot
import json
import random

# ТВОЙ ТОКЕН
TOKEN = "8362260678:AAGF1ObDqQuCdDXhpIiPISf3Zqv-qL6wnlY"

bot = telebot.TeleBot(TOKEN)

# Подгруппа 1
GROUP1 = [
    {"id": "g1_01", "name": "Афанасьева Илона Андреевна", "count": 0},
    {"id": "g1_02", "name": "Архипушкин Денис", "count": 12},
    {"id": "g1_03", "name": "Березин Дмитрий Сергеевич", "count": 2},
    {"id": "g1_04", "name": "Бетке Кирилл Антонович", "count": 0},
    {"id": "g1_05", "name": "Бакулев Даниил", "count": 3},
    {"id": "g1_06", "name": "Гребенева Ольга Владимировна", "count": 2},
    {"id": "g1_07", "name": "Демакова Александра Андреевна", "count": 0},
    {"id": "g1_08", "name": "Дранишников Александр Олегович", "count": 41},
    {"id": "g1_09", "name": "Ермохина Дарья Дмитриевна", "count": 0},
    {"id": "g1_10", "name": "Жукова Светлана Алексеевна", "count": 1},
    {"id": "g1_11", "name": "Котовщиков Дмитрий Вадимович", "count": 0},
    {"id": "g1_12", "name": "Андреев Александр Александрович", "count": 0},
]

# Подгруппа 2
GROUP2 = [
    {"id": "g2_01", "name": "Лучинин Владислав Николаевич", "count": 9},
    {"id": "g2_02", "name": "Лопарев Владислав Павлович", "count": 5},
    {"id": "g2_03", "name": "Назарова Лайло Бахтиёрджоновна", "count": 0},
    {"id": "g2_04", "name": "Папанов Иван Денисович", "count": 12},
    {"id": "g2_05", "name": "Пахомов Кирилл Артурович", "count": 0},
    {"id": "g2_06", "name": "Прохорова Александра Алексеевна", "count": 0},
    {"id": "g2_07", "name": "Савин Иван Аркадьевич", "count": 11},
    {"id": "g2_08", "name": "Спасельников Эрик Павлович", "count": 5},
    {"id": "g2_09", "name": "Струлева Вера Игоревна", "count": 12},
    {"id": "g2_10", "name": "Твердякова Марина Андреевна", "count": 0},
    {"id": "g2_11", "name": "Шишеня Мария Григорьевна", "count": 0},
    {"id": "g2_12", "name": "Янковская Венера Васильевна", "count": 6},
]

def load_data():
    try:
        with open('duty_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['group1'], data['group2']
    except:
        return [s.copy() for s in GROUP1], [s.copy() for s in GROUP2]

def save_data(g1, g2):
    with open('duty_data.json', 'w', encoding='utf-8') as f:
        json.dump({'group1': g1, 'group2': g2}, f, ensure_ascii=False, indent=2)

group1, group2 = load_data()
user_data = {}

def find_by_id(group, sid):
    for s in group:
        if s['id'] == sid:
            return s
    return None

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
        user_data[chat_id] = {'days': days, 'absent1': [], 'absent2': []}
        show_absent_group1(call)
    
    elif call.data.startswith('a1_'):
        sid = call.data[3:]
        if sid in user_data[chat_id]['absent1']:
            user_data[chat_id]['absent1'].remove(sid)
        else:
            user_data[chat_id]['absent1'].append(sid)
        show_absent_group1(call)
    
    elif call.data.startswith('a2_'):
        sid = call.data[3:]
        if sid in user_data[chat_id]['absent2']:
            user_data[chat_id]['absent2'].remove(sid)
        else:
            user_data[chat_id]['absent2'].append(sid)
        show_absent_group2(call)
    
    elif call.data == 'next_g2':
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
    markup.add(telebot.types.InlineKeyboardButton("📋 ПОДГРУППА 1", callback_data='noop'))
    
    for student in group1:
        status = "❌" if student["id"] in absent else "✅"
        markup.add(telebot.types.InlineKeyboardButton(
            f"{status} {student['name']}", 
            callback_data=f'a1_{student["id"]}'
        ))
    
    markup.add(telebot.types.InlineKeyboardButton("➡️ Далее", callback_data='next_g2'))
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='back'))
    
    text = f"👥 Отметь отсутствующих в ПОДГРУППЕ 1:\n✅ - на месте\n❌ - отсутствует\n\nДней: {days}"
    bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)

def show_absent_group2(call):
    chat_id = call.message.chat.id
    absent = user_data[chat_id]['absent2']
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(telebot.types.InlineKeyboardButton("📋 ПОДГРУППА 2", callback_data='noop'))
    
    for student in group2:
        status = "❌" if student["id"] in absent else "✅"
        markup.add(telebot.types.InlineKeyboardButton(
            f"{status} {student['name']}", 
            callback_data=f'a2_{student["id"]}'
        ))
    
    markup.add(telebot.types.InlineKeyboardButton("✔️ Готово", callback_data='generate'))
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='days_' + str(user_data[chat_id]['days'])))
    
    text = "👥 Отметь отсутствующих в ПОДГРУППЕ 2:"
    bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)

def generate(call):
    chat_id = call.message.chat.id
    days = user_data[chat_id]['days']
    absent1_ids = user_data[chat_id]['absent1']
    absent2_ids = user_data[chat_id]['absent2']
    
    available1 = [s for s in group1 if s["id"] not in absent1_ids]
    available2 = [s for s in group2 if s["id"] not in absent2_ids]
    
    if len(available1) < days or len(available2) < days:
        bot.edit_message_text("❌ Ошибка: недостаточно учеников!", 
            chat_id, call.message.message_id, reply_markup=main_menu())
        return
    
    schedule = []
    used1 = set()
    used2 = set()
    
    for day in range(1, days + 1):
        # Группа 1
        cand1 = [s for s in available1 if s["id"] not in used1]
        if not cand1:
            used1 = set()
            cand1 = available1
        min1 = min(s["count"] for s in cand1)
        best1 = [s for s in cand1 if s["count"] == min1]
        sel1 = random.choice(best1)
        
        # Группа 2
        cand2 = [s for s in available2 if s["id"] not in used2]
        if not cand2:
            used2 = set()
            cand2 = available2
        min2 = min(s["count"] for s in cand2)
        best2 = [s for s in cand2 if s["count"] == min2]
        sel2 = random.choice(best2)
        
        schedule.append({
            "day": day,
            "p1": {"name": sel1["name"], "count": sel1["count"]},
            "p2": {"name": sel2["name"], "count": sel2["count"]},
            "id1": sel1["id"],
            "id2": sel2["id"]
        })
        used1.add(sel1["id"])
        used2.add(sel2["id"])
    
    user_data[chat_id]['schedule'] = schedule
    
    text = f"📋 Расписание на {days} дней:\n\n"
    for item in schedule:
        text += f"📅 День {item['day']}:\n"
        text += f"   👤 {item['p1']['name']} (гр.1, {item['p1']['count']} раз)\n"
        text += f"   👤 {item['p2']['name']} (гр.2, {item['p2']['count']} раз)\n\n"
    
    if absent1_ids or absent2_ids:
        text += "🚫 Отсутствуют:\n"
        if absent1_ids:
            names1 = [find_by_id(group1, i)["name"] for i in absent1_ids]
            text += f"   Гр.1: {', '.join(names1)}\n"
        if absent2_ids:
            names2 = [find_by_id(group2, i)["name"] for i in absent2_ids]
            text += f"   Гр.2: {', '.join(names2)}\n"
    
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
        for s in group1:
            if s["id"] == item["id1"]:
                s["count"] += 1
                break
        for s in group2:
            if s["id"] == item["id2"]:
                s["count"] += 1
                break
    
    save_data(group1, group2)
    
    text = "✅ Сохранено!\n\n📊 Статистика:\n\n📋 Подгруппа 1:\n"
    for s in sorted(group1, key=lambda x: x['count']):
        text += f"{s['name'][:28]}: {s['count']}\n"
    
    text += "\n📋 Подгруппа 2:\n"
    for s in sorted(group2, key=lambda x: x['count']):
        text += f"{s['name'][:28]}: {s['count']}\n"
    
    bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=main_menu())

def show_stats(call):
    text = "📊 Статистика:\n\n📋 Подгруппа 1:\n"
    for s in sorted(group1, key=lambda x: x['count'], reverse=True):
        bar = "█" * min(s['count'], 10)
        text += f"{s['name'][:22]}: {s['count']} {bar}\n"
    
    text += "\n📋 Подгруппа 2:\n"
    for s in sorted(group2, key=lambda x: x['count'], reverse=True):
        bar = "█" * min(s['count'], 10)
        text += f"{s['name'][:22]}: {s['count']} {bar}\n"
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='back'))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

def show_lists(call):
    text = "📋 Списки:\n\n📋 Подгруппа 1:\n"
    for i, s in enumerate(group1, 1):
        text += f"{i}. {s['name']} ({s['count']} раз)\n"
    
    text += "\n📋 Подгруппа 2:\n"
    for i, s in enumerate(group2, 1):
        text += f"{i}. {s['name']} ({s['count']} раз)\n"
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='back'))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

def show_help(call):
    text = "❓ Помощь:\n\n📝 Создать дежурство\n👥 2 человека (по одному из каждой подгруппы)\n✅ Отмечай отсутствующих\n🔄 Автовыбор по счётчику"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data='back'))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

print("Бот запущен!")
bot.polling(none_stop=True)
