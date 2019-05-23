# moutu
某图片网站曾是广大爬虫的目标，本人也跟风以此为目标来做项目练手，无奈该网站早已对图片资源进行了加密（哪怕是非爬虫的正常用户，看到的图片资源也是
来自缓存，刷新一下页面就会返回403）。就在本人准备放弃的时候，却无意间破解了，至于如何破解的这里不方便公开，只能透露下破解了请求头就能拿到资源。

本项目的大致思路：

meizitu1：1、拿到前5个一级url
          2、使用3个线程来构造二级url和爬取三级url，并且爬取失败时将对应的二级url存到一个列表
          3、使用while循环去爬之前爬取失败的二级url，直到拿到所有的三级url
          4、使用15个线程来构造四级url和爬取五级url（存放图片的url）并下载图片
          5、下载图片的同时，爬取失败的三级url和四级url以excel的形式保存
          
meizitu2:1、读取excel中爬取失败的三级url，创建15个线程来构造四级url和爬取五级url（存放图片的url）并下载图片，并且爬取失败时将对应的三级url存
         到一个列表，爬取失败的四级url以excel的形式保存
         2、使用while循环去爬之前爬取失败的三级url，直接下载图片或将爬取失败的四级url以excel的形式保存
         3、读取excel中爬取失败的四级url，创建15个线程来爬取五级url并下载图片，并将爬取失败的四级url存入新的excel中
         （下载图片时只要破解了请求头就肯定返回200）
         
meizitu3:读取新excel中的四级url,使用while循环爬取五级url并下载图片

meizitu4:1、拿到后2个一级url
         2、使用2个线程来构造二级url和爬取三级url（存放图片的url），并且爬取失败时将对应的二级url存到一个列表
         3、使用while循环去爬之前爬取失败的二级url，直到拿到所有的三级url
         4、使用20线程来爬取三级url并下载图片
         
遇到的问题：能破解请求头项目就活，不能破解项目就死。

改进和优化：前3个文件里有太多重复代码，可以进行优化合并，以至于不被绕晕。