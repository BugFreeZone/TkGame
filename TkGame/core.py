import tkinter as tk
import threading
import time
import os

try:
    from playsound import playsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class Game:
    def __init__(self, width=640, height=480, title="My Game"):
        self.width = width
        self.height = height
        self.title = title
        self.running = True
        self._game_thread = None

        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="black")
        self.canvas.pack()

        # Клавиатура
        self.root.bind("<KeyPress>", self._on_key_down)
        self.root.bind("<KeyRelease>", self._on_key_up)
        self.keys = set()

        # Мышь
        self.mouse_pos = (0, 0)
        self.mouse_buttons = set()
        self.mouse_events = []

        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<ButtonPress>", self._on_mouse_down)
        self.canvas.bind("<ButtonRelease>", self._on_mouse_up)

        # Кэш изображений и объектов canvas
        self._image_cache = {}
        self._draw_objects = {}

    # --- Обработка событий клавиатуры ---

    def _on_key_down(self, event):
        self.keys.add(event.keysym)

    def _on_key_up(self, event):
        self.keys.discard(event.keysym)

    # --- Обработка событий мыши ---

    def _on_mouse_move(self, event):
        self.mouse_pos = (event.x, event.y)
        self.mouse_events.append(('move', event.x, event.y))

    def _on_mouse_down(self, event):
        self.mouse_buttons.add(event.num)
        self.mouse_events.append(('down', event.num, event.x, event.y))

    def _on_mouse_up(self, event):
        self.mouse_buttons.discard(event.num)
        self.mouse_events.append(('up', event.num, event.x, event.y))

    def get_mouse_events(self):
        events = self.mouse_events[:]
        self.mouse_events.clear()
        return events

    # --- Основные методы ---

    def handle_events(self):
        """Обработка событий tkinter (обязательно вызывать каждый кадр)."""
        self.root.update_idletasks()
        self.root.update()

    def play_sound(self, filename, block=False):
        """Воспроизведение звука (wav, mp3)."""
        if not SOUND_AVAILABLE:
            print("playsound не установлен, звук не работает!")
            return
        if block:
            playsound(filename)
        else:
            threading.Thread(target=playsound, args=(filename,), daemon=True).start()

    def clear(self, color="black"):
        """Очистка экрана с заданным цветом фона (скрывает все объекты, но не удаляет их)."""
        self.canvas.configure(bg=color)
        for obj_id in self._draw_objects.values():
            self.canvas.itemconfigure(obj_id, state='hidden')

    def remove_all_objects(self):
        """Удаляет все графические объекты с холста и очищает кэш."""
        for obj_id in self._draw_objects.values():
            self.canvas.delete(obj_id)
        self._draw_objects.clear()

    # --- Встроенные функции отрисовки с кэшированием ---

    def draw_rect(self, name, x, y, w, h, color="white", width=1, fill=True):
        if name in self._draw_objects:
            obj_id = self._draw_objects[name]
            self.canvas.coords(obj_id, x, y, x+w, y+h)
            self.canvas.itemconfigure(obj_id, outline=color, width=width)
            self.canvas.itemconfigure(obj_id, fill=color if fill else "")
            self.canvas.itemconfigure(obj_id, state='normal')
        else:
            if fill:
                obj_id = self.canvas.create_rectangle(x, y, x+w, y+h, outline=color, fill=color, width=width)
            else:
                obj_id = self.canvas.create_rectangle(x, y, x+w, y+h, outline=color, width=width)
            self._draw_objects[name] = obj_id

    def draw_circle(self, name, x, y, r, color="white", width=1, fill=True):
        if name in self._draw_objects:
            obj_id = self._draw_objects[name]
            self.canvas.coords(obj_id, x-r, y-r, x+r, y+r)
            self.canvas.itemconfigure(obj_id, outline=color, width=width)
            self.canvas.itemconfigure(obj_id, fill=color if fill else "")
            self.canvas.itemconfigure(obj_id, state='normal')
        else:
            if fill:
                obj_id = self.canvas.create_oval(x-r, y-r, x+r, y+r, outline=color, fill=color, width=width)
            else:
                obj_id = self.canvas.create_oval(x-r, y-r, x+r, y+r, outline=color, width=width)
            self._draw_objects[name] = obj_id

    def draw_line(self, name, x1, y1, x2, y2, color="white", width=1):
        if name in self._draw_objects:
            obj_id = self._draw_objects[name]
            self.canvas.coords(obj_id, x1, y1, x2, y2)
            self.canvas.itemconfigure(obj_id, fill=color, width=width, state='normal')
        else:
            obj_id = self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
            self._draw_objects[name] = obj_id

    def draw_text(self, name, x, y, text, color="white", font=("Arial", 16), anchor="nw"):
        if name in self._draw_objects:
            obj_id = self._draw_objects[name]
            self.canvas.coords(obj_id, x, y)
            self.canvas.itemconfigure(obj_id, text=text, fill=color, font=font, state='normal')
        else:
            obj_id = self.canvas.create_text(x, y, text=text, fill=color, font=font, anchor=anchor)
            self._draw_objects[name] = obj_id

    def draw_image(self, name, x, y, filename, anchor="nw"):
        if not PIL_AVAILABLE:
            print("Pillow не установлен, отрисовка изображений не работает!")
            return
        if filename not in self._image_cache:
            if not os.path.exists(filename):
                print(f"Файл {filename} не найден!")
                return
            img = Image.open(filename)
            self._image_cache[filename] = ImageTk.PhotoImage(img)
        if name in self._draw_objects:
            obj_id = self._draw_objects[name]
            self.canvas.coords(obj_id, x, y)
            self.canvas.itemconfigure(obj_id, image=self._image_cache[filename], state='normal')
        else:
            obj_id = self.canvas.create_image(x, y, image=self._image_cache[filename], anchor=anchor)
            self._draw_objects[name] = obj_id

    # --- Игровой цикл и запуск ---

    def update(self):
        """Переопределять: логика игры."""
        pass

    def draw(self):
        """Переопределять: отрисовка."""
        self.clear()

    def flip(self):
        """Для совместимости, в tkinter не нужен."""
        pass

    def quit(self):
        """Завершить игру и закрыть окно."""
        self.running = False
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self, fps=60):
        """Запустить игровой цикл в отдельном потоке."""
        def game_loop():
            interval = 1.0 / fps
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.flip()
                time.sleep(interval)
            try:
                self.root.quit()
            except Exception:
                pass

        self._game_thread = threading.Thread(target=game_loop, daemon=True)
        self._game_thread.start()
        return self._game_thread
