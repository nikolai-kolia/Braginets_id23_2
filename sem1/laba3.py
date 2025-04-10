import sys
import json
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSpinBox, QPushButton, QSlider, QDialog
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer
import math


# Функция для загрузки констант из JSON файла
def load_constants(filename):
    with open(filename) as f:
        return json.load(f)


# Функция для загрузки начального состояния из JSON файла
def load_initial_state(filename):
    with open(filename) as f:
        return json.load(f)


# Загрузка констант
try:
    constants = load_constants('constants.json')
except FileNotFoundError:
    print("Файл constants.json не найден.")
    sys.exit(1)

# Загрузка начального состояния
try:
    initial_state = load_initial_state('initial_state.json')
except FileNotFoundError:
    print("Файл initial_state.json не найден.")
    initial_state = {"frogs": []}  # Пустой список лягушек

# Константы для симуляции
FROG_JUMP_DISTANCE = constants["FROG_JUMP_DISTANCE"]
FROG_WEIGHT = constants["FROG_WEIGHT"]
LILY_PAD_STRENGTH = constants["LILY_PAD_STRENGTH"]
RIVER_SPEED = constants["RIVER_SPEED"]
LILY_PAD_Y_RANGE = tuple(constants["LILY_PAD_Y_RANGE"])
LILY_PAD_APPEAR_INTERVAL = constants["LILY_PAD_APPEAR_INTERVAL"]


class Frog:
    def __init__(self, weight=FROG_WEIGHT, jump_distance=FROG_JUMP_DISTANCE, position=0, y_position=300):
        self.position = position  # Позиция лягушки по оси x
        self.y_position = y_position  # Начальная фиксированная позиция по оси y для простоты
        self.path = []  # Хранит путь лягушки для визуализации
        self.weight = weight  # Вес лягушки
        self.jump_distance = jump_distance  # Максимальное расстояние прыжка

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
        self.position -= RIVER_SPEED  # Движение кувшинки вниз по течению с учетом скорости реки


class FrogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить новую лягушку")

        layout = QVBoxLayout()

        self.weight_input = QSpinBox()
        self.weight_input.setRange(1, FROG_WEIGHT * 2)
        self.weight_input.setValue(FROG_WEIGHT)

        self.jump_distance_input = QSpinBox()
        self.jump_distance_input.setRange(100, FROG_JUMP_DISTANCE * 2)
        self.jump_distance_input.setValue(FROG_JUMP_DISTANCE)

        layout.addWidget(QLabel("Введите вес лягушки:"))
        layout.addWidget(self.weight_input)
        layout.addWidget(QLabel("Введите максимальное расстояние прыжка:"))
        layout.addWidget(self.jump_distance_input)

        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.accept)  # Закрытие диалога при нажатии на кнопку "Добавить"

        layout.addWidget(add_button)

        self.setLayout(layout)

    def get_values(self):
        return self.weight_input.value(), self.jump_distance_input.value()


