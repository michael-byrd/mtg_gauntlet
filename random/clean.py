with open('input.txt', 'r') as f:
    lines = f.readlines()

for line in lines:
    if line != '\n' and "fill" not in line:
        print(line.strip())