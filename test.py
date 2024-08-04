import traceback

try:
    # Ваш код, который может вызвать исключение
    result = 10 / 0
except Exception as e:
    print(traceback.format_exc())