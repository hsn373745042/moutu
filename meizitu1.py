import requests
import os
from bs4 import BeautifulSoup
import re
import threading
import time
import openpyxl
# 零级url: https://www.mzitu.com/
# 一级url: https://www.mzitu.com/xxx/        如：https://www.mzitu.com/mm/
# 二级url: https://www.mzitu.com/xxx/page/x/ 如：https://www.mzitu.com/mm/page/2/
# 三级url: https://www.mzitu.com/xxxxx/      如：https://www.mzitu.com/184030
# 四级url：https://www.mzitu.com/xxxxx/x     如：https://www.mzitu.com/184030/2
# 五级url: https://i.meizitu.net/xxx.jpg     如：https://i.meizitu.net/2019/05/09b02.jpg

# 第一个多线程用来构造二级url和爬取三级url
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
    global l1,l2,l0,lh
    while len(l1) > 0:
        # 取当前l1列表的一级url并删除，防止各线程爬取相同url
        url = l1.pop(0)
        headers = {}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 爬取一级url下的页码数（每页有若干个三级url）
        u = soup.find_all(class_='page-numbers')[-2].text
        # 构造二级url
        for x in range(1,int(u)+1):
            # 第一个二级url
            if x == 1:
                urls = url
                res = requests.get(urls,headers=headers,timeout=10)
# 有的时候会请求失败，但是多请求几次可以成功，所以若在多线程里失败了，可以暂时把这个二级url放到一个列表里，最后集中进行重复请求
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    # 找到存放三级url的标签
                    o = soup.find(id='pins').find_all('li')
                    # 爬取第一页中的所有三级url
                    for y in o:
                        # 异常处理是为了除去'li'标签中混入的广告
                        try:
                            urls = y.find('a')['href']
                            # 用hash去重三级url，也可能多此一举
                            l = hash(urls)
                            if l not in lh:
                                lh.append(l)
                                l2.append(urls)
                            else:
                                pass
                        except:
                            pass
                # 第一次请求失败，把这个二级url先放到列表l0中
                else:
                    l0.append(urls)
                    pass
            # 更多二级url
            else:
                urls = url+'page/'+str(x)+'/'
                res = requests.get(urls, headers=headers,timeout=10)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    o = soup.find(id='pins').find_all('li')
                    for y in o:
                        try:
                            urls = y.find('a')['href']
                            l = hash(urls)
                            if l not in lh:
                                lh.append(l)
                                l2.append(urls)
                            else:
                                pass
                        except:
                            pass
                else:
                    l0.append(urls)
                    pass
        print('%s号爬取完一组三级url %s' % (num,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))

# 第二个多线程用来构造四级url和爬取五级url(存放图片的url)并下载图片
class MyThread(threading.Thread):
    def __init__(self,threadID,num):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.num = num

    def run(self):
        print("开始线程：" + self.num)
        crawler2(self.num)
        print("退出线程：" + self.num)

def crawler2(num):
    global l2,l0,l3
    while len(l2) > 0:
        url = l2.pop(0)
        headers = {}
        res = requests.get(url,headers=headers,timeout=60)
