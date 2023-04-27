import socket
from time import sleep
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import RadioButtons, Button, TextBox
import numpy as np

# Setting server address
TCP_IP = '192.168.1.69'
TCP_PORT = 10001
BUFFER_SIZE = 1024
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.connect((TCP_IP, TCP_PORT))

# Initialize variables
stop_flag = False
clear_flag = False
refresh_interval = 100 # [ms]
Kp, Kd = 0, 0

# Initialize plot
fig, ax = plt.subplots(figsize = [8,7.5])
plt.subplots_adjust(bottom = 0.1, right = 0.7)
plt.xlim(-7.0, 7.0)
plt.ylim(-5.0, 13.0)
ax.set_xticks(np.arange(-7,8,1))
ax.set_yticks(np.arange(-5,14,1))
ax.grid()
points = []
line, = ax.plot(points, '.')

# Initialize map
lx, ly = [2, 6, 6, -6, -6, -2], [0, 0, 12, 12, 0, 0]
plt.plot(lx, ly, color = 'brown')
circle1 = plt.Circle((-2, -4), 1, color = 'blue', fill = False)
circle2 = plt.Circle((2, -4), 1, color = 'orange', fill = False)
ax.add_patch(circle1)
ax.add_patch(circle2)
 
# Kp TextBox
input_box_1 = plt.axes([0.85, 0.7, 0.15, 0.05])
txt_box_1 = TextBox(input_box_1, "Kp ", color = 'white', hovercolor = '.9')
def change_value(data):
    Kp = data
    print("Kp changed to", Kp)
txt_box_1.on_submit(change_value)
txt_box_1.set_val(' ')

# Kd TextBox
input_box_2 = plt.axes([0.85, 0.65, 0.15, 0.05])
txt_box_2 = TextBox(input_box_2, "Kd ",  color = 'white', hovercolor = '.9')
def change_value(data):
    Kd = data
    print("Kd changed to", Kd)
txt_box_2.on_submit(change_value)
txt_box_2.set_val(' ')

# Define clear widget
clear_ax = plt.axes([0.8, 0.9, 0.1, 0.1])
clear_button = Button(clear_ax, 'Clear', color = 'white', hovercolor = '.8')
def clear_points(event):
    global points
    points = []
    line.set_data(list(zip(*points)))
clear_button.on_clicked(clear_points)

# Define stop widget
stop_ax = plt.axes([0.9, 0.9, 0.1, 0.1])
stop_button = Button(stop_ax, 'Stop', color = 'white', hovercolor = '.8')
def stop_receiving(event):
    global stop_flag
    stop_flag = not stop_flag
    clear_flag = True
stop_button.on_clicked(stop_receiving)

# Update thread
def update_plot(frame):
    x = 0
    y = 0
    tx_data = [0, 0, 0, 0, 0, 0, 0, 0]
    try:
        server.send(tx_data.encode())
        rx_data = server.recv(BUFFER_SIZE).decode().split('\r\n')
        rx_data = rx_data[0].split(' ')
        print(rx_data)
        if (len(rx_data) > 4):
            x = rx_data[0]
            y = rx_data[1]
            theta = rx_data[3]
            if (not stop_flag):
                point = [float(x), float(y)]
                if (not clear_flag):
                    points.append(point)
                    line.set_data(list(zip(*points)))
                    line.set_color(color)
    except socket.timeout:
        pass

animation = FuncAnimation(fig, update_plot, frames=None, repeat=True, blit=False, interval=refresh_interval)
plt.show()