import sys
import json
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer
import math

# Константы для симуляции
FROG_JUMP_DISTANCE = 300  # Максимальное расстояние прыжка лягушки
FROG_WEIGHT = 10  # Вес лягушки
LILY_PAD_STRENGTH = 15  # Прочность кувшинок
RIVER_SPEED = 5  # Скорость течения реки
LILY_PAD_Y_RANGE = (100, 400)  # Диапазон для y-позиций кувшинок
LILY_PAD_APPEAR_INTERVAL = 200  # Интервал времени в миллисекундах для появления новой кувшинки


class Frog:
    def __init__(self):
        self.position = 0  # Позиция лягушки по оси x
        self.y_position = (300)  # Начальная фиксированная позиция по оси y для простоты
        self.path = []  # Хранит путь лягушки для визуализации

    def jump(self, target_position, target_y_position):
        self.position = target_position
        self.y_position = target_y_position
        self.path.append((self.position, self.y_position))


class LilyPad:
    def __init__(self, position, y_position):
        self.position = position  # Позиция кувшинки по оси x
        self.y_position = y_position  # Позиция кувшинки по оси y
        self.strength = random.randint(5, 20)  # Случайная прочность между 5 и 20

    def move(self):
        self.position -= RIVER_SPEED # Движение кувшинки вниз по течению с учетом скорости реки


class RiverSimulation(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Симуляция прыжков лягушки")
        self.setGeometry(100, 100, 800, 600)

        self.frog = Frog()
        self.lily_pads = [self.create_lily_pad(i * 150) for i in range(5)]  # Создание начальных кувшинок

        # Таймер для обновления симуляции и появления кувшинок
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(100)  # Обновление каждые 100 мс

        # Таймер для создания новых кувшинок
        self.lily_pad_timer = QTimer()
        self.lily_pad_timer.timeout.connect(self.add_lily_pad)
        self.lily_pad_timer.start(LILY_PAD_APPEAR_INTERVAL)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Позиция лягушки: {}".format(self.frog.position))
        layout.addWidget(self.label)
        self.setLayout(layout)

    def create_lily_pad(self, position):
        y_position = random.randint(*LILY_PAD_Y_RANGE)  # Случайная позиция y в заданном диапазоне
        return LilyPad(position, y_position)

    def add_lily_pad(self):
        # Добавление новой кувшинки на случайной позиции по оси x
        new_position = random.randint(0, self.width() - 100)
        new_pad = LilyPad(new_position, random.randint(*LILY_PAD_Y_RANGE))
        self.lily_pads.append(new_pad)

    def update_simulation(self):
        target_pad = None

        # Движение существующих кувшинок вниз по течению и их удаление при выходе за границы экрана
        for pad in list(self.lily_pads):  # Используем список для избежания модификации во время итерации
            pad.move()
            if pad.position < -100:  # Удаление кувшинок за пределами экрана
                print(f"Кувшинкa на позиции {pad.position} удалена.")
                self.lily_pads.remove(pad)

            # Проверка на отрицательную позицию перед добавлением в список (если требуется)
            if pad.position < 0:
                print(f"Кувшинкa на позиции {pad.position} ушла за пределы экрана и будет удалена.")
                continue

            # Вычисление расстояния от лягушки до каждой кувшинки с учетом координат x и y
            distance_x = pad.position - self.frog.position
            distance_y = pad.y_position - self.frog.y_position

            distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
            if distance <= FROG_JUMP_DISTANCE:
                if target_pad is None or distance < math.sqrt((target_pad.position - self.frog.position) ** 2 + (
                        target_pad.y_position - self.frog.y_position) ** 2):
                    target_pad = pad

        if target_pad:
            if FROG_WEIGHT > target_pad.strength:
                print(f"Кувшинкa на позиции {target_pad.position} потонула!")
                self.lily_pads.remove(target_pad)  # Удаление кувшинки, если она тонет

            # Прыжок к целевой кувшинке и уменьшение ее прочности
            self.frog.jump(target_pad.position, target_pad.y_position)
            target_pad.strength -= FROG_WEIGHT

            # Обновление метки и перерисовка окна
            self.label.setText("Позиция лягушки: {}".format(self.frog.position))
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Рисование берегов реки
        painter.setBrush(QColor(139, 69, 19))  # Коричневый цвет для берегов
        painter.drawRect(0, 0, self.width(), 50)  # Верхний берег
        painter.drawRect(0, self.height() - 50, self.width(), 50)  # Нижний берег

        # Рисование кувшинок на их позициях по оси y
        painter.setBrush(QColor(0, 255, 0))  # Зеленый цвет для кувшинок
        for pad in self.lily_pads:
            painter.drawRect(pad.position, pad.y_position - 25, 50, 20)

        # Рисование лягушки как эллипса на текущей позиции и y-позиции
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(self.frog.position - 15,
                            (self.height() // 2) - 30 + (self.frog.y_position - (self.height() // 2)),
                            30,
                            30)

        # Рисование пути лягушки с линиями между прыжками
        pen = QPen(QColor(0, 0, 255))
        pen.setWidth(2)
        painter.setPen(pen)

        for i in range(len(self.frog.path) - 1):
            start_x, start_y = self.frog.path[i]
            end_x, end_y = self.frog.path[i + 1]
            painter.drawLine(start_x - 15, start_y - 30, end_x - 15, end_y - 30)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        with open('initial_state.json') as f:
            initial_state = json.load(f)
            print("Загружено начальное состояние:", initial_state)
    except FileNotFoundError:
        with open('initial_state.json', 'w') as f:
            json.dump({"frog_position": 0}, f)
            print("Создано начальное состояние с значениями по умолчанию.")

    simulation = RiverSimulation()
    simulation.show()

    sys.exit(app.exec_())