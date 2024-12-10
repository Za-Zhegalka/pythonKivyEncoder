from cryptography.fernet import Fernet
import mysql.connector

# База данных MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="crypto_db-copy"
)

cursor = db.cursor()

# Создание таблиц в базе данных
cursor.execute("""
CREATE TABLE IF NOT EXISTS encryption_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_text TEXT,
    encrypted_text TEXT,
    encryption_key BLOB
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS decryption_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    encrypted_text TEXT,
    decrypted_text TEXT,
    decryption_key BLOB
)
""")


# Функции шифрования и дешифрования
def generate_key():
    return Fernet.generate_key()

def encrypt(text, key):
    f = Fernet(key)
    encrypted_text = f.encrypt(text.encode())
    return encrypted_text, key

def decrypt(encrypted_text, key):
    f = Fernet(key)
    decrypted_text = f.decrypt(encrypted_text).decode()
    return decrypted_text

def log_action(username, action):
    cursor.execute("""
        INSERT INTO action_log (username, action)
        VALUES (%s, %s)
    """, (username, action))
    db.commit()