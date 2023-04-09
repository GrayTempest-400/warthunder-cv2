# warthunder-cv2
战争雷霆坦克训练器
在have_thank文件夹正样本no_负样本

1，运行完run.py后cmd在正样本和负样本中cmd 分别输入dir /b/s/p/w *.jpg > have_mask.txt 创建路径文件

2， 此时在have_thank下就会产生一个have_than.txt文件，并将其放到上一层目录,no_thank也相同

3,运行run2.py

4,创建xml放置训练好的模型

5,在thank文件夹cmd运行opencv_createsamples.exe -vec havethank.vec -info have_mask.txt -num 400 -w 20 -h 20

pause得到havethank.vec文件

6,修改文件名为start.bat并运行

7，训练完成后在xml文件下即可看到以下文件，第一个文件即为我们训练好的分类器
