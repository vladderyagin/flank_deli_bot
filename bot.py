import os
import json
from flask import Flask, request
import requests

app = Flask(__name__)

# Настройки бота
TOKEN = os.environ.get("TELEGRAM_TOKEN")
YOUR_USER_ID = os.environ.get("YOUR_USER_ID")  # Ваш ID для уведомлений
URL = f"https://api.telegram.org/bot{TOKEN}"

# Меню
menu = {
    "1": {"name": "🥩 Брискет", "price": 2500, "desc": "Говяжья грудинка, 12 часов копчения"},
    "2": {"name": "🥩 Ростбиф", "price": 2200, "desc": "Нежная говядина с травами"},
    "3": {"name": "🦆 Пастрами утка", "price": 1800, "desc": "Хрустящая корочка, сочное мясо"},
    "4": {"name": "🦃 Пастрами индейка", "price": 1500, "desc": "Диетическое, но сочное"},
    "5": {"name": "🍖 Ребра свиные", "price": 2000, "desc": "Карамельная глазурь, мясо от кости"},
    "6": {"name": "🐷 Рваная свинина", "price": 1800, "desc": "Для бургеров или отдельно"},
    "7": {"name": "🥪 Сэндвич с брискетом", "price": 450, "desc": "Домашний хлеб, соус BBQ"},
    "8": {"name": "🥪 Сэндвич пастрами утка", "price": 420, "desc": "Нежный и ароматный"},
    "9": {"name": "🥪 Сэндвич пастрами индейка", "price": 390, "desc": "Лёгкий и сытный"},
    "10": {"name": "🍔 Бургер рваная свинина", "price": 480, "desc": "Булочка бриошь, капуста слайс"},
    "11": {"name": "🍱 Набор ассорти", "price": 3500, "desc": "3 вида мяса + 2 гарнира"},
    "12": {"name": "🥒 Огурцы маринованные", "price": 250, "desc": "Домашние, хрустящие"},
    "13": {"name": "🥬 Капуста квашеная", "price": 200, "desc": "Классическая, с клюквой"}
}

# Хранилище заказов (временно, в памяти)
orders = {}

def send_message(chat_id, text, keyboard=None, parse_mode="Markdown"):
    """Отправить сообщение"""
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        response = requests.post(f"{URL}/sendMessage", json=data)
        return response.json()
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def main_menu():
    """Главное меню"""
    return {
        "inline_keyboard": [
            [{"text": "📋 Меню", "callback_data": "menu"}],
            [{"text": "🛒 Корзина", "callback_data": "cart"}],
            [{"text": "📞 Контакты", "callback_data": "contacts"}],
            [{"text": "❓ Помощь", "callback_data": "help"}]
        ]
    }

def show_menu(page=0):
    """Показать меню с пагинацией"""
    items_per_page = 5
    items = list(menu.items())
    start = page * items_per_page
    end = min(start + items_per_page, len(items))
    
    keyboard = {"inline_keyboard": []}
    
    for i in range(start, end):
        key, item = items[i]
        keyboard["inline_keyboard"].append([
            {"text": f"{item['name']} - {item['price']}₽", "callback_data": f"add_{key}"}
        ])
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append({"text": "⬅️ Назад", "callback_data": f"menu_page_{page-1}"})
    if end < len(items):
        nav_buttons.append({"text": "Вперед ➡️", "callback_data": f"menu_page_{page+1}"})
    
    if nav_buttons:
        keyboard["inline_keyboard"].append(nav_buttons)
    
    keyboard["inline_keyboard"].append([{"text": "🔙 В главное меню", "callback_data": "main_menu"}])
    
    return keyboard

