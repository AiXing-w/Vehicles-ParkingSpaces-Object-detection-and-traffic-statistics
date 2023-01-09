from client_window import Ui_MainWindow
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
import sys
import os
import datetime
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import multiprocessing as mp
import socket
from PIL import Image
from io import BytesIO


class client_window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        img_src = cv2.imread("background.jpg")  # 读取图像
        img_src = cv2.cvtColor(img_src, cv2.COLOR_BGR2RGB)  # 转换图像通道
        label_width = self.label.width()
        label_height = self.label.height()
        temp_imgSrc = QImage(img_src[:], img_src.shape[1], img_src.shape[0], img_src.shape[1] * 3, QImage.Format_RGB888)
        # 将图片转换为QPixmap方便显示
        self.pixmap_imgSrc = QPixmap.fromImage(temp_imgSrc).scaled(label_width, label_height)
        self.label.setPixmap(QPixmap(self.pixmap_imgSrc))
        self.pushButton.clicked.connect(self.request)

    def request(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 8000))
        sock.send(b'123')  # (b'GET / HTTP/1.1\r\nHost: 127.0.0.1:8000\r\n\r\n')
        data = sock.recv(4096)
        date, op, ep, cnt = data.decode().split(';')
        self.lineEdit.setText(date)
        self.lineEdit_2.setText(op)
        self.lineEdit_3.setText(ep)
        sock.close()
        cnt = int(cnt.strip())
        img_src = cv2.imread("background.jpg")  # 读取图像
        img_src = cv2.cvtColor(img_src, cv2.COLOR_BGR2RGB)  # 转换图像通道

        label_width = self.label.width()
        label_height = self.label.height()

        if cnt == 1:
            cv2.rectangle(img_src, (10, 10), (img_src.shape[0] // 2, img_src.shape[1] // 2), (255, 0, 0), 5)
            textx = (img_src.shape[0] // 2 - 15) // 3
            texty = (img_src.shape[1] // 2 - 50) // 3
            cv2.putText(img_src, "Best", (textx,texty), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
            cv2.putText(img_src, "Region", (textx - 15, texty + 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
        elif cnt == 2:
            cv2.rectangle(img_src, (img_src.shape[0] // 2, 0), (img_src.shape[0], img_src.shape[1] // 2 - 10), (255, 0, 0), 5)
            textx = img_src.shape[0] // 2 + (img_src.shape[0] // 2) // 3
            texty = (img_src.shape[1] // 2 - 50) // 3
            cv2.putText(img_src, "Best", (textx, texty), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
            cv2.putText(img_src, "Region", (textx - 15, texty + 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
        elif cnt == 3:
            cv2.rectangle(img_src, (10, img_src.shape[0] // 2), (img_src.shape[0] // 2, img_src.shape[1] - 10), (255, 0, 0), 5)
            textx = (img_src.shape[0] // 2 - 15) // 3
            texty = img_src.shape[0] // 2 + (img_src.shape[1] // 2 - 50) // 3
            cv2.putText(img_src, "Best", (textx, texty), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
            cv2.putText(img_src, "Region", (textx - 15, texty + 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)

        elif cnt == 4:
            cv2.rectangle(img_src, (img_src.shape[0] // 2, img_src.shape[1] // 2), (img_src.shape[0] - 10, img_src.shape[1] - 10), (255, 0, 0), 5)
            textx = img_src.shape[0] // 2 + (img_src.shape[0] // 2 - 15) // 3
            texty = img_src.shape[0] // 2 + (img_src.shape[1] // 2 - 50) // 3
            cv2.putText(img_src, "Best", (textx, texty), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
            cv2.putText(img_src, "Region", (textx - 15, texty + 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)


        temp_imgSrc = QImage(img_src[:], img_src.shape[1], img_src.shape[0], img_src.shape[1] * 3, QImage.Format_RGB888)
        # 将图片转换为QPixmap方便显示
        self.pixmap_imgSrc = QPixmap.fromImage(temp_imgSrc).scaled(label_width, label_height)
        self.label.setPixmap(QPixmap(self.pixmap_imgSrc))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = client_window()
    window.show()
    sys.exit(app.exec_())
