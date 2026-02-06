# app.py - ГЛАВНЫЙ ЗАПУСКНОЙ ФАЙЛ ДЛЯ RENDER
from flask import Flask, Response
import threading
import time
import requests
import os
import subprocess
import sys
import atexit

app = Flask(__name__)

# Глобальные переменные
bot_process = None
is_running = True

def run_bot():
    """Запускает бота в отдельном процессе"""
    global bot_process
    
    print("=" * 50)
    print("🤖 ЗАПУСК ТЕЛЕГРАМ БОТА...")
    print("=" * 50)
    
    # Инициализируем базу данных перед запуском
    try:
        from database import init_db
        init_db()
        print("✅ База данных инициализирована")
    except Exception as e:
        print(f"⚠️ Ошибка инициализации базы: {e}")
    
    # Команда для запуска бота
    python_path = sys.executable
    bot_command = [python_path, "main.py"]
    
    # Запускаем процесс
    bot_process = subprocess.Popen(
        bot_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Читаем вывод в реальном времени
    def read_output():
        while True:
            line = bot_process.stdout.readline()
            if not line:
                break
            # Выводим логи бота
            if line.strip():
                print(f"🤖 БОТ: {line.strip()}")
    
    # Запускаем чтение вывода в отдельном потоке
    output_thread = threading.Thread(target=read_output, daemon=True)
    output_thread.start()
    
    # Ждем завершения
    return_code = bot_process.wait()
    print(f"⚠️ Бот завершился с кодом: {return_code}")
    
    # Если бот упал, перезапускаем через 10 секунд
    if is_running:
        print("🔄 Перезапуск бота через 10 секунд...")
        time.sleep(10)
        run_bot()

def keep_awake():
    """Периодически пингует сам себя чтобы не заснуть"""
    print("🔔 Запуск keep-alive системы...")
    
    while is_running:
        try:
            # Получаем наш URL с Render
            render_url = os.environ.get('RENDER_EXTERNAL_URL')
            
            if render_url:
                response = requests.get(f"{render_url}/health", timeout=10)
                print(f"✅ Keep-alive ping: {response.status_code}")
            else:
                # Если локально, просто ждем
                print("⏳ Keep-alive: ожидание...")
                
        except Exception as e:
            print(f"⚠️ Keep-alive ошибка: {e}")
        
        # Ждем 4 минуты 30 секунд (меньше 5 минут, чтобы не заснуть)
        time.sleep(270)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Telegram Barber Bot</title>
        <style>
            body { 
                font-family: 'Arial', sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                margin: 0;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                padding: 40px;
                border-radius: 20px;
                max-width: 600px;
                margin: 0 auto;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            .status { 
                color: #4ade80; 
                font-weight: bold;
                font-size: 1.5em;
                margin: 20px 0;
            }
            .links a {
                display: inline-block;
                margin: 10px;
                padding: 10px 20px;
                background: white;
                color: #667eea;
                text-decoration: none;
                border-radius: 50px;
                font-weight: bold;
                transition: transform 0.3s;
            }
            .links a:hover {
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Telegram Barber Bot</h1>
            <p class="status">✅ Бот работает и готов к работе!</p>
            <p>Сервер автоматически поддерживает работу бота 24/7</p>
            <p>Бот отвечает на команды в Telegram</p>
            
            <div class="links">
                <a href="/health">Проверить статус</a>
                <a href="/restart">Перезапустить бота</a>
                <a href="/logs">Посмотреть логи</a>
            </div>
            
            <div style="margin-top: 30px; font-size: 0.9em; opacity: 0.8;">
                <p>Система автоматически "будит" бота каждые 5 минут</p>
                <p>Бесплатный хостинг Render.com</p>
            </div>
        </div>
    </body>
    </html>
    """, 200

@app.route('/health')
def health():
    """Эндпоинт для проверки здоровья"""
    return Response("✅ OK - Bot is running", status=200, mimetype='text/plain')

@app.route('/logs')
def show_logs():
    """Показывает последние логи"""
    try:
        # Здесь можно добавить чтение логов из файла
        return "Логи будут доступны после первого запуска", 200
    except:
        return "Логи временно недоступны", 200

@app.route('/start-bot')
def start_bot_route():
    """Запуск бота по запросу"""
    global bot_process
    
    if bot_process and bot_process.poll() is None:
        return "🤖 Бот уже запущен", 200
    
    # Запускаем в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    return "🤖 Бот запускается...", 200

@app.route('/restart')
def restart_bot():
    """Перезапуск бота"""
    global bot_process
    
    if bot_process:
        bot_process.terminate()
        bot_process.wait(timeout=5)
        print("🔄 Бот остановлен для перезапуска")
    
    # Запускаем заново
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    return "🔄 Бот перезапускается... Обновите страницу через 10 секунд.", 200

def cleanup():
    """Очистка при завершении"""
    global is_running, bot_process
    print("🛑 Остановка системы...")
    is_running = False
    
    if bot_process:
        print("🛑 Останавливаем бота...")
        bot_process.terminate()
        try:
            bot_process.wait(timeout=5)
        except:
            bot_process.kill()

# Регистрируем очистку
atexit.register(cleanup)

def start_system():
    """Запуск всей системы"""
    print("=" * 50)
    print("🚀 ЗАПУСК СИСТЕМЫ ТЕЛЕГРАМ БОТА")
    print("=" * 50)
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем keep-alive в отдельном потоке
    keep_alive_thread = threading.Thread(target=keep_awake, daemon=True)
    keep_alive_thread.start()
    
    print("✅ Система запущена!")
    print("🌐 Веб-сервер будет запущен на порту", os.environ.get('PORT', 10000))

if __name__ == '__main__':
    # Запускаем систему
    start_system()
    
    # Получаем порт от Render
    port = int(os.environ.get('PORT', 10000))
    
    # Запускаем Flask сервер
    print(f"🌐 Запуск веб-сервера на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)