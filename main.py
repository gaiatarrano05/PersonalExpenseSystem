"""Sistema di gestione delle spese personali: Python 3.10+ e SQLite."""

import os
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation


CARTELLA = os.path.dirname(os.path.abspath(__file__))
FILE_SQL = os.path.join(CARTELLA, "..", "sql", "database.sql")
FILE_DB = os.path.join(CARTELLA, "spese.db")


def apri_connessione():
    """Crea schema e dati solo se il database non contiene tabelle utente."""
    conn = sqlite3.connect(FILE_DB)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        tabelle = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        if not tabelle:
            with open(FILE_SQL, encoding="utf-8") as file:
                conn.executescript(file.read())
        nomi = {riga[0] for riga in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )}
        if not {"categorie", "spese", "budget"}.issubset(nomi):
            raise sqlite3.DatabaseError("Schema del database incompleto.")
        return conn
    except (OSError, sqlite3.Error):
        conn.rollback()
        conn.close()
        raise


def chiedi_numero(messaggio):
    """Accetta euro con punto o virgola, al massimo due cifre decimali."""
    testo = input(messaggio).strip().replace(",", ".")
    try:
        valore = Decimal(testo)
        if not valore.is_finite() or valore <= 0 or valore > 1000000000:
            return None
        if valore != valore.quantize(Decimal("0.01")):
            return None
        return float(valore)
    except InvalidOperation:
        return None


def controlla_data(testo, tipo):
    """Controlla formato esatto e validita' del calendario."""
    formato = "%Y-%m-%d" if tipo == "g" else "%Y-%m"
    try:
        data = datetime.strptime(testo, formato)
        canonica = f"{data.year:04d}-{data.month:02d}"
        if tipo == "g":
            canonica += f"-{data.day:02d}"
        return testo == canonica
    except ValueError:
        return False


def prendi_id_cat(conn, nome):
    riga = conn.execute(
        "SELECT id FROM categorie WHERE nome = ?", (nome,)
    ).fetchone()
    return riga[0] if riga else None


def aggiungi_categoria(conn):
    nome = input("Nome della categoria: ").strip()
    if not nome:
        print("Errore: il nome della categoria non puo' essere vuoto.")
        return
    if prendi_id_cat(conn, nome) is not None:
        print("La categoria esiste gia'.")
        return
    conn.execute("INSERT INTO categorie (nome) VALUES (?)", (nome,))
    conn.commit()
    print("Categoria inserita correttamente.")


def aggiungi_spesa(conn):
    data = input("Data (YYYY-MM-DD): ").strip()
    if not controlla_data(data, "g"):
        print("Errore: data non valida; usare YYYY-MM-DD.")
        return
    importo = chiedi_numero("Importo in euro: ")
    if importo is None:
        print("Errore: l'importo deve essere maggiore di zero.")
        print("Usare massimo due decimali e non oltre 1000000000 euro.")
        return
    nome = input("Nome della categoria: ").strip()
    id_categoria = prendi_id_cat(conn, nome)
    if id_categoria is None:
        print("Errore: la categoria non esiste.")
        return
    descrizione = input("Descrizione (facoltativa): ").strip() or None
    conn.execute(
        "INSERT INTO spese (data, importo, id_categoria, descrizione) "
        "VALUES (?, ?, ?, ?)",
        (data, importo, id_categoria, descrizione),
    )
    conn.commit()
    print("Spesa inserita correttamente.")


def imposta_budget(conn):
    mese = input("Mese (YYYY-MM): ").strip()
    if not controlla_data(mese, "m"):
        print("Errore: mese non valido; usare YYYY-MM.")
        return
    nome = input("Nome della categoria: ").strip()
    id_categoria = prendi_id_cat(conn, nome)
    if id_categoria is None:
        print("Errore: la categoria non esiste.")
        return
    importo = chiedi_numero("Budget in euro: ")
    if importo is None:
        print("Errore: budget positivo, massimo due decimali,")
        print("non oltre 1000000000 euro.")
        return
    esiste = conn.execute(
        "SELECT id FROM budget WHERE mese = ? AND id_categoria = ?",
        (mese, id_categoria),
    ).fetchone()
    if esiste:
        conn.execute(
            "UPDATE budget SET importo = ? "
            "WHERE mese = ? AND id_categoria = ?",
            (importo, mese, id_categoria),
        )
    else:
        conn.execute(
            "INSERT INTO budget (mese, id_categoria, importo) "
            "VALUES (?, ?, ?)", (mese, id_categoria, importo),
        )
    conn.commit()
    print("Budget mensile salvato correttamente.")


