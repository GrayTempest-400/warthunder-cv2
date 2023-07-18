
# 说明(一定要打开源码看注释！！！）
# 没有训练集，还没训练集不能检测出坦克！！！
# 用person测试的
![%6WRE61M5EG E@9H7`SNWO5](https://user-images.githubusercontent.com/101955396/235575092-137cb391-bc70-4897-9cac-92996a9178ff.png)
能拉枪指到人

![123](https://user-images.githubusercontent.com/101955396/235646622-bdff5520-e61f-4691-92e6-28ce674a67df.png)
`星野爱指哪我哪（（（`                   整活p图，实际使用情况见上

检测坦克就会出现这样，因为没有训练训练集
![2RQ4)~W@6F8OPUIF3)F WJ](https://user-images.githubusercontent.com/101955396/235575351-2f84fc2f-37a6-4fcd-b1b0-43fb09fd540f.png)
![P0Y(RNR6GYZ2T$~$0`IA%MQ](https://user-images.githubusercontent.com/101955396/235575471-05ea3bd4-67bf-4828-9563-792ef1b67821.png)
![Z2UKYV93Z6FTALES6WHD)O6](https://user-images.githubusercontent.com/101955396/235575485-2aa5b5a7-eb90-4f8e-8207-a00f54b55cad.png)



![532](https://user-images.githubusercontent.com/101955396/235846080-859c8ea1-39fe-40a6-80bc-8caea10acad1.png)

`卡尔曼滤波`蓝圈是预测出的预测点（截图技术不好就截的只剩半圆了）           因为放不了视频就随便截了张图


![mb](https://github.com/GrayTempest-400/warthunder-cv2/assets/101955396/507fbd2c-7192-4661-b421-298ffd702249)
模板匹配，精准度还行
 
![rang](https://github.com/GrayTempest-400/warthunder-cv2/assets/101955396/c05d2352-e658-4227-b2dc-806f550b45d5)
单目测距
![Arcade](https://github.com/GrayTempest-400/warthunder-cv2/assets/101955396/dba91475-c91f-4c82-92ab-f1a76f2cbd72)
街机检测版，绿色的是瞄准点                   根据边缘检测，代码25 - 27 行HSV范围自己调，我也不会找HSV范围，检测不准确
源码说明:

- wt_auto.py: 入口, 自瞄逻辑，敌我识别与程序控制都在这里
- wt_auto_Arcade : 街机版
- yolov8FPSGame : yolov8版，基于 wt_auto.py
- Monocular_ranging : 测距，具体自定义见代码注释
- toolkit.py , tool , detect: 自行封装的工具, 封装了截图推理等工具
- yolos5s.pt: 预训练模型权重文件,无训练，还不能检测坦克
- logitech.driver.dll: 调用罗技驱动的库文件
- test.py: 草稿文件，可以不要管
- detect.realtime.py: 实时展示推理结果, 用于测试权重文件是否好用, 可通过播放warthunder集锦来测试
- export.pt: 导出工具, 将 .pt 导出为 .engine 等
- toolkit8111 ： 通过访问8111端口获取地图等信息进行自动寻路
- wt.bak.fov,wt.bak.pid,wt.bak.queue : 基于wt_auto的改进型
- tool_matches ，find_direction: 模板匹配工具   自定义用于检测按钮
- 其他 ： 依赖文件或无用文件