@app.route("/", methods=["GET"])
def index():
    return "Бот Flank Delicatessen работает! 🔥"

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    """Обработка сообщений от Telegram"""
    update = request.get_json()
    if not update:
        return "ok", 200
    
    # Обработка обычных сообщений
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        user_name = update["message"]["chat"].get("first_name", "")
        
        if text == "/start":
            send_message(
                chat_id,
                f"🔥 Привет, {user_name}!\n\n"
                f"Добро пожаловать в *Flank Delicatessen* — коптильню настоящего мяса.\n\n"
                f"• Выбирайте блюда из меню\n"
                f"• Добавляйте в корзину\n"
                f"• Оформляйте заказ\n\n"
                f"Мы свяжемся с вами в течение часа!\n\n"
                f"*Приятного аппетита!* 🥩",
                keyboard=main_menu()
            )
        
        elif text == "/menu":
            send_message(chat_id, "📋 Наше меню:", keyboard=show_menu())
        
        elif text == "/help":
            send_message(
                chat_id,
                "❓ *Помощь*\n\n"
                "• /start — начать\n"
                "• /menu — меню\n"
                "• /help — помощь\n\n"
                "Или используйте кнопки под сообщениями",
                keyboard=main_menu()
            )
    
    # Обработка нажатий на кнопки
    elif "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        data = callback["data"]
        user_name = callback["from"].get("first_name", "")
        
        # Главное меню
        if data == "main_menu":
            send_message(
                chat_id,
                "🔥 *Flank Delicatessen*\n\nВыберите действие:",
                keyboard=main_menu()
            )
        
        elif data == "menu":
            send_message(chat_id, "📋 Наше меню:", keyboard=show_menu())
        
        elif data.startswith("menu_page_"):
            page = int(data.split("_")[2])
            send_message(chat_id, "📋 Наше меню:", keyboard=show_menu(page))
        
        # Добавление в корзину
        elif data.startswith("add_"):
            item_key = data.split("_")[1]
            item = menu.get(item_key)
            
            if item_key not in orders:
                orders[item_key] = []
            orders[item_key].append(chat_id)
            
            # Отправляем подтверждение
            send_message(
                chat_id,
                f"✅ *{item['name']}* добавлен в корзину!\n\n"
                f"💰 Цена: {item['price']}₽\n"
                f"📝 {item['desc']}\n\n"
                f"Продолжайте выбирать или перейдите в корзину 🛒",
                keyboard=main_menu()
            )
            
            # Уведомление админу
            if YOUR_USER_ID:
                send_message(
                    YOUR_USER_ID,
                    f"🆕 *Добавлен товар в корзину*\n\n"
                    f"👤 {user_name}\n"
                    f"🆔 {chat_id}\n"
                    f"📦 {item['name']} - {item['price']}₽"
                )
        
        # Просмотр корзины (упрощённо)
        elif data == "cart":
            user_items = []
            for key, user_list in orders.items():
                if chat_id in user_list:
                    item = menu[key]
                    count = user_list.count(chat_id)
                    user_items.append(f"• {item['name']} x{count} — {item['price'] * count}₽")
            
            if user_items:
                total = sum([int(item['price']) * orders[key].count(chat_id) for key, item in menu.items() if chat_id in orders.get(key, [])])
                cart_text = "🛒 *Ваша корзина:*\n\n" + "\n".join(user_items) + f"\n\n💰 *Итого: {total}₽*"
                
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "✅ Оформить заказ", "callback_data": "checkout"}],
                        [{"text": "🗑 Очистить корзину", "callback_data": "clear_cart"}],
                        [{"text": "🔙 В главное меню", "callback_data": "main_menu"}]
                    ]
                }
                send_message(chat_id, cart_text, keyboard=keyboard)
            else:
                send_message(chat_id, "🛒 Корзина пуста", keyboard=main_menu())
        
        # Оформление заказа
        elif data == "checkout":
            user_items = []
            for key, user_list in orders.items():
                if chat_id in user_list:
                    item = menu[key]
                    count = user_list.count(chat_id)
                    user_items.append(f"{item['name']} x{count}")
            
            if user_items:
                total = sum([int(item['price']) * orders[key].count(chat_id) for key, item in menu.items() if chat_id in orders.get(key, [])])
                
                # Отправляем заказ админу
                if YOUR_USER_ID:
                    send_message(
                        YOUR_USER_ID,
                        f"🆕 *НОВЫЙ ЗАКАЗ!*\n\n"
                        f"👤 {user_name}\n"
                        f"📞 ID: {chat_id}\n"
                        f"📦 Товары:\n" + "\n".join([f"  • {item}" for item in user_items]) +
                        f"\n\n💰 Сумма: {total}₽"
                    )
                
                # Очищаем корзину пользователя
                for key in list(orders.keys()):
                    orders[key] = [user for user in orders[key] if user != chat_id]
                
                send_message(
                    chat_id,
                    f"✅ *Заказ оформлен!*\n\n"
                    f"📦 Состав:\n" + "\n".join([f"• {item}" for item in user_items]) +
                    f"\n\n💰 Сумма: {total}₽\n\n"
                    f"📞 Мы свяжемся с вами в ближайшее время для подтверждения.\n\n"
                    f"*Спасибо за заказ!* 🔥",
                    keyboard=main_menu()
                )
            else:
                send_message(chat_id, "❌ Корзина пуста", keyboard=main_menu())
        
        # Очистка корзины
        elif data == "clear_cart":
            for key in list(orders.keys()):
                orders[key] = [user for user in orders[key] if user != chat_id]
            send_message(chat_id, "🗑 Корзина очищена", keyboard=main_menu())
        
        # Контакты
        elif data == "contacts":
            send_message(
                chat_id,
                "📞 *Наши контакты*\n\n"
                "📍 Доставка по городу\n"
                "⏰ Режим: 10:00 - 20:00\n\n"
                "📱 +7 (XXX) XXX-XX-XX\n"
                "💬 @flank_deli_manager\n"
                "📧 flank@delicatessen.ru",
                keyboard=main_menu()
            )
        
        # Помощь
        elif data == "help":
            send_message(
                chat_id,
                "❓ *Помощь*\n\n"
                "📋 *Как сделать заказ:*\n"
                "1. Нажмите 'Меню'\n"
                "2. Выберите товары\n"
                "3. Перейдите в 'Корзину'\n"
                "4. Нажмите 'Оформить заказ'\n\n"
                "Мы свяжемся с вами в течение часа!\n\n"
                "Вопросы: @flank_deli_manager",
                keyboard=main_menu()
            )
    
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
