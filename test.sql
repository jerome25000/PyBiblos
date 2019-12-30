
DROP TABLE IF EXISTS AUTHOR;
CREATE TABLE AUTHOR (ID INTEGER, UPDATE_DATE DATE, DATA TEXT);
INSERT INTO AUTHOR (ID, UPDATE_DATE, DATA) VALUES (1, date('now'), '{"id": 1, "name": "Brussolo", "firstname": "Serge"}');
INSERT INTO AUTHOR (ID, UPDATE_DATE, DATA) VALUES (2, date('now'), '{"id": 2, "name": "Priest", "firstname": "Christopher"}');
INSERT INTO AUTHOR (ID, UPDATE_DATE, DATA) VALUES (3, date('now'), '{"id": 3, "name": "Faye", "firstname": "Estelle"}');

DROP TABLE IF EXISTS BOOK;
CREATE TABLE BOOK (ID INTEGER, UPDATE_DATE DATE, DATA TEXT);
INSERT INTO BOOK (ID, UPDATE_DATE, DATA) VALUES (1, date('now'), '{"id": 1, "title": "Les lutteurs immobiles", "year": 1985, "authors": [{"id" : 1, "name": "Brussolo", "firstname": "Serge"}]}');
INSERT INTO BOOK (ID, UPDATE_DATE, DATA) VALUES (2, date('now'), '{"id": 2, "title": "L''adjacent", "year": 2012, "authors": [{"id" : 2, "name": "Priest", "firstname": "Christopher"}]}');
INSERT INTO BOOK (ID, UPDATE_DATE, DATA) VALUES (3, date('now'), '{"id": 3, "title": "Un éclat de givre", "year": 2016, "authors": [{"id" : 3, "name": "Faye", "firstname": "Estelle"}]}');
