from config import *
from sys import exit, argv
from threading import Thread
from time import sleep
from ui import MainWindow
from PyQt5.QtWidgets import QApplication
from soup import get_nbw_message

def update_table(window: MainWindow):

    # 首次获取信息，若没第一时间获取到则循环获取
    while True:
        window.message_list = get_nbw_message()
        if window.message_list:
            break
        sleep(UPDATE_INTERVAL)

    # 正确获取到信息，UI进行更新
    window.have_update = True
    window.populate_table()
    window.update()

    while True:
        
        # 等待<UPDATE_INTERVAL>后获取公文通信息
        sleep(UPDATE_INTERVAL)

        window.next_msg_list = get_nbw_message()

        if not window.next_msg_list:
            continue

        # 如果没更新则继续等待
        if window.next_msg_list[0][1] == window.message_list[0][1]:
            continue

        # 更新了就填充新表
        window.have_update = True
        window.message_list = window.next_msg_list
        window.populate_table()

def notice(window: MainWindow):
    while True:
        sleep(FLICKER_FREQUENCY)
        if not window.have_update:
            continue

        window.border_color = window.notice_color
        window.update()
        sleep(FLICKER_FREQUENCY)
        window.border_color = window.normal_color
        window.update()

if __name__ == '__main__':
    app = QApplication(argv)
    window = MainWindow()
    Thread(target=notice, args=(window,), daemon=True).start()
    Thread(target=update_table, args=(window,), daemon=True).start()
    # 获取主显示器分辨率
    screen_width = app.primaryScreen().geometry().width()
    screen_height = app.primaryScreen().geometry().height()

    # 获取屏幕信息并设置窗口宽高位置
    window_width = window.geometry().width()
    window_height = window.geometry().height()
    window.setGeometry(
        screen_width - window_width - 10, 
        screen_height//2 - 150, 
        window_width, 
        window_height
        )
    window.show()
    exit(app.exec_())
