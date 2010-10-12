#!/usr/bin/python
# fill the resolver database with test data

import pyPgSQL
from pyPgSQL import libpq

conn = libpq.PQconnectdb("user=croddy password=p4ss!@#$ dbname=resolver hostaddr=127.0.0.1 port=5432")

words = ["foo", "bar", "baz", "quux"]

for part1 in words:
    for part2 in words:
        for part3 in words:
            c = 0
            while c < 32767:
                conn.query(
                    "INSERT INTO purls (path, url) VALUES ('" +
                    "/" + part1 + "/" + part2 + "/" + part3 + "/" + 
                    str(c) + "', 'http://localhost/')"
                )
                c = c+1
        
