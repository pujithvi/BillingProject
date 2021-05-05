import os

directory = os.getcwd()
for file in os.scandir(directory):
    if ((file.path.endswith('Log.txt') or (file.path.endswith('Bill.txt'))) and file.is_file()):
        os.remove(file.path)