from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    """Обработчик корневого URL."""
    return "Я работаю"

def run():
    """Запуск веб-сервера."""
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Запуск веб-сервера в отдельном потоке."""
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()