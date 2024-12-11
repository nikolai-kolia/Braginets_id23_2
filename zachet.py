import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QSpinBox, QPushButton, QLabel
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QTimer

# Константы
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

class SolarEclipseSimulation(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Симуляция солнечного затмения")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Параметры анимации
        self.moon_radius = 30
        self.moon_position = -self.moon_radius  # Начальная позиция Луны
        self.speed = 1  # Скорость движения Луны

        # Таймер для анимации
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_moon_position)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.canvas = QWidget(self)
        layout.addWidget(self.canvas)

        # Слайдер для скорости Луны
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(1)
        self.speed_slider.valueChanged.connect(self.update_speed)

        # Спинбокс для радиуса Луны
        self.moon_radius_spinbox = QSpinBox()
        self.moon_radius_spinbox.setRange(10, 100)
        self.moon_radius_spinbox.setValue(self.moon_radius)
        self.moon_radius_spinbox.valueChanged.connect(self.update_moon_radius)

        # Слайдер для расстояния до Земли
        self.distance_slider = QSlider(Qt.Horizontal)
        self.distance_slider.setRange(10, 100)  # Изменяем диапазон для радиуса Луны
        self.distance_slider.setValue(self.moon_radius)  # Устанавливаем начальное значение равным радиусу Луны
        self.distance_slider.valueChanged.connect(self.update_distance)

        # Кнопка для запуска анимации
        start_button = QPushButton("Запустить анимацию")
        start_button.clicked.connect(self.start_animation)

        # Кнопка для сброса параметров
        reset_button = QPushButton("Сбросить параметры")
        reset_button.clicked.connect(self.reset_parameters)

        controls_layout = QVBoxLayout()

        controls_layout.addWidget(QLabel("Скорость движения Луны:"))
        controls_layout.addWidget(self.speed_slider)

        controls_layout.addWidget(QLabel("Радиус Луны:"))
        controls_layout.addWidget(self.moon_radius_spinbox)

        controls_layout.addWidget(QLabel("Расстояние между Луной и Землей:"))
        controls_layout.addWidget(self.distance_slider)

        controls_layout.addWidget(start_button)
        controls_layout.addWidget(reset_button)

        layout.addLayout(controls_layout)

        self.setLayout(layout)

    def update_speed(self):
        self.speed = self.speed_slider.value()  # Обновление скорости движения Луны

    def update_moon_radius(self):
        self.moon_radius = self.moon_radius_spinbox.value()  # Обновление радиуса Луны

    def update_distance(self):
        new_distance = self.distance_slider.value()  #Обновление расстояния до Земли и изменение размера Луны

        # Устанавливаем радиус Луны равным значению слайдера
        self.moon_radius = new_distance
        self.moon_radius_spinbox.setValue(new_distance)


    def start_animation(self):
        if not self.timer.isActive():
            self.moon_position = -self.moon_radius  # Сброс позиции Луны перед запуском
            self.timer.start(50)  # Обновляем каждую 50 миллисекунд


    def reset_parameters(self):
        # Сброс параметров и возврат Луны в начальное положение

        # Останавливаем таймер
        if self.timer.isActive():
            self.timer.stop()

        # Устанавливаем начальные значения
        self.moon_radius_spinbox.setValue(30)
        self.speed_slider.setValue(1)
        self.distance_slider.setValue(30)

        # Сбрасываем позицию Луны
        self.moon_position = -self.moon_radius

        # Перерисовываем окно
        self.update()


    def update_moon_position(self):
        # Обновление позиции Луны

        # Двигаем Луну вправо на заданную скорость
        if self.moon_position < WINDOW_WIDTH + self.moon_radius:
            self.moon_position += self.speed
        else:
            # Если Луна прошла экран, останавливаем анимацию и сбрасываем позицию
            self.timer.stop()
            # Запускаем анимацию заново при выходе за пределы окна
            self.start_animation()

        # Перерисовываем окно
        self.update()


    def paintEvent(self, event):
        # Отрисовка объектов на экране
        painter = QPainter(self)

        # Рисуем солнце
        painter.setBrush(QColor("yellow"))
        painter.drawEllipse(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 50, 100, 100)

        # Рисуем луну
        painter.setBrush(QColor("gray"))
        painter.drawEllipse(int(self.moon_position), WINDOW_HEIGHT // 2 - int(self.moon_radius),
                            int(self.moon_radius * 2), int(self.moon_radius * 2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SolarEclipseSimulation()
    window.show()
    sys.exit(app.exec_())
