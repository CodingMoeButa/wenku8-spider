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
