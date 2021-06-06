#!/usr/bin/python
import sqlite3
import opencc

cid = 0
cid_to = 0
cid = int(input('cid from: '))
cid_to = int(input('cid to: '))

converter = opencc.OpenCC('s2twp.json')

conn = sqlite3.connect('wenku8.db')
c = conn.cursor()

while cid <= cid_to:
    cursor = c.execute("SELECT cid FROM s2twp WHERE cid=" + str(cid))
    if len(list(cursor)) != 0:
        cid += 1
        continue
    cursor = c.execute("SELECT aid,title,author,cid,subtitle,content FROM article WHERE cid=" + str(cid))
    for row in list(cursor):
        aid = row[0]
        title = converter.convert(row[1])
        author = converter.convert(row[2])
        cid = row[3]
        subtitle = str(converter.convert(row[4]))
        content = str(converter.convert(row[5]))
        if subtitle.find('插圖') != -1:
            content = content.replace('[](', '![](')
        c.execute("INSERT INTO s2twp (aid,title,author,cid,subtitle,content) \
            VALUES (?,?,?,?,?,?)", (aid,title,author,cid,subtitle,content))
        conn.commit()
        print(str(aid) + ':' + str(cid), author + '《' + title + '》' + subtitle)
    cid += 1

conn.close()
input('Press the Enter key to continue...')