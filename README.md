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

`卡尔曼滤波`蓝圈是预测出的预测点           因为放不了视频就随便截了张图

因为没有计算机视觉相关方向的专业知识, 所以做出来的东西, 有一定效果, 但是还有很多不足, 目前仍在调优

源码说明:

- wt_auto.py: 入口, 自瞄逻辑，敌我识别与程序控制都在这里
- kalman_wt.py:在wt_auto.py的基础上加了卡尔曼滤波，用于攻击移动的敌人(屏幕坐标系检测，类似[1,0][2,0][3,0]卡尔曼预测出[4,0]`但战雷谁会匀速
走直线（`
- toolkit.py: 自行封装的工具, 封装了截图推理等工具
- yolos5s.pt: 预训练模型权重文件,无训练，还不能检测坦克
- logitech.driver.dll: 大佬封装的调用罗技驱动的库文件
- logitech.test.py: 用于测试罗技驱动安装配置是否正确
- test.*.py: 测试一些东西
- detect.realtime.py: 实时展示推理结果, 用于测试权重文件是否好用, 可通过播放warthunder集锦来测试
- export.pt: 导出工具, 将 .pt 导出为 .engine 等

参数说明: apex.py 中的 init

- ads: 就是一个作用于鼠标移动距离的倍数, 用于调整移动鼠标时的实际像素和鼠标 eDPI 的关系. 
  - 调整方式: 瞄准目标旁边并按住 Shift 键, 当准星移动到目标点的过程, 稳定精准快速不振荡时, 就找到了合适的 ADS 值
- classes: 要检测的标签的序号(标签序号从0开始), 多个时如右 [0, 1]

按键说明:        （具体见wt_auto.py注释)

- End: 全局有效, 退出程序
- Shift: 仅游戏中有效, 锁定敌人
  - Shift 在游戏中默认是 `开镜` 快捷键, 我修改为 `鼠标滚轮上旋`, 同时设置了 `右键放大`, 所以 Shift 可以用来锁定目标, 很顺手
- Down: 仅游戏中有效, 是否显示推理结果
- Up: 仅游戏中有效, 是否瞄头
  - 该瞄头是通过身体范围大致推断出来的头的位置, 正面效果比较好, 侧面可能瞄不到头
- Left: 仅游戏中有效, 按鼠标左键时锁
- Right: 仅游戏中有效, 是否启用 PID 控制

其他说明:

- 显示器关闭 `缩放`
- 游戏分辨率和显示器物理分辨率需要一致
- 游戏需要设置显示模式为 `无边框窗口`
- 游戏可能需要限制帧数, 以便给显卡让出足够算力做目标检测, 比如锁60帧 `+fps_max 60`, 根据自己的情况定

模型转换

- .pt 模型可以转换为 .engine 模型以提高推理速度(需要 TensorRT 环境支持)           转为.engine速度加3倍
- `python export.py --weights 你训练出的.pt --device 0 --include engine`

# 环境准备

运行工程, 需要 PyTorch Cuda 环境,tensorRT,cuDNN



## 操纵键鼠

大多FPS游戏都屏蔽了操作鼠标的Win函数(DirectInput), 要想在游戏中用代码操作鼠标, 需要一些特殊的办法, 其中罗技驱动算是最简单方便的了

代码直接控制罗技驱动向操作系统(游戏)发送鼠标命令, 达到了模拟鼠标操作的效果, 这种方式是鼠标无关的, 任何鼠标都可以使用这种方法

我们不会直接调用罗技驱动, 但是有大佬已经搭过桥了, 有现成的调用驱动的dll, 只是需要安装指定版本的罗技驱动配合才行

