# 说明
#没有训练集，还没训练集不能检测出坦克！！！
#用peron测试的
![%6WRE61M5EG E@9H7`SNWO5](https://user-images.githubusercontent.com/101955396/235575092-137cb391-bc70-4897-9cac-92996a9178ff.png)
能拉枪指到人

检测坦克就会出现这样
![2RQ4)~W@6F8OPUIF3)F WJ](https://user-images.githubusercontent.com/101955396/235575351-2f84fc2f-37a6-4fcd-b1b0-43fb09fd540f.png)
![P0Y(RNR6GYZ2T$~$0`IA%MQ](https://user-images.githubusercontent.com/101955396/235575471-05ea3bd4-67bf-4828-9563-792ef1b67821.png)
![Z2UKYV93Z6FTALES6WHD)O6](https://user-images.githubusercontent.com/101955396/235575485-2aa5b5a7-eb90-4f8e-8207-a00f54b55cad.png)


因为没有计算机视觉相关方向的专业知识, 所以做出来的东西, 有一定效果, 但是还有很多不足, 目前仍在调优

源码说明:

- wt_auto.py: 入口, 自瞄逻辑，敌我识别与程序控制都在这里
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

- .pt 模型可以转换为 .engine 模型以提高推理速度(需要 TensorRT 环境支持)
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

