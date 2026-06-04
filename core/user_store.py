users = {}

def get_user(phone):
    return users.get(phone)

def save_user(phone, program, level):
    users[phone] = {
        "program": program,
        "level": level
    }