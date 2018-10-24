file_path = "logs.txt"

with open(file_path, 'r') as f:
    text = f.read()
    count = text.count('(')
    print count