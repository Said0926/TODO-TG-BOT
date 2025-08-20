import sqlite3
from config import DB_PATH

# Инициализируем БД
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT,
                date TEXT,
                done INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f'[ERROR  init_db] {e}')
    finally:
        conn.close()
    

# Добавляем задачу в БД
def add_task(user_id, text, date):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'INSERT INTO tasks (user_id, text, date) VALUES (?, ?, ?)',
            (user_id, text, date)
        )
        conn.commit()
    except Exception as e:
        print(f'[ERROR add_task] {e}')
    finally:    
        conn.close()


# Получаем задачи с БД 
def get_tasks(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            SELECT id, text, date FROM tasks
            WHERE user_id = ? AND done = 0
            ORDER BY date
        ''', (user_id,))
        tasks = c.fetchall()
    except Exception as e:
        print(f'[ERROR get_tasks] {e}')
    finally:    
        conn.close()
        return tasks


# Отмечаем задачу выполненой 
def mark_done(task_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
                UPDATE tasks SET done = 1 WHERE id = ?
        ''', (task_id,))
        conn.commit()
    except Exception as e:
        print(f'[ERROR mark_task_done] {e}')
    finally:    
        conn.close()
    
# Удаляем задачу
def delete_task(task_id):
    try: 
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    except Exception as e:
        print(f'[ERROR delet_task] as {e}')
    finally:        
        conn.close()

# рудактируем задачу
def update_task_text(task_id, new_text):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE tasks SET text = ? WHERE id = ?', (new_text, task_id))
        conn.commit()
    except Exception as e:
        print(f'[ERROR update_task_text] {e}')
    finally:
        conn.close()
