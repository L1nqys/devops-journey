from flask import Flask
import psycopg2
import time

app = Flask(__name__)

# Настройки подключения. Обрати внимание на host!
DB_SETTINGS = {
    "dbname": "devops_db",
    "user": "linqy",
    "password": "supersecret123",
    "host": "db",  # Docker свяжет это имя с нужным контейнером
    "port": "5432"
}

def get_hit_count():
    # Лайфхак: база данных при старте контейнера может инициализироваться пару секунд.
    # Если питон попытается подключиться мгновенно, он упадет с ошибкой.
    # Этот цикл просто делает 10 попыток подключения с паузой в 1 секунду.
    for _ in range(10):
        try:
            conn = psycopg2.connect(**DB_SETTINGS)
            break
        except psycopg2.OperationalError:
            time.sleep(1)
            
    cursor = conn.cursor()
    
    # Автоматически создаем таблицу, если её еще нет в базе
    cursor.execute("CREATE TABLE IF NOT EXISTS counter_table (id SERIAL PRIMARY KEY, hits INT NOT NULL);")
    # Вставляем стартовый ноль, если таблица пустая
    cursor.execute("INSERT INTO counter_table (hits) SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM counter_table WHERE id = 1);")
    # Делаем +1 к просмотрам
    cursor.execute("UPDATE counter_table SET hits = hits + 1 WHERE id = 1;")
    conn.commit()
    
    # Забираем актуальную цифру
    cursor.execute("SELECT hits FROM counter_table WHERE id = 1;")
    hits = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    return hits

@app.route('/')
def hello():
    try:
        count = get_hit_count()
        return f"""
        <html>
            <head><title>Docker Compose Practice</title></head>
            <body style="text-align: center; font-family: Arial; margin-top: 100px; background-color: #e8f4f8;">
                <h1 style="color: #2c3e50;">L1nqys DevOps Journey: Docker Compose</h1>
                <div style="background: white; display: inline-block; padding: 20px 50px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p style="font-size: 20px; color: #7f8c8d; margin: 0;">Количество просмотров страницы:</p>
                    <span style="font-size: 72px; font-weight: bold; color: #3498db;">{count}</span>
                </div>
                <p style="color: #bdc3c7; margin-top: 20px;">Полностью автоматизировано через Docker Compose 🚀</p>
            </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Ошибка подключения к Базе Данных внутри Docker!</h1><p>{str(e)}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
