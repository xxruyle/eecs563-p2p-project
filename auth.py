import hashlib
import os

hasher = hashlib.sha256()

def generate_auth_file(): 
    '''
    Generates an auth.txt file in the project root directory if it does not already exist 
    '''
    if not os.path.exists('auth.txt'): 
        with open('auth.txt', 'w') as f:
            pass

def store_username_and_password(username : str, password : str) -> bool:
    '''
    Stores username and password into the auth.txt file 
    The password is hashed using hashlib 
    Returns true if storing is successful, false otherwise 
    '''

    # checks to see if that username already exists in the auth.txt 
    with open('auth.txt', 'r') as f:
        for line in f: 
            name, pw = line.split('|')
            if name == username: 
                return False 

    hasher.update(password.encode('utf-8'))
    hashed_password = hasher.hexdigest()
    with open('auth.txt', 'w') as f:
        f.write(f'{username}|{hashed_password}\n')

    return True 



def is_authorized(username : str, password : str) -> bool: 
    '''
    Checks if a username or password exists in the auth.txt file 
    Returns true if username and password exists in the auth.txt, false otherwise
    '''
    hasher.update(password.encode('utf-8'))
    hashed_password = str(hasher.hexdigest())
    with open('auth.txt', 'r') as f:
        for line in f: 
            name, pw = line.split('|')
            if name.strip() == username and pw.strip() == hashed_password: 
                return True 

    return False
            
def register(): 
    '''
    Asks the user for a username and password 
    Uses store_username_and_password to store the user info in auth.txt
    '''
    while True: 
        username = input("Enter a username: ").strip()
        password = input("Enter a password: ").strip()
        res = store_username_and_password(username, password)
        if res: 
            return username 
        else: 
            print("Username already exists")

def login() -> str: 
    '''
    Asks the user for a username and password 
    Uses is_authorized to check if the uesrname and password is valid
    Return: username string 
    '''
    while True: 
        username = input("Enter a username: ").strip()
        password = input("Enter a password: ").strip()
        res = is_authorized(username, password)

        if res: 
            return username 
        else: 
            print("Login info does not exist. Register if you haven't already")







