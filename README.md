# Vehicles-ParkingSpaces-Object-detection-and-traffic-statistics
 通过目标检测算法检测和统计区域内的车辆与车位情况使用户能够提前获知车位情况以及对用户停车位置的引导，并能对实际车流量进行统计。

# 功能介绍
## 服务器端（PKLot_server）
PKLot_server中的是服务器端，负责对车位进行目标检测，判断是否已有车停在车位上，并统计计算最优停车区域，以及记录车位占用情况以供统计可视化使用,检测后的数据将存储到detect_Log中，以供数据分析使用。当服务器端需要统计时，从detect_Log中读出相应的数据并做图展示

## 客户端（PKLot_client）
PKLot_client为客户端，客户端发起车位查询的请求，客户端负责接收来自服务器端检测的车位占用情况以及最优的停车区域，并将其标注在画面上起到对于用户的指引作用

## 可视化

使用PyQt5构建可视化窗口

# 权值文件

权值文件下载后应该放到 \PKLot_server\model_data文件夹中

**权值文件下载地址：**

链接：https://pan.baidu.com/s/1X_iAieXwVn02HEo5ihFSFw?pwd=xqbr 

提取码：xqbr

# 测试样例

**测试样例下载链接：**

链接：https://pan.baidu.com/s/1wH5_PkoUYxQTXvEt6wzoHA?pwd=m76z 

提取码：m76z

# 演示视频

视频链接：[https://www.bilibili.com/video/BV1XG4y1w7kT](https://www.bilibili.com/video/BV1XG4y1w7kT)