class RiverSimulation(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Симуляция прыжков лягушки")
        self.setGeometry(100, 100, 800, 600)

        # Создание лягушек из начального состояния
        self.frogs = [Frog(weight=frog['weight'], jump_distance=frog['jump_distance'],
                           position=frog['position'], y_position=frog['y_position'])
                      for frog in initial_state['frogs']]

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

        # Метка для отображения позиции лягушек
        self.label = QLabel("Позиции лягушек: {}".format([frog.position for frog in self.frogs]))
        layout.addWidget(self.label)

        # Слайдер для настройки скорости течения реки
        self.river_speed_slider = QSlider(Qt.Horizontal)
        self.river_speed_slider.setRange(1, 20)
        self.river_speed_slider.setValue(RIVER_SPEED)
        layout.addWidget(QLabel("Скорость течения реки:"))
        layout.addWidget(self.river_speed_slider)

        # Слайдер для настройки частоты появления кувшинок

        self.lily_pad_appear_interval_slider = QSlider(Qt.Horizontal)
        self.lily_pad_appear_interval_slider.setRange(100, 1000)
        self.lily_pad_appear_interval_slider.setValue(LILY_PAD_APPEAR_INTERVAL)
        layout.addWidget(QLabel("Частота появления кувшинок:"))
        layout.addWidget(self.lily_pad_appear_interval_slider)

        self.setLayout(layout)


    def create_lily_pad(self, position):
        y_position = random.randint(*LILY_PAD_Y_RANGE)
        return LilyPad(position, y_position)


    def add_lily_pad(self):
        new_position = random.randint(150, self.width() - 100)
        new_pad = LilyPad(new_position, random.randint(*LILY_PAD_Y_RANGE))
        self.lily_pads.append(new_pad)

    def update_simulation(self):
        global RIVER_SPEED

        RIVER_SPEED = self.river_speed_slider.value()  # Обновление скорости реки из слайдера

        for frog in list(self.frogs):
            target_pad = None

            for pad in list(self.lily_pads):
                pad.move()
                if pad.position < -10:
                    print(f"Кувшинкa на позиции {pad.position} удалена.")
                    self.lily_pads.remove(pad)

                distance_x = pad.position - frog.position
                distance_y = pad.y_position - frog.y_position

                distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
                if distance <= frog.jump_distance:
                    if target_pad is None or distance < math.sqrt((target_pad.position - frog.position) ** 2 + (
                            target_pad.y_position - frog.y_position) ** 2):
                        target_pad = pad

            if target_pad:
                if frog.weight > target_pad.strength:
                    print(f"Кувшинкa на позиции {target_pad.position} потонула!")
                    self.lily_pads.remove(target_pad)

                # Прыжок лягушки
                new_position = target_pad.position
                new_y_position = target_pad.y_position

                # Проверка на выход за границы
                if new_position >= 0 and new_position <= self.width():
                    frog.jump(new_position, new_y_position)
                    target_pad.strength -= frog.weight

                    # Обновление метки и перерисовка окна
                    positions = [frog.position for frog in self.frogs]
                    self.label.setText("Позиции лягушек: {}".format(positions))
                else:
                    print(f"Лягушка не может прыгнуть на позицию {new_position}, выходящую за границы.")

        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setBrush(QColor(139, 69, 19))
        painter.drawRect(0, 0, self.width(), 50)
        painter.drawRect(0, self.height() - 50, self.width(), 50)

        for pad in self.lily_pads:
            painter.setBrush(QColor(0, 255, 0))
            painter.drawRect(pad.position, pad.y_position - 25, 50, 20)

        painter.setBrush(QColor(255, 0, 0))

        for frog in self.frogs:
            painter.drawEllipse(frog.position - 15,
                                (self.height() // 2) - 30 + (frog.y_position - (self.height() // 2)),
                                30,
                                30)

        pen = QPen(QColor(0, 0, 255))
        pen.setWidth(2)
        painter.setPen(pen)

        for frog in self.frogs:
            for i in range(len(frog.path) - 1):
                start_x, start_y = frog.path[i]
                end_x, end_y = frog.path[i + 1]
                painter.drawLine(start_x - 15, start_y - 30,
                                 end_x - 15, end_y - 30)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            mouse_x = event.x()
            mouse_y = event.y()

            for pad in self.lily_pads:
                if pad.position <= mouse_x <= pad.position + 50 and \
                        pad.y_position - 25 <= mouse_y <= pad.y_position:
                    print("Клик попал на кувшинку.")
                    return self.prompt_add_frog(pad)
        print("Клик не попал на кувшинку.")


    def prompt_add_frog(self, pad):
        dialog = FrogDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            weight, jump_distance = dialog.get_values()
            return self.add_frog(weight, jump_distance, pad)


    def add_frog(self, weight, jump_distance, pad):
        new_frog = Frog(weight=weight, jump_distance=jump_distance)
        new_frog.jump(pad.position + 25, pad.y_position)
        print(
            f"Добавлена новая лягушка с весом {new_frog.weight} и максимальным расстоянием прыжка {new_frog.jump_distance}.")

        # Добавляем новую лягушку в список всех лягушек.
        self.frogs.append(new_frog)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    simulation = RiverSimulation()
    simulation.show()

    sys.exit(app.exec_())