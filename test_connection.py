import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="candidates_chat",
        user="candidates_chat",
        password="root",
        port=5432
    )
    print("✅ Подключение успешно!")
    conn.close()
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")