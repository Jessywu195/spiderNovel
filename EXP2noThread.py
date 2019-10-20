import requests
import pymongo
import re
import time
from bs4 import BeautifulSoup


# 获取链接
def getHtml(url):
    try:
        header = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}   # 构造请求头
        r = requests.get(url, headers=header, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print("Somthing Wrong!")

# 爬取小说主页
def getHomePage(text):
    soup = BeautifulSoup(text, 'lxml')
    link = soup.find('a',string='一念永恒')
    return link.attrs['href']


def getContent(txt):
    '''
    function:爬取小说内容
    :param url:
    :return:
    '''
    dic = {}
    soup = BeautifulSoup(txt, 'lxml')
    head1 = soup.find('h1')
    content = soup.find('div', class_='showtxt')
    head_txt = head1.get_text()
    # 格式化输出
    [script.extract() for script in soup.find_all('script')]  # 去除script标签
    [br.extract() for br in soup.find_all('br')]              # 去除br标签
    reg1 = re.compile("<[^>]*>")                              # 去除html标签
    content = reg1.sub('',content.prettify())
    content = content.replace('\xa0',' ')
    if head_txt.find('.'):
        head_txt = head_txt.replace('.', '_')

    dic[head_txt] = content
    return dic


def getCharpter(txt, url):
    # 连接数据库
    myClient = pymongo.MongoClient('mongodb://39.105.117.20:40000/')
    myDB = myClient['NovelTest']
    myCol = myDB['一念永恒x']
    soup = BeautifulSoup(txt, 'lxml')
    listmain = soup.find('div', class_='listmain')
    first = listmain.find('a', string='章节目录')    # 找到'章节目录'

    for charpter in first.parent.next_siblings:
        # 过滤掉换行符
        if charpter == '\n':
            continue
        # 过滤非章节部分
        if charpter.a.string == '新书《三寸人间》发布！！！求收藏！！':
            break
        link = charpter.find('a')   # link：章节网址所在的a标签
        url_ = url + link['href']   # url：章节网址
        con_text = getHtml(url_)
        dic = getContent(con_text)
        # 插入数据
        myCol.insert_one(dic)
        print(dic)



def main():
    start = time.perf_counter()
    url = "https://www.biqukan.com"  # 笔趣阁链接
    text = getHtml(url)
    homePage = getHomePage(text)
    homePage = url + homePage  # 小说主页链接
    text_ = getHtml(homePage)  # 解析主页
    getCharpter(text_, url)

    end = time.perf_counter()
    print("final is in 2", end - start)#计算整个爬虫运行所花费的时间。


if __name__ == '__main__':
    main()