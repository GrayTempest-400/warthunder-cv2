import time

from find import locate, find_match, check
from utils import active, logger_log as log, click


def cantjoin():#加入失败
    while True:
        active()
        error1 = find_match('pic/error1.png', 0.8)
        if error1 is not None:
            log('检测到选择载具弹窗')
            p = 10, 30
            click(p)
            chkerr1 = check('pic/error1.png', 0.8)
            if chkerr1 is True:
                click(p)
        else:
            break

def main_end():
    global flag_back
    flag_back = False
    while True:
        active()
        if flag_back is False:
            log('正在检测是否有其他要素')
            pic_list = {'pic/lingqu.png', 'pic/res01.png', 'pic/ok02.png', 'pic/okk.png',
                        'pic/ok03.png', 'pic/rescom.png', 'pic/close.png', 'pic/x.png', 'pic/tectree.png',
                        'pic/completeres.png', 'pic/buy.png', 'pic/checkin.png', 'pic/backtobase2.png', 'pic/lost.png'}
            for pic in pic_list:
                a = locate(pic, 0.8)
                time.sleep(0.5)
                if a is not None:
                    if pic == 'pic/lingqu.png':
                        menu = locate('pic/lost.png', 0.8)
                        if menu is not None:
                            click(a)
                            log('开箱子')
                    elif pic == 'pic/res01.png':
                        click(a)
                        log('分配研发')
                    elif pic == 'pic/ok02.png':
                        click(a)
                        log('确定')
                    elif pic == 'pic/ok03.png':
                        click(a)
                        log('确定')
                    elif pic == 'pic/rescom.png':
                        click(a)
                        log('研发载具')
                    elif pic == 'pic/close.png':
                        click(a)
                        log('关闭其他')
                    elif pic == 'pic/x.png':
                        click(a)
                        log('关闭其他')
                    elif pic == 'pic/completeres.png':
                        click(a)
                        log('完成研发')
                    elif pic == 'pic/buy.png':
                        notbuy = locate('pic/notbuy.png', 0.8)
                        no = locate('pic/no.png', 0.8)
                        if notbuy is not None:
                            time.sleep(0.5)
                            click(notbuy)
                            log('pic/notbuy.png')
                        elif no is not None:
                            time.sleep(0.5)
                            click(no)
                            log('pic/no.png')
                    elif pic == 'pic/tectree.png':
                        p = (20, 60)
                        click(p)
                        log('关闭科技树')
                    elif pic == 'pic/checkin.png':
                        menu = locate('pic/lost.png', 0.8)
                        if menu is not None:
                            click(a)
                            log('签到')
                            time.sleep(8)
                            lingquqiandao = locate('pic/close.png', 0.8)
                            time.sleep(0.5)
                            click(lingquqiandao)
                            log('领取成功')
                    elif pic == 'pic/backtobase2.png':
                        click(a)
                        log('返回基地')
                        flag_back = True
                        time.sleep(5)
                        menu = locate('pic/lost.png', 0.8)
                        time.sleep(0.5)
                        if menu is not None:
                            flag_back = True
                            log('循环结束')
                            break
                        else:
                            continue
                    elif pic == 'pic/lost.png':
                        time.sleep(2)
                        confirm = locate('pic/lost.png', 0.8)
                        if confirm is not None:
                            flag_back = True
                            log('循环结束，已经在主菜单')
                            break
                        else:
                            continue
                    elif pic == 'pic/okk.png':
                        click(a)
                        log('点击确定，可能有其他待点击资源')
                        time.sleep(5)
                        wait_for_match = ['pic/completeres.png', 'pic/rescom.png', 'pic/res01.png']
                        for wait_pic in wait_for_match:
                            wait_pic_loc = locate(wait_pic, 0.8)
                            stop = locate('pic/lost.png', 0.8)
                            time.sleep(0.5)
                            if wait_pic_loc is not None:
                                if wait_pic_loc == 'pic/completeres.png':
                                    click(wait_pic_loc)
                                    log('完成研发')
                                    time.sleep(0.5)
                                elif wait_pic_loc == 'pic/rescom.png':
                                    click(wait_pic_loc)
                                    log('研发载具')
                                    time.sleep(0.5)
                                elif wait_pic_loc == 'pic/res01.png':
                                    click(wait_pic_loc)
                                    log('分配研发')
                                    time.sleep(0.5)
                            elif stop is not None:
                                flag_back = True
                                log('循环结束')
                                break
        else:
            break
    cantjoin()
    return True