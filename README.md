# 一定要对照注释改init
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
![wayfing](https://github.com/GrayTempest-400/warthunder-cv2/assets/101955396/762235bb-c636-4a9d-955c-7a2a928c2f7d)
自动寻路 基于8111端口
测试视频请见
https://www.bilibili.com/video/BV1M841127RG/
源码说明:

- wt_auto.py: 入口, 自瞄逻辑，敌我识别与程序控制都在这里
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
- edge_detect.py              街机版
- detect.py                   街机版的依赖
- 其他 ： 依赖文件或无用文件



操纵键鼠
大多FPS游戏都屏蔽了操作鼠标的Win函数, 要想在游戏中用代码操作鼠标, 需要一些特殊的办法, 其中罗技驱动算是最简单方便的了

代码直接控制罗技驱动向操作系统(游戏)发送鼠标命令, 达到了模拟鼠标操作的效果, 这种方式是鼠标无关的, 任何鼠标都可以使用这种方法

我们不会直接调用罗技驱动, 但是有大佬已经搭过桥了, 有现成的调用驱动的dll, 只是需要安装指定版本的罗技驱动配合才行

百度网盘 罗技键鼠驱动
驱动安装：https://pan.baidu.com/s/1VkE2FQrNEOOkW6tCOLZ-kw?pwd=yh3s
罗技驱动分 LGS (老) 和 GHub (新)

LGS, 需要使用 9.02.65 版本
GHub, 需要使用 2021.11 版本之前的, 因 2021.11 版本存在无法屏蔽自动更新的问题, 所以暂时建议选 2021.3 版本
如果有安装较新版本的 GHub, 需要运行 C:\Program Files\LGHUB\lghub_uninstaller.exe 卸载, 然后重新安装旧版本 GHub

装好驱动后, 需在设置中 取消 勾选 启用自动更新, 可运行 屏蔽GHUB更新.exe 防止更新(不一定有效)

另外需要确保 控制面板-鼠标-指针选项 中下面两个设置

提高指针精确度 选项去掉, 不然会造成实际移动距离变大
选择指针移动速度 要在正中间, 靠右会导致实际移动距离过大, 靠左会导致指针移动距离过小
运行 logitech.test.py 查看效果, 确认安装是否成功, End 键 结束程序, Home 键 移动鼠标, 自行测试效果, 如无效果, 则按上述步骤检查


