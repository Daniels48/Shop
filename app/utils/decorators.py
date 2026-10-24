import traceback
from functools import wraps
import functools

def debug_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            print(f"[{func.__name__}] Вызвана ошибка:")
            traceback.print_exc()
    return wrapper


def handle_dialog(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        self.overlay_on()

        try:
            return func(self, *args, **kwargs)
        except Exception:
            traceback.print_exc()
        finally:
            self.overlay_off()
            self.focus_table()

    return wrapper