> [百度网盘 罗技键鼠驱动](https://pan.baidu.com/s/1VkE2FQrNEOOkW6tCOLZ-kw?pwd=yh3s)

罗技驱动分 LGS (老) 和 GHub (新)

- LGS, 需要使用 9.02.65 版本
- GHub, 需要使用 2021.11 版本之前的, 因 2021.11 版本存在无法屏蔽自动更新的问题, 所以暂时建议选 2021.3 版本

如果有安装较新版本的 GHub, 需要运行 `C:\Program Files\LGHUB\lghub_uninstaller.exe` 卸载, 然后重新安装旧版本 GHub

装好驱动后, 需在设置中 `取消` 勾选 `启用自动更新`, 可运行 `屏蔽GHUB更新.exe` 防止更新(不一定有效)

另外需要确保 控制面板-鼠标-指针选项 中下面两个设置

- 提高指针精确度 选项去掉, 不然会造成实际移动距离变大
- 选择指针移动速度 要在正中间, 靠右会导致实际移动距离过大, 靠左会导致指针移动距离过小

运行 `logitech.test.py` 查看效果, 确认安装是否成功, End 键 结束程序, Home 键 移动鼠标, 自行测试效果, 如无效果, 则按上述步骤检查

## 键鼠监听

> [Pynput 说明](https://pypi.org/project/pynput/)

注意调试回调方法的时候, 不要打断点, 不然会卡死IO, 导致鼠标键盘失效

回调方法如果返回 False, 监听线程就会自动结束, 所以不要随便返回 False

键盘的特殊按键采用 `keyboard.Key.tab.xxx` 这种写法，普通按键用 `keyboard.KeyCode.from_char('c')` 这种写法, 有些键不知道该怎么写, 可以 `print(key)` 查看信息

部分代码说明
FOV 详见 apex.fov.py (FOV 我觉得比较鸡肋, 已放弃)
鼠标灵敏度, ADS鼠标灵敏度加成, FOV视角, 位移像素之间的关系
鼠标灵敏度: 鼠标灵敏度是鼠标物理移动距离与游戏内视角旋转角度的倍数关系. 假设鼠标灵敏度为 1 时, 鼠标向右移动 100 像素, 游戏内向右转动 2°. 则鼠标灵敏度为 2 时, 鼠标向右移动 100 像素, 游戏内向右转动 (2×鼠标灵敏度)°
ADS鼠标灵敏度加成: 开镜后的鼠标灵敏度, 灵敏度=基本灵敏度×ADS加成
FOV: 第一人称角色视角范围? 可近似认为就是视线角度? 包括水平和垂直两种
DPI: 物理调整鼠标的移动幅度
如何求 鼠标从中心跳到敌人位置对应的鼠标物理水平移动像素
在这里插入图片描述

假设 AB 是屏幕, ∠AOB 是角色视角(即 FOV), C 是屏幕中心(准星), X是敌人位置(已知, 目标检测得到的坐标), 求鼠标向左移动多少像素能让准星正好落在敌人 X 身上?

假设当前游戏设置的 FOV 是 120, 即水平视角是 120°, 即 ∠AOB 是 120°, 可知 ∠ AOC 是 60°

因为 OC 垂直于 AB 所以三角形 AOC 是直角三角形, 根据三角函数可知, AC/OC=tan60°, 可得 OC=AC/tan60°

AB 的长度就是游戏的水平分辨率, 可知 AC 长度为 AB 的一半, 由此可得 OC=AB/2/tan60°

CX 可以由目标检测的结果算出来, OC 也知道了, 又因为三角形 OCX 是直角三角形, 可知 CX/OC=tan∠COX, 可得 ∠COX

当然, 计算角度的正切值和反正切值, 需要将角度转换为弧度, 才能代入函数. 角度=弧度×π/180, 弧度=角度×180/π

tan60°=tan(60×π/180), ∠COX=atan(CX/OC)×180/π

假设游戏内水平旋转 360°, 对应的鼠标需要水平移动 a 像素, 我们称之为 一周移动量, 即鼠标每移动 a/360 像素, 视角水平旋转 1°

求出了 ∠COX, 再乘以视角旋转 1° 需要移动的鼠标距离, 就可以求出让准星落在 OX 这条线上需要移动的鼠标距离了

所以, 鼠标移动的距离=∠COX*a/360

接下来就该测 一周移动量 了, 拿到这个值即可计算需要的 鼠标移动量

算鼠标垂直移动量也是一样的, 但是因为 OC 已经计算出来了, 可以直接使用, 只需要测游戏内垂直方向的 半周移动量 即可

如何测 游戏内水平旋转 360° 对应鼠标水平移动的像素
通常在 FPS 游戏内, 鼠标的位置是固定在屏幕中心的, 我们移动鼠标, 动的不是鼠标位置, 而是游戏内 FOV 视角的朝向, 所以不论如何旋转视角, 取鼠标位置的函数返回的鼠标坐标点, 永远都是屏幕的正中心(全屏游戏时)

所以, 测试游戏内的 一周移动量 得反着来. 记录移动鼠标的距离之和, 当正好旋转了 1 周时, 该值就是需要的距离

需要用本文 工程源码 下 test.measure.palstance.py 部分来测试, 该方法可测试水平和垂直两个方向的像素, 垂直方向通常只能测一半

操作说明
按右键: 模拟鼠标向右移动 100 像素, 按住 Shift 键再按右键, 模拟鼠标向右移动 10 像素, 反之同理
按 Enter 键清零, 可重新测量
按 End 键结束程序
测试水平距离: 选一个点让准星对准该点, 按右键旋转一周, 让准星正好回到原位, 看日志里向右移动了的距离
测试垂直距离: 下拉鼠标到底, 找一个特征点, 让准星对准该点. 然后按上键到视角不再变化, 再多按几次上键, 然后按回车键清零, 然后按下键和 shift+下键, 直到准星与之前选好的特征点刚好重合, 然后看日志里的移动距离. 切记不要按多了, 因为到底后再按下键, 会继续累加移动距离, 但准星受游戏机制影响却是不会动了

灵敏度一定要根据实际情况改，不然可能拉枪拉上天



当我们调整 ADS 不为 1 后, 移动反而会不准. 调小会导致移动变慢, 但还是能稳定在目标点, 调大会无限左右横跳
卡尔曼滤波器预测目标轨迹

利用卡尔曼滤波与Opencv进行目标轨迹预测
PySource - Kalman filter, predict the trajectory of an Object

我不清楚其中的原理的, 只是大概知道是根据前几帧的状态预测下一帧的轨迹

找了个预测橘子位置的案例, 然后做了个预测来回摆动的小球的例子 (详见 kalman_wt.py), 接着就改吧改吧整合进来了

只移动人物是可以用卡尔曼滤波器来预测敌人位置的, 而调整视角时则不适用卡尔曼滤波器, 因为每次移动鼠标像目标靠近, 都是在人为地破坏卡尔曼滤波器依赖的数据, 会导致预测不准

瞄准效果
暂无

