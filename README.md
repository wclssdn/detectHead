# 头部检测

## 功能描述

此命令行应用通过摄像头采集面部各关键点位，计算点位之间的关系，识别出用户是否低头或者距离摄像头太近。

支持通过配置文件个性化设置（参考config/default.ini）

- 提示音效
- 面部关键点位选取
- 识别间隔（越久越省电，也越不灵敏）


## 使用方式

启动终端，执行`start.sh`脚本

首次启动加载时间预计1分钟左右，请耐心等待。当应用要获取摄像头权限时，请允许。

每次启动时都会加载配置文件中的阈值等配置，可以在视频采集窗口中按快捷键进行调整（此调整不会保存到配置文件中，用户可自行修改配置文件）
