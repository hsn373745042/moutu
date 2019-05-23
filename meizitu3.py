import requests
import os
from bs4 import BeautifulSoup
import re
import openpyxl

# 读取爬取失败的四级url
def read_url1():
    l = []
    wb = openpyxl.load_workbook('./meizi1.xlsx')
    sheet = wb['url']
    for i in sheet['A']:
        l.append(i.value)
    return l

# 读取爬取失败的四级url
l0 = read_url1()

# 爬取之前爬取失败的四级url
while len(l0) > 0:
    url = l0[0]
    headers = {}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text,'html.parser')
        urls = soup.find(class_='main-image').find('img')['src']
        try:
            title = soup.find(class_='main-image').find('img')['alt'].replace('：','')
            if not os.path.exists('d:\\python\\meizitu\\' + title):
                os.mkdir('d:\\python\\meizitu\\' + title)
            else:
                pass
        except:
            try:
                title = soup.find(class_='main-image').find('img')['alt'].replace('?','')
                if not os.path.exists('d:\\python\\meizitu\\' + title):
                    os.mkdir('d:\\python\\meizitu\\' + title)
                else:
                    pass
            except:
                try:
                    title = soup.find(class_='main-image').find('img')['alt'].replace(':', '')
                    if not os.path.exists('d:\\python\\meizitu\\' + title):
                        os.mkdir('d:\\python\\meizitu\\' + title)
                    else:
                        pass
                except:
                    title = soup.find(class_='main-image').find('img')['alt']
                    if not os.path.exists('d:\\python\\meizitu\\' + title):
                        os.mkdir('d:\\python\\meizitu\\'+title)
                    else:
                        pass
        name = re.findall('.*?(\d.*)',urls)[0].replace('/', '_')
        headers = {}
        res = requests.get(urls, headers=headers,timeout=60)
        with open('d:/python/meizitu/' + title + '/' + name, 'wb') as f:
            f.write(res.content)
        l0.pop(0)
        print('成功爬取到一张图片')
    elif 400 <= res.status_code < 500:
        l0.pop(0)
        print('一张图片无法爬取')
    else:
        pass