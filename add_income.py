# add_income.py
import sqlite3

DB_PATH = "data/expenses.db"

def add_incomes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Cek apakah tabel incomes ada
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incomes'")
    if not cursor.fetchone():
        print("❌ Tabel incomes tidak ada!")
        print("📌 Jalankan aplikasi GUI/CLI dulu untuk membuat tabel")
        conn.close()
        return
    
    # Data income
    incomes = [
        ('2026-07-01', 'Salary', 5000000, 'Monthly salary - July', 0),
        ('2026-07-05', 'Bonus', 2000000, 'Performance bonus', 0),
        ('2026-07-10', 'Freelance', 1500000, 'Freelance project', 0),
        ('2026-06-25', 'Investment', 1000000, 'Dividend payment', 0),
        ('2026-06-15', 'Salary', 5000000, 'Monthly salary - June', 0),
        ('2026-06-01', 'Rental income', 3000000, 'Property rental', 1),
        ('2026-05-20', 'Bonus', 1500000, 'Quarterly bonus', 0),
        ('2026-05-10', 'Freelance', 800000, 'Website project', 0),
        ('2026-04-15', 'Salary', 4500000, 'Monthly salary - April', 0),
        ('2026-04-01', 'Side business', 2000000, 'Side business income', 0),
    ]
    
    # Insert incomes
    inserted = 0
    for date, source, amount, desc, recurring in incomes:
        try:
            cursor.execute("""
                INSERT INTO incomes (date, source, amount, description, is_recurring)
                VALUES (?, ?, ?, ?, ?)
            """, (date, source, amount, desc, recurring))
            inserted += 1
        except sqlite3.IntegrityError:
            print(f"⚠️ Data sudah ada: {source} - {date}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {inserted} incomes berhasil ditambahkan!")

if __name__ == "__main__":
    add_incomes()