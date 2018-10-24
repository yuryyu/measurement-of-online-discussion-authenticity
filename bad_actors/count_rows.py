file_path = "logs.txt"

with open(file_path, 'r') as f:
    text = f.read()
    text = text.replace('(', '')
    string_list = text.split('),')
    auth_id_list = []
    duplicates = []
    for string in string_list:
        auth_id = string.split(',')[0]
        if auth_id in auth_id_list:
            duplicates.append(auth_id)
        else:
            auth_id_list.append(auth_id)
    print duplicates
