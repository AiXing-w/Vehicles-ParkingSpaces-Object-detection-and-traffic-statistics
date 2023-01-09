from MainWindow import Ui_MainWindow
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
import sys
import datetime
import cv2
import numpy as np
from PIL import ImageDraw, ImageFont
from centernet import CenterNet
from DataServer import FormetDayTime
from threading import Thread, Lock
import socket
from PIL import Image
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

centernet = CenterNet()
lock = Lock()

class predictWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        img_src = cv2.imread("model_data/timg.jpg")  # 读取图像
        img_src = cv2.cvtColor(img_src, cv2.COLOR_BGR2RGB)  # 转换图像通道
        label_width = self.label.width()
        label_height = self.label.height()
        temp_imgSrc = QImage(img_src[:], img_src.shape[1], img_src.shape[0], img_src.shape[1] * 3, QImage.Format_RGB888)
        # 将图片转换为QPixmap方便显示
        self.pixmap_imgSrc = QPixmap.fromImage(temp_imgSrc).scaled(label_width, label_height)
        now = datetime.datetime.now()
        time = now.strftime("%Y %m %d %H %M %S")
        timelist = time.split(" ")
        self.mon = int(timelist[1])
        self.isOn = False
        self.isVideoOn = False
        self.isImgOn = False
        self.day, self.time = FormetDayTime(timelist)
        self.label.setPixmap(QPixmap(self.pixmap_imgSrc))
        self.pushButton.clicked.connect(self.CountTime)
        self.pushButton_1.clicked.connect(self.imgOnOff)
        self.pushButton_2.clicked.connect(self.videoOnOff)
        self.pushButton_3.clicked.connect(self.On_Off)

    def CountTime(self):
        try:
            tco = np.zeros(24)
            tce = np.zeros(24)
            lock.acquire()
            with open("./detect_Logs/countlogs") as f:
                for fn in f.readlines():
                    print(fn)
                    tco[int(fn.split(';')[0])] += int(fn.split(";")[1])
                    tce[int(fn.split(';')[0])] += int(fn.split(";")[2].strip())

            lock.release()
            label = []
            for i in range(24):
                label.append(str(i))
            rate = tco / (tco + tce)
            plt.plot(range(24), rate, label="时段内车位占用比")
            plt.xticks(range(24), label)
            plt.xlim((0, 23))
            plt.xlabel("小时")
            plt.ylabel("车位占有率")
            plt.legend()
            plt.title("时段车位统计")
            plt.show()
        except:
            msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '数据加载失败!')
            msg_box.exec_()

    def imgOnOff(self):
        self.isImgOn = ~self.isImgOn
        if not self.isImgOn:
            self.pushButton_1.setText("图片检测")
        else:
            self.pushButton_1.setText("完成图片检测")

        if self.isImgOn:
            try:
                image_file, _ = QFileDialog.getOpenFileName(self, 'Open file', '\\', 'Image files (*.jpg *.gif *.png *.jpeg)')
            except:
                msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '未选中图片!')
                msg_box.exec_()
                print('Open Error! Try again!')
                return

            try:
                image = Image.open(image_file)
                r_image, obj1sum, obj2sum, color1, color2, max_cnt = centernet.detect_image(image)

                draw = ImageDraw.Draw(r_image)
                fontStyle = ImageFont.truetype(
                    font="model_data/simhei.ttf", size=20, encoding='utf-8')

                    # # 绘制框和文本
                    # draw.rectangle(
                    #     [tuple((0, 560)), tuple((180, 640))],
                    #     fill=(255, 255, 255), outline='black')

                draw.ellipse((10, 560, 30, 580), fill=color1)
                draw.ellipse((10, 600, 30, 620), fill=color2)
                draw.text((50, 560), "被占车位:" + str(obj1sum), color1, font=fontStyle)
                draw.text((50, 600), "空车位  :" + str(obj2sum), color2, font=fontStyle)

                r_image = np.array(r_image)
                    # RGBtoBGR满足opencv显示格式
                img_src = r_image # cv2.cvtColor(r_image, cv2.COLOR_RGB2BGR)
                label_width = self.label.width()
                label_height = self.label.height()
                temp_imgSrc = QImage(img_src[:], img_src.shape[1], img_src.shape[0], img_src.shape[1] * 3,
                                         QImage.Format_RGB888)

                    # 将图片转换为QPixmap方便显示
                pixmap_imgSrc = QPixmap.fromImage(temp_imgSrc).scaled(label_width, label_height)
                self.label.setPixmap(QPixmap(pixmap_imgSrc))

            except:
                msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '识别失败!')
                msg_box.exec_()
        else:
            self.label.setPixmap(QPixmap(self.pixmap_imgSrc))


    def videoOnOff(self):
        self.isVideoOn = ~self.isVideoOn
        if not self.isVideoOn:
            self.pushButton_2.setText("视频检测")
        else:
            self.pushButton_2.setText("停止视频检测")
        if self.isVideoOn:
            try:
                image_file, _ = QFileDialog.getOpenFileName(self, 'Open file', '\\',
                                                            'Video files (*.gif *.mp4 *.avi *.dat *.mkv *.flv *.vob *.3gp)')
                capture = cv2.VideoCapture(image_file)
            except:
                msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '未选中视频!')
                msg_box.exec_()
                print('Open Error! Try again!')
                return

            try:
                global centernet
                while self.isVideoOn:
                    ref, frame = capture.read()

                    now = datetime.datetime.now()
                    time = now.strftime("%Y %m %d %H %M %S")
                    timelist = time.split(" ")
                    self.day, self.time = FormetDayTime(timelist)

                    # 转变成Image
                    frame = Image.fromarray(np.uint8(frame))
                    # 进行检测
                    frame, obj1sum, obj2sum, color1, color2, max_cnt = centernet.detect_image(frame)

                    lock.acquire()
                    with open("./detect_Logs/logs.txt", 'w') as f:
                        f.write(self.day + " " + self.time + ';')
                        f.write(str(obj1sum)+';')
                        f.write(str(obj2sum)+";")
                        f.write(str(max_cnt))

                    with open("./detect_Logs/countlogs", 'a') as f:
                        f.write(self.time.split(":")[0] + ';')
                        f.write(str(obj1sum)+';')
                        f.write(str(obj2sum))
                        f.write("\n")
                    lock.release()
                    # 设置
                    draw = ImageDraw.Draw(frame)
                    fontStyle = ImageFont.truetype(
                        font="model_data/simhei.ttf", size=20, encoding='utf-8')

                    # 绘制框和文本
                    # draw.rectangle(
                    #     [tuple((0, 560)), tuple((180, 640))],
                    #     fill=(255, 255, 255), outline='black')

                    draw.ellipse((10, 560, 30, 580), fill=color1)
                    draw.ellipse((10, 600, 30, 620), fill=color2)
                    draw.text((50, 560), "被占车位:" + str(obj1sum), color1, font=fontStyle)
                    draw.text((50, 600), "空车位  :" + str(obj2sum), color2, font=fontStyle)
                    draw.text((0, 0), "时间:" + self.day + " " + self.time, (255, 255, 255), font=fontStyle)

                    frame.save("detect_Logs/1.png")
                    frame = np.array(frame)

                    img_src = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    label_width = self.label.width()
                    label_height = self.label.height()
                    temp_imgSrc = QImage(img_src[:], img_src.shape[1], img_src.shape[0], img_src.shape[1] * 3,
                                         QImage.Format_RGB888)

                    # 将图片转换为QPixmap方便显示
                    pixmap_imgSrc = QPixmap.fromImage(temp_imgSrc).scaled(label_width, label_height)
                    self.label.setPixmap(QPixmap(pixmap_imgSrc))

                    c = cv2.waitKey(1) & 0xff

                    if c == 27:
                        capture.release()
                        break

                capture.release()
                cv2.destroyAllWindows()


            except:
                self.label.setPixmap(QPixmap(self.pixmap_imgSrc))
        else:
            self.label.setPixmap(QPixmap(self.pixmap_imgSrc))

    def On_Off(self):
        self.isOn = ~self.isOn
        if not self.isOn:
            self.pushButton_3.setText("实时监测")
        else:
            self.pushButton_3.setText("结束实时监测")
        if self.isOn:
            capture = cv2.VideoCapture(0)
            global centernet
            while self.isOn:
                # 获取当前时间
                now = datetime.datetime.now()
                time = now.strftime("%Y %m %d %H %M %S")
                timelist = time.split(" ")
                self.day, self.time = FormetDayTime(timelist)

                # 读取某一帧
                ref, frame = capture.read()
                # 转变成Image
                frame = Image.fromarray(np.uint8(frame))
                # 进行检测
                frame, obj1sum, obj2sum, color1, color2, max_cnt = centernet.detect_image(frame)

                # 设置
                draw = ImageDraw.Draw(frame)
                fontStyle = ImageFont.truetype(
                 font="model_data/simhei.ttf", size=20, encoding='utf-8')

                # 绘制框和文本
                # draw.rectangle(
                #     [tuple((0, 0)), tuple((180, 40))],
                #     fill=(255, 255, 255), outline='black')
                # draw.rectangle(
                #     [tuple((0, 0)), tuple((420, 40))],
                #     fill=(255, 255, 255), outline='black')

                draw.ellipse((35, 410, 55, 430), fill=color1)
                draw.ellipse((35, 440, 55, 460), fill=color2)
                draw.text((60, 410), "被占车位:" + str(obj1sum), fill=color1, font=fontStyle)
                draw.text((60, 440), "空车位  :" + str(obj2sum), fill=color2, font=fontStyle)
                draw.text((0, 0), "时间:" + self.day + " " + self.time, (0, 0, 0), font=fontStyle)
                lock.acquire()
                with open("./detect_Logs/logs.txt", 'w') as f:
                    f.write(self.day + " " + self.time + ';')
                    f.write(str(obj1sum) + ';')
                    f.write(str(obj2sum)+";")
                    f.write(str(max_cnt))

                with open("./detect_Logs/countlogs", 'a') as f:
                    f.write(self.time.split(":")[0] + ';')
                    f.write(str(obj1sum) + ';')
                    f.write(str(obj2sum))
                    f.write("\n")

                lock.release()
                frame.save("detect_Logs/1.png")
                frame = np.array(frame)

                # RGBtoBGR满足opencv显示格式
                img_src = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                label_width = self.label.width()
                label_height = self.label.height()
                temp_imgSrc = QImage(img_src[:], img_src.shape[1], img_src.shape[0], img_src.shape[1] * 3,
                                     QImage.Format_RGB888)

                # 将图片转换为QPixmap方便显示
                pixmap_imgSrc = QPixmap.fromImage(temp_imgSrc).scaled(label_width, label_height)
                self.label.setPixmap(QPixmap(pixmap_imgSrc))

                # if int(timelist[4]) % 5 == 0 and int(timelist[5]) == 0:
                #     # 每隔五分钟保存一次
                #     SaveData(self.day, self.time, num)
                c = cv2.waitKey(1) & 0xff

                if c == 27:
                    capture.release()
                    break
            capture.release()
            cv2.destroyAllWindows()
        else:
            self.label.setPixmap(QPixmap(self.pixmap_imgSrc))


def detect_process():
    app = QApplication(sys.argv)
    window = predictWindow()
    window.show()
    sys.exit(app.exec_())

def response_process():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', 8000))
    sock.listen(5)
    while 1:
        cli_sock, cli_addr = sock.accept()
        req = cli_sock.recv(4096)
        lock.acquire()
        with open('detect_Logs/logs.txt') as f:
            word = f.readline()
            cli_sock.send(word.encode())
        cli_sock.close()
        lock.release()

if __name__ == "__main__":
    t1 = Thread(target=detect_process)
    t2 = Thread(target=response_process)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
