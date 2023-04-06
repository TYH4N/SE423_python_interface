#!/usr/bin/env python

import socket
from time import sleep
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import RadioButtons, Button


TCP_IP = '192.168.1.72'
TCP_PORT = 10001
BUFFER_SIZE = 1024
MESSAGE = '123'
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

# while True:
#     s.send(MESSAGE.encode())
#     data = s.recv(BUFFER_SIZE).decode().split(' ')
#     x = data[0]
#     y = data[1]
#     theta = data[3]
#     print(x,y,theta)
#     sleep(0.2)
# s.close()
# print ("received data:", data)

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
plt.xlim(-15, 15)
plt.ylim(-15, 15)
points = []
line, = ax.plot(points, '.')

color_rax = plt.axes([0.05, 0.5, 0.1, 0.15])
color = 'blue'
rax = RadioButtons(color_rax, ('blue', 'green', 'red'))

def update_color(label):
    global color
    color = label
rax.on_clicked(update_color)

clear_ax = plt.axes([0.8, 0.9, 0.1, 0.075])
clear_button = Button(clear_ax, 'Clear')

def clear_points(event):
    global points
    points = []
    line.set_data(list(zip(*points)))
clear_button.on_clicked(clear_points)

stop_ax = plt.axes([0.9, 0.9, 0.1, 0.075])
stop_button = Button(stop_ax, 'Stop')

stop_flag = True
clear_flag = False
def stop_receiving(event):
    global stop_flag
    stop_flag = not stop_flag
    clear_flag = True
stop_button.on_clicked(stop_receiving)

def update_plot(frame):
    x = 0
    y = 0
    try:
        s.send(MESSAGE.encode())
        data = s.recv(BUFFER_SIZE).decode().split('\r\n')
        data = data[0].split(' ')
        print(data)
        if (len(data) > 4):
            x = data[0]
            y = data[1]
            theta = data[3]
            if stop_flag and data:
                point = [float(x), float(y)]
                if not clear_flag:
                    points.append(point)
                    line.set_data(list(zip(*points)))
                    line.set_color(color)
    except socket.timeout:
        pass

ani = FuncAnimation(fig, update_plot, frames=None, repeat=True, blit=False, interval=100)
plt.show()
