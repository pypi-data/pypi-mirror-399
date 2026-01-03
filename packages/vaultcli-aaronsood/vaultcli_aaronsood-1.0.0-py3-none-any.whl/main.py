import string
import sys
import random
import bcrypt
import base64, json, os
import pyperclip
import time
import threading
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

USERS_FILE = "users.json"

# setup
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)


if os.name == "nt":
    import msvcrt
else:
    import tty
    import termios

def input_masked(prompt=""):
    print(prompt, end="", flush=True)
    buf ="" 
    if os.name == "nt":
        while True:
            ch = msvcrt.getch()
            if ch in {b'\r', b'\n'}:
                print()
                break
            elif ch == b'\x08':
                if buf:
                    buf = buf[:-1]
                    print ("\b \b", end="", flush=True)
            elif ch == b'\x03':
             raise KeyboardInterrupt
            else:
             buf += ch.decode()
             print("*", end="", flush=True)
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in "\r\n":
                    print()
                    break
                elif ch == "\x03":
                    raise KeyboardInterrupt
                else:
                    buf += ch
                    print("*", end="", flush=True)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return buf


last_activity = time.time()
lock_timeout = 300
vault_locked = False

def reset_activity():
     global last_activity
     last_activity = time.time()
    
def auto_lock_monitor():
     global vault_locked
     while True:
          time.sleep(1)
          if not vault_locked and time.time() - last_activity > lock_timeout:
               vault_locked = True
               print("\nVault auto-locked due to inactivity.")
threading.Thread(target=auto_lock_monitor, daemon=True).start()

# key derivation
def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

def load_or_create_salt(username):
    salt_file = f"{username}_vault.salt"
    if os.path.exists(salt_file):
        return open(salt_file, "rb").read()
    
    salt = os.urandom(16)
    open(salt_file, "wb").write(salt)
    return salt

def get_fernet(username, master_password):
    salt = load_or_create_salt(username)
    key = derive_key(master_password, salt)
    return Fernet(key)

def get_vault_file(username):
    return f"vault_{username}.json"


def load_vault(username, fernet):
    vault_file = get_vault_file(username)   

    if not os.path.exists(vault_file):
        return {}
    
    with open(vault_file, "r") as f:
        encrypted = f.read().strip()
    
    if not encrypted:
        return {}
    
    decrypted = fernet.decrypt(encrypted.encode()).decode()
    return json.loads(decrypted)

def save_vault(username, vault, fernet):
    vault_file = get_vault_file(username)
    encrypted = fernet.encrypt(json.dumps(vault).encode()).decode()

    with open(vault_file, "w") as f:
        f.write(encrypted)
# auth

def signup():
    
    username = input("Create username: ")
    master_password = input_masked("Create master password: ")

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if username in users:
        print("Username already taken. Try another one")
        return None
    
    hashed = bcrypt.hashpw(master_password.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent = 2)
    
    save_vault(username, {}, get_fernet(username, master_password))

    print(f"User '{username}' created.")
    return username, master_password


def login():
    with open("users.json", "r") as f:
        users = json.load(f)

    if not users:
        print("No users found. Please create an account.")
        return signup()
    
    username = input("Username: ")
    master_password = input_masked("Master password: ")
    
    if username not in users:
        print("User not found")
        return None
    
    stored_hash = users[username].encode("utf-8")

    if not bcrypt.checkpw(master_password.encode(), stored_hash):
        print("Incorrect password.")
        return None
    
    print(f"Welcome, {username}.")
    return username, master_password
    
def password_strength(password: str) -> str:
    score = 0
    length = len(password)

    if length >= 8:
            score += 1
    if length >= 12:
            score += 1
        
    if any(c.islower() for c in password):
            score +=1
    if any(c.isupper() for c in password):
         score +=1
    if any(c.isdigit() for c in password):
            score +=1
    if any(c in "!@#$%^&*()-_+=<>?" for c in password):
            score +=1

    if score <= 2:
            return "Weak"
    elif score <=4:
            return "Medium"
    else:
            return "Strong"

# password generator 
def generate_password():
    length = int(input("Password length: "))
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_+=<>?"
    pw = "".join(random.choice(chars) for _ in range(length))
    strength = password_strength(pw)
    print(f"Generated: {pw}")
    print(f"Password Strength: {strength}")
    return pw
  


def add_password(username, fernet):
    vault =load_vault(username, fernet)

    site = input("Site: ").lower()
    pw = input("Enter password (leave blank to auto-generate): ") 

    if not pw:
        pw = generate_password()
        print("Generated:", pw)
    else:
        strength = password_strength(pw)
        print(f"Password strength: {strength}")

    vault[site] = pw
    save_vault(username, vault, fernet)
    
    print ("Saved.")

def get_password(username, fernet):
    vault = load_vault(username, fernet)
    site = input("Site: ").lower()

    if site in vault:
        pw = vault[site]    
        print("Password:", pw)
        pyperclip.copy(pw)
        print("(Copied to clipboard)")
    else:
        print("No entry found.")

def list_passwords(username, fernet):
    vault = load_vault(username, fernet)

    if not vault:
        print("Vault is empty.")
        return
    for site in vault:
        print("-", site)

def delete_password(username, fernet):
    vault = load_vault(username, fernet)
    site = input("Site to delete: ")

    if site in vault:
        del vault[site]
        save_vault(username, vault, fernet)
        print("Deleted.")
    else:
        print("Not found.")




def main():
    global vault_locked 

    auth = login()
    if not auth:
        return
    username, master_password = auth
    fernet = get_fernet(username, master_password)
    vault_locked = False


    while True:
        reset_activity()
        print("""
1. Add password
2. Get password
3. List passwords
4. Delete password
5. Generate password
6. Exit
        """)
        c = input("> ")
        reset_activity()

        if vault_locked:
            print("Vault is locked. Please re-enter your master password.")
            auth = login()
            if not auth:
                continue
            username, master_password = auth
            fernet = get_fernet(username, master_password)
            vault_locked = False
            continue

        if c == "1":
            add_password(username, fernet)
        elif c == "2":
            get_password(username, fernet)
        elif c == "3":
            list_passwords(username, fernet)
        elif c == "4":
            delete_password(username, fernet)
        elif c == "5":
            print(generate_password())
        elif c == "6":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()