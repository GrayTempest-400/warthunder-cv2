Houzhui=r" 1 0 0 20 20" #后缀
filelist = open('have_thank.txt','r+',encoding = 'utf-8')
line = filelist.readlines()
for file in line:
    file=file.strip('\n')+Houzhui+'\n'
    print(file)
    filelist.write(file)