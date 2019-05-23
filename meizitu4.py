import requests
from bs4 import BeautifulSoup
import re
import threading
import time
import openpyxl

# 零级url: https://www.mzitu.com/
# 一级url: https://www.mzitu.com/xx/         如：https://www.mzitu.com/zipai/
# 二级url: https://www.mzitu.com/xx/xx/xx    如：https://www.mzitu.com/zipai/comment-page-392/#comments
# 三级url: https://wxt.sinaimg.cn/xxx.jpg    如：https://wxt.sinaimg.cn/mw1024/9d52c073gy1g39bu9ybbsj20u012m4fq.jpg

start = time.time()

# 第一个多线程用来构造二级url并爬取三级url(存放图片的url)
class my_thread(threading.Thread):
    def __init__(self,num):
        threading.Thread.__init__(self)
        #self.ID = ID
        self.num = num

    def run(self):
        print("开始线程：" + self.num)
        crawler1(self.num)
        print("退出线程：" + self.num)

def crawler1(num):
    global l1,l2,l0,lh,lj
    while len(l1) > 0:
        url = l1.pop(0)
        headers = {}
        res = requests.get(url,headers=headers,timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        u = soup.find_all(class_='page-numbers')[-1].text
        # 每个二级url里有若干三级url
        for x in range(1,int(u)+1):
            urls = url+'comment-page-'+str(x)+'/'
            headers = {}
            res = requests.get(urls,headers=headers,timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text,'html.parser')
                o = soup.find(class_='postlist').find_all('li')
                for y in o:
                    try:
                        urls = y.find('img')['data-original']
                        l = hash(urls)
                        if l not in lh:
                            lh.append(l)
                            l2.append(urls)
                        else:
                            pass
                    except:
                        pass
            else:
                l = hash(urls)
                if l not in lh:
                    lj.append(l)
                    l0.append(urls)
                else:
                    pass
        print('%s号爬取完一组三级url %s' % (num,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))

# 第二个多线程用来下载图片
class MyThread(threading.Thread):
    def __init__(self,num):
        threading.Thread.__init__(self)
        self.num = num

    def run(self):
        print("开始线程：" + self.num)
        crawler2(self.num)
        print("退出线程：" + self.num)

def crawler2(num):
    global l2
    while len(l2) > 0:
        url = l2.pop(0)
        name = re.findall('.*/.*?(\d.*)',url)[0]
        headers = {}
        res = requests.get(url,headers=headers,timeout=60)
        with open('d:/python/自拍街拍/'+name,'wb') as f:
            f.write(res.content)
        print('%s号完成爬取一张图片 %s' % (num,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))

if __name__ == '__main__':

    start = time.time()
    # 爬自拍、街拍妹子图片
    url = 'https://www.mzitu.com/tag/ugirls/'
    headers = {}
    res = requests.get(url,headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    s = soup.find(id='menu-nav').find_all('a')

    l1 = []  # 用来放一级url
    l0 = []  # 用来放爬取失败的二级url
    lj = []  # 用来放爬取失败的二级url的hash值
    l2 = []  # 用来放三级url
    lh = []  # 用来放三级url的hash值

    for x in s[5:7]:
        url = x['href']
        l1.append(url)

    # 创建2个新线程
    thread = {}
    for i in range(2):
        thread[str(i)] = my_thread(str(i))
    # 开启新线程
    for i in range(2):
        thread[str(i)].start()
    # 等待至线程中止
    for i in range(2):
        thread[str(i)].join()

    # 爬取之前爬取失败的二级url
    while len(l0) > 0:
        url = l0[0]
        headers = {}
        res = requests.get(url,headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text,'html.parser')
            o = soup.find(class_='postlist').find_all('li')
            for y in o:
                try:
                    urls = y.find('p')['src']
                    l = hash(urls)
                    if l not in lh:
                        lh.append(l)
                        l2.append(urls)
                    else:
                        pass
                except:
                    pass
            l0.pop(0)
            print('成功爬取到一组三级url')
        else:
            pass

    # 创建20个新线程
    thread = {}
    for i in range(20):
        thread[str(i)] = MyThread(str(i))
    # 开启新线程
    for i in range(20):
        thread[str(i)].start()
    # 等待至线程中止
    for i in range(20):
        thread[str(i)].join()

    print("退出主线程，耗时%s" % (time.time() - start))