def stampa_totali(conn):
    righe = conn.execute("""
        SELECT c.nome, ROUND(COALESCE(SUM(s.importo), 0), 2)
        FROM categorie AS c
        LEFT JOIN spese AS s ON s.id_categoria = c.id
        GROUP BY c.id, c.nome
        ORDER BY c.nome
    """).fetchall()
    print("\nTOTALE SPESE PER CATEGORIA")
    if not righe:
        print("Nessuna categoria presente.")
    for nome, totale in righe:
        print(f"{nome}: {totale:.2f} EUR")


def stampa_budget(conn):
    righe = conn.execute("""
        SELECT b.mese, c.nome, b.importo,
               ROUND(COALESCE(SUM(s.importo), 0), 2)
        FROM budget AS b
        JOIN categorie AS c ON c.id = b.id_categoria
        LEFT JOIN spese AS s ON s.id_categoria = b.id_categoria
             AND substr(s.data, 1, 7) = b.mese
        GROUP BY b.id, b.mese, c.nome, b.importo
        ORDER BY b.mese, c.nome
    """).fetchall()
    print("\nSPESE MENSILI VS BUDGET")
    if not righe:
        print("Nessun budget presente.")
    for mese, nome, limite, speso in righe:
        print(f"\nMese: {mese} | Categoria: {nome}")
        print(f"Budget: {limite:.2f} EUR | Speso: {speso:.2f} EUR")
        if speso > limite:
            print("Stato: SUPERAMENTO BUDGET")
        else:
            print("Stato: ENTRO IL BUDGET")


def stampa_lista_spese(conn):
    righe = conn.execute("""
        SELECT s.data, c.nome, s.importo, s.descrizione
        FROM spese AS s
        JOIN categorie AS c ON c.id = s.id_categoria
        ORDER BY s.data, s.id
    """).fetchall()
    print("\nELENCO COMPLETO DELLE SPESE ORDINATE PER DATA")
    if not righe:
        print("Nessuna spesa presente.")
    for data, nome, importo, descrizione in righe:
        print(f"{data} | {nome} | {importo:.2f} EUR | {descrizione or ''}")


def sottomenu_report(conn):
    while True:
        print("\nMENU REPORT")
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs budget")
        print("3. Elenco completo delle spese ordinate per data")
        print("4. Ritorna al menu principale")
        scelta = input("Inserisci la tua scelta: ").strip()
        # match/case realizza la selezione multipla in Python 3.10+.
        match scelta:
            case "1":
                stampa_totali(conn)
            case "2":
                stampa_budget(conn)
            case "3":
                stampa_lista_spese(conn)
            case "4":
                return
            case _:
                print("Scelta non valida. Riprovare.")


def avvia():
    conn = None
    try:
        conn = apri_connessione()
        print("Benvenuto nel sistema di gestione delle spese personali!")
        while True:
            print("\nSISTEMA SPESE PERSONALI")
            print("1. Gestione Categorie")
            print("2. Inserisci Spesa")
            print("3. Definisci Budget Mensile")
            print("4. Visualizza Report")
            print("5. Esci")
            scelta = input("Inserisci la tua scelta: ").strip()
            try:
                match scelta:
                    case "1":
                        aggiungi_categoria(conn)
                    case "2":
                        aggiungi_spesa(conn)
                    case "3":
                        imposta_budget(conn)
                    case "4":
                        sottomenu_report(conn)
                    case "5":
                        print("Arrivederci!")
                        break
                    case _:
                        print("Scelta non valida. Riprovare.")
            except sqlite3.Error as errore:
                conn.rollback()
                print(f"Errore del database: {errore}")
    except (EOFError, KeyboardInterrupt):
        print("\nSessione interrotta. Chiusura del programma.")
    except (OSError, sqlite3.Error) as errore:
        print(f"Impossibile aprire il progetto: {errore}")
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    avvia()
