# wenku8-spider
## wenku8.db
```SQL
CREATE TABLE article (
    aid      INT  NOT NULL,
    title    TEXT NOT NULL,
    author   TEXT,
    cid      INT  PRIMARY KEY
                  NOT NULL,
    subtitle TEXT NOT NULL,
    content  TEXT
);
```
## 已知問題
1.由於pyquery的漏洞，採集到某個章節時，採集程式會崩潰。

2.多執行緒版本存在內存溢出問題。
