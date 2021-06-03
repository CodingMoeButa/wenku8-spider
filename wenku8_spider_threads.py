#!/usr/bin/python
import requests
import sqlite3
import re
import tomd
import threading

'''
    Title: 针对轻小说文库（wenku8.net）的多线程自动采集器
    Version: 1.1.0
    Author: Ricky
    Github: https://github.com/ricky50575/wenku8-spider
    Website: http://lightnovel.moe/
'''

aid = 0
aid = int(input('Start from aid: '))
cid = 0
errorPages = 0
maxErrorPages = 10
failedArticles = 0

conn = sqlite3.connect('wenku8.db', check_same_thread=False)
c = conn.cursor()

url = 'https://www.wenku8.net/modules/article/reader.php'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }

class downloadArticle(threading.Thread):
    def __init__(self, url, headers, aid, title, author, cid):
        threading.Thread.__init__(self)
        self.url = url
        self.headers = headers
        self.aid = aid
        self.title = title
        self.author = author
        self.cid = cid
    def run(self):
        global failedArticles
        threadLock.acquire()
        cursor = c.execute("SELECT cid FROM article WHERE cid=" + str(self.cid))
        if len(list(cursor))!=0:
            threadLock.release()
            return
        threadLock.release()
        params = {
            'aid': self.aid,
            'cid': self.cid
            }
        try:
            r = requests.get(self.url, params=params, headers=self.headers, timeout=3)
            r.encoding = 'gbk'
            result = re.search('(?<=(<div id="title">))[.\s\S]*?(?=(</div>))', r.text, re.I)
            subtitle = result.group()
            result = re.search('因版权问题，文库不再提供该小说的阅读！', r.text, re.I)
            if result:
                content = ''
            else:
                result = re.search('(?<=(</ul>))[.\s\S]*?(?=(<ul id="contentdp">))', r.text, re.I|re.S)
                content = tomd.convert(result.group())
            threadLock.acquire()
            c.execute("INSERT INTO article (aid,title,author,cid,subtitle,content) \
                VALUES (?,?,?,?,?,?)", (self.aid,self.title,self.author,self.cid,subtitle,content))
            conn.commit()
            print(str(self.aid) + ':' + str(self.cid), self.author + '《' + self.title + '》' + subtitle)
            threadLock.release()
        except requests.exceptions.RequestException:
            failedArticles += 1
            threadLock.acquire()
            print(str(self.aid) + ':' + str(self.cid), '访问失败')
            threadLock.release()

while errorPages < maxErrorPages:
    params = {
        'aid': aid
        }
    try:
        r = requests.get(url, params=params, headers=headers)
        r.encoding = 'gbk'
        result = re.search('<title>出现错误</title>', r.text, re.I)
        if result:
            errorPages += 1
            print(aid, '访问失败，已连续', errorPages, '次失败。')
            aid +=1
        else:
            result = re.search('(?<=(<div id="title">))[.\s\S]*?(?=(</div>))', r.text, re.I)
            title = result.group()
            result = re.search('(?<=(<div id="info">作者：))[.\s\S]*?(?=(</div>))', r.text, re.I)
            author = result.group()
            print(aid, author + '《' + title + '》')
            it = re.finditer('(?<=(<td class="ccss"><a href="https://www.wenku8.net/modules/article/reader.php\?aid='+str(aid)+'&cid=))[.\s\S]*?(?=(">))', r.text, re.I)
            threads = []
            threadLock = threading.Lock()
            for match in it:
                cid = match.group()
                thread = downloadArticle(url, headers, aid, title, author, cid)
                thread.start()
                threads.append(thread)
            for t in threads:
                t.join()
            aid += 1
            errorPages = 0
    except requests.exceptions.RequestException:
        errorPages += 1
        print(aid, '访问失败，已连续', errorPages, '次失败。')
        aid +=1

conn.close()
print('访问失败的章节数：' + str(failedArticles))
input('Press the Enter key to continue...')