# 同上，请求失败的三级url先放到列表l0(在开启第二个多线程前，会循环爬取失败的二级url，之前存放二级url的l0就变为[])
        if res.status_code == 200:
            soup = BeautifulSoup(res.text,'html.parser')
            # 爬取三级url下的页码数（每页只有1个五级url）
            o = soup.find(class_='pagenavi').find_all('a')[-2].text
            # 为了方便分类和命名，用三/四级url标题命名文件夹，五级url的一部分命名文件。
            # 有的三/四级url标题存在“：”和“？”，故用异常处理找出来并替换为“”。
            try:
                title = soup.find(class_='main-image').find('img')['alt'].replace('?','')
                os.mkdir('d:\\python\\meizitu\\' + title)
            except:
                try:
                    title = soup.find(class_='main-image').find('img')['alt'].replace('：','')
                    os.mkdir('d:\\python\\meizitu\\' + title)
                except:
                    title = soup.find(class_='main-image').find('img')['alt']
                    os.mkdir('d:\\python\\meizitu\\'+title)
            # 构造更多四级url
            for x in range(1,int(o)+1):
                if x == 1:
                    # 第一页的四级url和三级url一样，无需构造
                    urls = url
                    headers = {}
                    res = requests.get(urls,headers=headers,timeout=60)
                    # 同上，请求失败的四级url先放到列表l3
                    if res.status_code == 200:
                        soup = BeautifulSoup(res.text,'html.parser')
                        # 找到存放五级url的标签
                        ur = soup.find(class_='main-image').find('img')['src']
                        name = re.findall('.*?(\d.*)', ur)[0].replace('/', '_')
                        # 这里状态码只会返回200或403，破解了请求头就能拿到图片
                        headers = {}
                        # 爬取五级url并下载图片
                        res = requests.get(ur, headers=headers, timeout=60)
                        with open('d:/python/meizitu/' + title + '/' + name, 'wb') as f:
                            f.write(res.content)
                    else:
                        l3.append([urls])
                else:
                    # 构造更多四级url
                    urls = url+'/'+str(x)
                    headers = {}
                    res = requests.get(urls,headers=headers,timeout=60)
                    if res.status_code == 200:
                        soup = BeautifulSoup(res.text,'html.parser')
                        ur = soup.find(class_='main-image').find('img')['src']
                        name = re.findall('.*?(\d.*)', ur)[0].replace('/', '_')
                        headers = {}
                        res = requests.get(ur,headers=headers,timeout=60)
                        with open('d:/python/meizitu/'+title+'/'+name,'wb') as f:
                            f.write(res.content)
                    else:
                        l3.append([urls])
            print('%s号完成爬取一组图片 %s' % (num,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        else:
            l0.append([url])
            print('%s号遇到无法爬取的三级url %s' % (num,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))

# 用来保存爬取失败的三级url和四级url
def my_url(s,l):
    # 创建工作簿
    wb = openpyxl.Workbook()
    # 添加工作表
    sheet = wb.active
    # 给工作表命名
    sheet.title = 'url2'
    wb.create_sheet(title='url1',index=0)
    for i in s:
        wb['url1'].append(i)
    for i in l:
        wb['url2'].append(i)
    # 保存工作簿并命名
    wb.save('meizi.xlsx')

if __name__ == '__main__':
    start = time.time()
    # 爬首页、性感、日本、台湾、清纯妹子图片
    url = 'https://www.mzitu.com/tag/ugirls/'
    headers = {}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    s = soup.find(id='menu-nav').find_all('a')
    l1 = []  # 用来放一级url
    l0 = []  # 先用来放爬取失败的二级url，后用来放爬取失败的三级url
    l2 = []  # 用来放爬取成功的三级url
    lh = []  # 用来放爬取成功的三级url的哈希值
    l3 = []  # 用来放爬取失败的四级url
    for x in s[0:5]: # 只取前5个一级url
        url = x['href']
        l1.append(url)
    # 创建3个新线程
    thread ={}
    for i in range(3):
        thread[str(i)] = my_thread(str(i))
    # 开启新线程
    for i in range(3):
        thread[str(i)].start()
    # 等待至线程中止
    for i in range(3):
        thread[str(i)].join()
    # 爬取之前爬取失败的二级url
    while len(l0) > 0:
        url = l0[0]
        headers = {}
        res = requests.get(url,headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text,'html.parser')
            o = soup.find(id='pins').find_all('li')
            for y in o:
                try:
                    urls = y.find('a')['href']
                    l = hash(urls)
                    if l not in lh:
                        lh.append(l)
                        l2.append(urls)
                    else:
                        pass
                except:
                    pass
            l0.pop(0)
            print('成功爬取到一组二级url')
        else:
            pass
    # 创建15个新线程
    thread = {}
    for i in range(15):
        thread[str(i)] = MyThread(str(i), str(i))
    # 开启新线程
    for i in range(15):
        thread[str(i)].start()
    # 等待至线程中止
    for i in range(15):
        thread[str(i)].join()
    # 保存爬取失败的三级url和四级url
    my_url(l0,l3)
    print("退出主线程，耗时%s" % (time.time() - start))

