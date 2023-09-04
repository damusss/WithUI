import pathlib, os

path = pathlib.Path(os.getcwd())

print(os.listdir(str(path)))