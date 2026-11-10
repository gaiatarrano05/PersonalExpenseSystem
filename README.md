# Sistema di gestione delle spese personali e del budget

Progetto per Fondamenti di informatica. Applicazione da console per un singolo
utente, realizzata in Python con database relazionale SQLite.

## Requisiti

- Python **3.10 o successivo**: i menu usano `match/case`.
- Un terminale e permessi di scrittura nella cartella `src`.
- Librerie standard: `os`, `sqlite3`, `datetime`, `decimal`.
- Nessun pacchetto da installare con pip. Non serve un server SQL separato.
- Non e' necessaria la compilazione del sorgente Python.

## Struttura del repository

- `src/main.py`: programma completo.
- `sql/database.sql`: creazione delle tabelle, vincoli e dati di esempio.
- `demo/demo.mp4`: video di un'esecuzione reale con input automatici.
- `README.md`: istruzioni.

## Avvio passo per passo

1. Scaricare ed estrarre il progetto, mantenendo le cartelle `src`, `sql`, `demo`.
2. Aprire il terminale nella cartella principale `PersonalExpenseSystem`.
3. Verificare la versione dell'interprete. Su Windows:

   ```text
   py --version
   ```

4. Avviare il programma. Su Windows:

   ```text
   py src/main.py
   ```

   Su macOS/Linux:

   ```text
   python3 src/main.py
   ```

   Se il comando configurato sul computer e' `python`, usare:

   ```text
   python src/main.py
   ```

5. Al primo avvio viene creato `src/spese.db` con i dati dimostrativi dello
   script SQL. Agli avvii successivi i dati vengono conservati.
6. Usare i numeri del menu. Scegliere `5` per uscire.

Lo script SQL viene letto automaticamente: non va eseguito manualmente prima
dell'avvio. SQLite crea il file del database senza un comando `CREATE DATABASE`.
Il percorso dello script e' calcolato a partire dal sorgente, non dal terminale.
Usare la cartella nuova del progetto corretto, senza copiare database della
versione precedente: il programma non esegue migrazioni di vecchi schemi.

## Funzioni e input

1. Gestione Categorie: nome obbligatorio e non duplicato.
2. Inserisci Spesa: data reale `YYYY-MM-DD`, importo positivo, categoria esistente,
   descrizione facoltativa. Esempio: `2025-01-27`, `12,50`, `Alimentari`.
3. Definisci Budget Mensile: mese `YYYY-MM`, categoria e importo positivo.
   La stessa coppia mese-categoria viene aggiornata, senza creare duplicati.
4. Visualizza Report: totali per categoria, confronto mensile con il budget,
   elenco delle spese ordinate per data.
5. Esci.

Importi in euro con punto o virgola, massimo due cifre decimali e limite
di 1.000.000.000 euro. Valori non finiti e testo non numerico sono rifiutati.
I nomi sono confrontati senza distinzione fra maiuscole e minuscole per i
caratteri ASCII, secondo `COLLATE NOCASE` di SQLite.

## Report e risultati iniziali

| Categoria | Speso gennaio 2025 | Budget | Stato |
| --- | ---: | ---: | --- |
| Alimentari | 320.50 | 300.00 | SUPERAMENTO BUDGET |
| Trasporti | 120.00 | 150.00 | ENTRO IL BUDGET |
| Svago | 40.00 | 50.00 | ENTRO IL BUDGET |

Il report dei budget considera le coppie mese-categoria per cui e' stato
definito un budget. Le altre spese compaiono negli altri due report.
Una spesa pari al budget e' entro il limite. Le categorie senza spese
sono mostrate con totale zero.

## Progettazione e controlli

- `categorie(id PK, nome UNIQUE NOT NULL)`.
- `spese(id PK, data, importo, id_categoria FK, descrizione facoltativa)`.
- `budget(id PK, mese, id_categoria FK, importo, UNIQUE(mese,id_categoria))`.
- Ogni categoria puo' avere zero o piu' spese e zero o piu' budget.
- `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `UNIQUE`, `CHECK` sono espliciti
  nello script. `PRAGMA foreign_keys = ON` attiva le chiavi esterne.
- Il database verifica formato e intervalli di base di data e mese;
  Python controlla anche i giorni effettivamente esistenti nel calendario.
- `Decimal` valida gli importi in ingresso; SQLite li conserva come `REAL`.
  I totali sono arrotondati ai centesimi con `ROUND(..., 2)` prima del confronto.
  E' una scelta didattica: `REAL` usa una rappresentazione approssimata.
- Le query usano parametri `?` per i valori inseriti dall'utente.
- Commit dopo le modifiche; rollback in caso di errore SQL e chiusura finale.
- In Python `input`, `print`, `match/case` svolgono i ruoli che la traccia
  descrive con i costrutti C++ `cin`, `cout`, `switch`.

## Video dimostrativo

`demo/demo.mp4` mostra l'avvio reale del programma, la creazione della categoria
Salute, una spesa di 12.50 euro, un budget iniziale di 10.00 euro, i tre report,
l'aggiornamento del budget a 20.00 euro e l'uscita. Il video e' ottenuto
dall'output reale di una sessione da console con input automatici; non ha audio.

La sessione del video e' eseguita su una copia temporanea: non modifica i dati
iniziali che l'utente trova al primo avvio del progetto scaricato.

## Verifica

Prima della consegna sono state eseguite 45 verifiche automatiche su una copia
temporanea: vincoli SQL, date, importi, duplicati, inserimenti, aggiornamento
budget, report, persistenza, menu e chiusura. I file di test e il database
generato non fanno parte del repository richiesto.
