-- SQLite: schema e dati dimostrativi. Eseguire su un database vuoto.
-- Il file fisico del database viene creato da sqlite3.connect in Python.
PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

CREATE TABLE categorie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL COLLATE NOCASE UNIQUE,
    CHECK (length(trim(nome)) > 0)
);

CREATE TABLE spese (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    importo REAL NOT NULL CHECK (importo > 0 AND importo <= 1000000000),
    id_categoria INTEGER NOT NULL,
    descrizione TEXT,
    CHECK (data GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
           AND substr(data, 1, 4) BETWEEN '0001' AND '9999'
           AND substr(data, 6, 2) BETWEEN '01' AND '12'
           AND substr(data, 9, 2) BETWEEN '01' AND '31'),
    FOREIGN KEY (id_categoria) REFERENCES categorie(id)
);

CREATE TABLE budget (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mese TEXT NOT NULL,
    id_categoria INTEGER NOT NULL,
    importo REAL NOT NULL CHECK (importo > 0 AND importo <= 1000000000),
    CHECK (mese GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
           AND substr(mese, 1, 4) BETWEEN '0001' AND '9999'
           AND substr(mese, 6, 2) BETWEEN '01' AND '12'),
    UNIQUE (mese, id_categoria),
    FOREIGN KEY (id_categoria) REFERENCES categorie(id)
);

-- Dati dimostrativi: gennaio 2025, come negli esempi della traccia.
INSERT INTO categorie (nome) VALUES ('Alimentari');
INSERT INTO categorie (nome) VALUES ('Trasporti');
INSERT INTO categorie (nome) VALUES ('Svago');

INSERT INTO spese (data, importo, id_categoria, descrizione)
VALUES ('2025-01-15', 25.00, 1, 'Pranzo');
INSERT INTO spese (data, importo, id_categoria, descrizione)
VALUES ('2025-01-18', 295.50, 1, 'Spesa mensile');
INSERT INTO spese (data, importo, id_categoria, descrizione)
VALUES ('2025-01-20', 120.00, 2, 'Abbonamento bus');
INSERT INTO spese (data, importo, id_categoria, descrizione)
VALUES ('2025-01-25', 40.00, 3, 'Cinema');

INSERT INTO budget (mese, id_categoria, importo) VALUES ('2025-01', 1, 300);
INSERT INTO budget (mese, id_categoria, importo) VALUES ('2025-01', 2, 150);
INSERT INTO budget (mese, id_categoria, importo) VALUES ('2025-01', 3, 50);
COMMIT;
