import socket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, TextBox
import numpy as np

# Setting server address
TCP_IP = '192.168.1.69'
TCP_PORT = 10001
BUFFER_SIZE = 1024
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((TCP_IP, TCP_PORT))

# Initialize variables
stop_flag = False
clear_flag = False
refresh_interval = 10 # [ms]
Kp, Kd = 0, 0
color_dic = ['orange', 'purple']
golf_balls = []
obstacles = np.zeros([16, 16])
rx_data = ''

# Initialize plot
fig, ax = plt.subplots(figsize = [8,7.5])
plt.subplots_adjust(bottom = 0.1, right = 0.7)
plt.xlim(-7.0, 7.0)
plt.ylim(-5.0, 13.0)
ax.set_xticks(np.arange(-7,8,1))
ax.set_yticks(np.arange(-5,14,1))
ax.grid()
points = []
line, = ax.plot(points, '-')

# Initialize map
lx, ly = [2, 6, 6, -6, -6, -2], [0, 0, 12, 12, 0, 0]
plt.plot(lx, ly, color = 'brown')
circle1 = plt.Circle((-2, -4), 1, color = 'blue', fill = False)
circle2 = plt.Circle((2, -4), 1, color = 'orange', fill = False)
ax.add_patch(circle1)
ax.add_patch(circle2)
 
# Kp TextBox
input_box_1 = plt.axes([0.82, 0.7, 0.18, 0.05])
txt_box_1 = TextBox(input_box_1, "Kp ", color = 'white', hovercolor = '.9')
def change_value(data):
    Kp = data
    print('Kp changed to ', Kp)
txt_box_1.on_submit(change_value)
txt_box_1.set_val(' ')

# Kd TextBox
input_box_2 = plt.axes([0.82, 0.65, 0.18, 0.05])
txt_box_2 = TextBox(input_box_2, "Kd ",  color = 'white', hovercolor = '.9')
def change_value(data):
    Kd = data
    print('Kd changed to ', Kd)
txt_box_2.on_submit(change_value)
txt_box_2.set_val(' ')

# Golf ball TextBox
output_box_1 = plt.axes([0.82, 0.35, 0.18, 0.25])
txt_box_3 = TextBox(output_box_1, "Ball Loc ", color = 'white')

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

# Draw golf ball
def draw_golf():
    golf_text = 'x y color\n'
    for golf_ball in golf_balls:
        circle_golf = plt.Circle((golf_ball['x'], golf_ball['y']), 0.2, color = golf_ball['color'], fill = True)
        ax.add_patch(circle_golf)
        # Generate golf text for golf ball textbox
        golf_text = golf_text + str(round(golf_ball['x'],1)) + ' ' + str(round(golf_ball['y'],1)) + ' ' + golf_ball['color'] + '\n'
    # Set value to golf ball textbox
    txt_box_3.set_val(golf_text)

# Draw obstacle
def draw_obstacle():
    for i in range(11):
        for j in range(11):
            if (obstacles[i, j]):
                # Look for horizontal line
                if (obstacles[i + 1, j]):
                    ax.plot([i - 5, i - 4], [11 - j, 11 - j], color = 'red')
                # Look for vertical line
                if (obstacles[i, j + 1]):
                    ax.plot([i - 5, i - 5], [11 - j, 10 - j], color = 'red')
                # Corner cases
                if (i == 0):
                    ax.plot([i - 6, i - 5], [11 - j, 11 - j], color = 'red')
                if (i == 10):
                    ax.plot([i - 5, i - 4], [11 - j, 11 - j], color = 'red')
                if (j == 0):
                    ax.plot([i - 5, i - 5], [11 - j, 12 - j], color = 'red')
                if (j == 10):
                    ax.plot([i - 5, i - 5], [11 - j, 10 - j], color = 'red')

# Update thread
def update_plot(frame):
    # Edit tx data here
    tx_data = [0, 0, 0, 0, 0, 0, 0, 0]
    global rx_data
    try:
        # Fetch data and store in rx_data
        server.send(str(tx_data).encode())
        new_data = server.recv(BUFFER_SIZE).decode()
        rx_data = rx_data + new_data
        # Extract the first complete message 
        while '\r\n' in rx_data:
            split_data = rx_data.split('\r\n', 1)
            current_data = split_data[0].split(' ')
            rx_data = split_data[1]
            # print('rx: ', current_data)
            if (len(current_data) >= 8):
                # Process robot pose
                x = float(current_data[0])
                y = float(current_data[1])
                theta = float(current_data[2])
                if (not stop_flag):
                    point = [x, y]
                    if (not clear_flag):
                        points.append(point)
                        line.set_data(list(zip(*points)))
                        line.set_color('blue')
                # Process golf ball location
                golf_x = float(current_data[3])
                golf_y = float(current_data[4])
                golf_color = int(float(current_data[5]))
                if ((golf_color != -1) and (-6 < golf_x < 6) and (0 < golf_y < 12)):
                    new_ball_dict = dict(x = golf_x, y = golf_y, color = color_dic[golf_color if golf_color<=1 else 0])
                    if new_ball_dict not in golf_balls:
                        print('New ball: ', new_ball_dict)
                        golf_balls.append(new_ball_dict)
                        draw_golf()
                # Process obstacle location
                obstacle_x = int(float(current_data[6]))
                obstacle_y = int(float(current_data[7]))
                if ((obstacle_x in range(1, 11)) and (obstacle_y in range(1, 11))):
                    print('New obstacle point: ', obstacle_x, obstacle_y)
                    # print(obstacles)
                    obstacles[obstacle_x, obstacle_y] = 1
                    draw_obstacle()

    except socket.timeout:
        pass

# Start animation
animation = FuncAnimation(fig, update_plot, frames=None, repeat=True, blit=False, interval=refresh_interval)
plt.show()