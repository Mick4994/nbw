from bcode import base_code
from base64 import b64decode
from config import *
from PIL import Image
from io import BytesIO
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QMessageBox, QLabel
from PyQt5.QtCore import Qt, QUrl, QPropertyAnimation, QRect, QCoreApplication
from PyQt5.QtGui import QDesktopServices, QPainter, QColor, QMouseEvent, QImage, QPixmap

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 逻辑变量
        self._startPos = None
        self._wmGap = None
        self.hidden = False
        self.have_update = False

        # 提醒闪烁的颜色
        self.normal_color = QColor(123, 123, 150, 123)
        self.notice_color = QColor(255, 0, 0, 123)
        self.border_color = self.normal_color

        # 获取屏幕大小
        dsk = QApplication.primaryScreen()
        self.screen_width = dsk.geometry().width()
        self.screen_height = dsk.geometry().height()

        # 窗体大小
        self.window_width = 605
        self.window_height = 275 + 20

        img_data = b64decode(base_code)
        image = Image.open(BytesIO(img_data))
        qimage = self.convert_image_to_qimage(image)
        label = QLabel(self)
        label.setPixmap(QPixmap.fromImage(qimage))
        label.setGeometry(20, 10, self.window_width, self.window_height)

        # 设置窗口透明度
        self.setWindowOpacity(0.8)
        self.setStyleSheet("""
                           border-radius: 10px;
                           border: 2px groove gray;
                           border-style: outset;
                           """)
        self.setWindowTitle('公文通桌面显示')

        # 设置窗口大小固定
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.window_width, self.window_height)

        # 创建表格控件
        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(10, 10, self.window_width - 20, self.window_height - 20)

        # 设置表格行列数
        self.table_widget.setRowCount(MAX_ROW)
        self.table_widget.setColumnCount(2)

        # 设置表格头部标签
        self.table_widget.verticalHeader().setFixedWidth(30)

        # 去掉列的表头
        self.table_widget.horizontalHeader().setVisible(False)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)

        # 设置为固定不可修改(防止小天才)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.message_list = []
        self.next_msg_list = []

        # 设置表格样式
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 128);
                border: none;
            }
                                                                    
            QTableWidget::item {
                border: 1px solid gray;
                background-color: rgba(255, 255, 255, 128);
            }
            
            QTableWidget::item:selected {
                background-color: rgba(245, 245, 245, 128);
            }
            
            QHeaderView::section {
                border: 1px solid gray;
                background-color: rgba(249, 249, 249, 128);
                padding: 5px;
                font-weight: bold;
            }
        """)

        self.table_widget.cellClicked.connect(self.open_url)
        self.how_to_use = """
            刚启动时默认有新消息，窗口会红灰交替，鼠标移到窗口闪烁消失
            所以闪烁代表公文通有新消息，之后有新消息也是
            鼠标移开，窗口会被吸入屏幕侧边收起窗体，留窗体边缘
            若有闪烁即有新消息，把鼠标移到窗体边缘，窗体会再次展开
            点击标题，会用默认浏览器打开该公文通超链接
            每20分钟获取一次公文通
            请关闭梯子使用
            高缩放的Windows桌面会有显示不全
            右键窗体边缘可以退出程序          ----made by Mick4994
        """
        QMessageBox.information(self, '使用须知', self.how_to_use, QMessageBox.Yes, QMessageBox.Yes)

    def convert_image_to_qimage(self, image):
        # 获取图像属性
        width, height = image.size
        format = QImage.Format_RGB888 if image.mode == "RGB" else QImage.Format_RGBA8888

        # 将 Image 对象转换成 QImage 对象
        qimage = QImage(image.tobytes(), width, height, format)
        
        return qimage

    def populate_table(self):
        """
        按消息列表在ui中的表逐个按行填充，第一列为来源的办公室，第二列为消息标题超链接
        """

        # if self.message_list:
        #     QMessageBox.information(self, '公文通更新啦!', f'{self.message_list[0][1]}', QMessageBox.Yes, QMessageBox.Yes)

        for index, row in zip(range(MAX_ROW), self.message_list):

            # 设置每行高度
            self.table_widget.setRowHeight(index, 20)

            # 设置来源办公室
            item = QTableWidgetItem(row[0])
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)  # 设置为只读
            self.table_widget.setItem(index, 0, item)

            # 设置标题
            item = QTableWidgetItem(row[1])
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)  # 设置为只读
            self.table_widget.setItem(index, 1, item)

        # 设置第一列宽度为 150 个字符宽度
        self.table_widget.setColumnWidth(0, 150)

        # 设置第二列宽度为 400 个字符宽度
        self.table_widget.setColumnWidth(1, 400)

    def open_url(self, row, column):
        # 检查点击的列是否是链接列
        if column == 1:
            url = self.message_list[row][2]
            # 使用默认浏览器打开链接
            QDesktopServices.openUrl(QUrl(url))

    def paintEvent(self, event):
        """GUI绘制的回调"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 设置半透明效果
        painter.setOpacity(0.8)
        painter.setBrush(self.border_color)
        painter.drawRoundedRect(self.rect(), 20, 20)

    def enterEvent(self, event):
        """鼠标进入的回调"""
        self.hide_or_show('show', event)
        self.have_update = False

    def leaveEvent(self, event):
        """鼠标离开的回调"""
        self.hide_or_show('hide', event)

    def hide_or_show(self, mode, event, outside = False):
        # 获取窗口左上角x,y
        pos = self.frameGeometry().topLeft()
        if mode == 'show' and self.hidden:
            # 窗口左上角x + 窗口宽度 大于屏幕宽度，从右侧滑出
            if pos.x() + self.window_width >= self.screen_width:
                # 需要留10在里边，否则边界跳动
                self.startAnimation(self.screen_width - self.window_width, pos.y())
            # 窗口左上角x 小于0, 从左侧滑出
            elif pos.x() <= 0:
                self.startAnimation(0, pos.y())
            # 窗口左上角y 小于0, 从上方滑出
            elif pos.y() <= 0:
                self.startAnimation(pos.x(), 0)
            self.hidden = False
        elif mode == 'hide' and (not self.hidden):
            if pos.x() + self.window_width + 20 >= self.screen_width:
                # 留10在外面
                self.startAnimation(self.screen_width - 10, pos.y(), mode, 'right')
            elif pos.x() <= 0:
                # 留10在外面
                self.startAnimation(10 - self.window_width, pos.y(), mode, 'left')
            elif pos.y() <= 0:
                # 留10在外面
                self.startAnimation(pos.x(), 10 - self.window_height, mode, 'up')
            self.hidden = True
        if not outside:
            event.accept()

    def startAnimation(self, x, y, mode='show', direction=None):
        animation = QPropertyAnimation(self, b"geometry", self)
        # 滑出动画时长
        animation.setDuration(200)
        # 隐藏时，只留10在外边，防止跨屏
        # QRect限制其大小，防止跨屏
        num = QApplication.desktop().screenCount()
        if mode == 'hide':
            if direction == 'right':
                animation.setEndValue(QRect(x, y, 10, self.window_height))
            elif direction == 'left':
                # 多屏时采用不同的隐藏方法，防止跨屏
                if num < 2:
                    animation.setEndValue(QRect(x, y, self.window_width, self.window_height))
                else:
                    animation.setEndValue(QRect(0, y, 10, self.window_height))
            else:
                if num < 2:
                    animation.setEndValue(QRect(x, y, self.window_width, self.window_height))
                else:
                    animation.setEndValue(QRect(x, 0, self.window_width, 10))
        else:
            animation.setEndValue(QRect(x, y, self.window_width, self.window_height))
        animation.start()

    def mouseMoveEvent(self, event: QMouseEvent):
        self._wmGap = event.pos() - self._startPos
        # 移动窗口，保持鼠标与窗口的相对位置不变
        # 检查是否移除了当前主屏幕
        # 左方界限
        final_pos = self.pos() + self._wmGap
        if self.frameGeometry().topLeft().x() + self._wmGap.x() <= 0:
            final_pos.setX(0)
        # 上方界限
        if self.frameGeometry().topLeft().y() + self._wmGap.y() <= 0:
            final_pos.setY(0)
        # 右方界限
        if self.frameGeometry().bottomRight().x() + self._wmGap.x() >= self.screen_width:
            final_pos.setX(self.screen_width - self.window_width)
        # 下方界限
        if self.frameGeometry().bottomRight().y() + self._wmGap.y() >= self.screen_height:
            final_pos.setY(self.screen_height - self.window_height)
        self.move(final_pos)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._startPos = event.pos()
        if event.button() == Qt.RightButton:
            # 创建右键菜单
            menu = QMenu(self)
            menu.setStyleSheet(u"background-color: white;\n"
                               "selection-color: rgb(0, 255, 127);\n"
                               "selection-background-color: gray;\n"
                               "font: 8pt;")
            # 二级菜单
            size_menu = menu.addMenu('Bkcolor')
            light_gray = size_menu.addAction('Light-Gray')
            gray = size_menu.addAction('Gray')
            black = size_menu.addAction('Black')

            # 普通菜单
            quit_action = menu.addAction('Exit')
            # 窗口定位到鼠标处
            action = menu.exec_(self.mapToGlobal(event.pos()))

            # 改变背景色
            if action == light_gray:
                self.setStyleSheet(u"background-color: rgb(100, 100, 100)")
            if action == gray:
                self.setStyleSheet(u"background-color: rgb(50, 50, 50)")
            if action == black:
                self.setStyleSheet(u"background-color: black")

            if action == quit_action:
                QCoreApplication.quit()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._startPos = None
            self._wmGap = None
        if event.button() == Qt.RightButton:
            self._startPos = None
            self._wmGap = None