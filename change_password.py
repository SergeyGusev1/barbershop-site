#!/usr/bin/env python3
"""Usage: python change_password.py <username> <new_password>"""
import sys
from database import SessionLocal, AdminUser
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def change_password(username, new_password):
    db = SessionLocal()
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user:
        print(f"Пользователь '{username}' не найден")
        db.close()
        return
    user.password_hash = pwd.hash(new_password)
    db.commit()
    db.close()
    print(f"Пароль для '{username}' успешно изменён")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Использование: python change_password.py <логин> <новый_пароль>")
        sys.exit(1)
    change_password(sys.argv[1], sys.argv[2])
