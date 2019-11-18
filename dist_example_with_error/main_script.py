import traceback
try:
    from some_modules import source_script
except Exception:
    traceback.print_exc()
    input("ERROR! Press Enter:")

if __name__ == '__main__':
    source_script.start()