import os

for x in range(1, 201):
    file_path = f"third_modules{os.path.sep}a{x}.py"
    with open(file_path, mode="wb") as f:
        f.write(f"class A{x}:\n    pass\n".encode())
