# project portofolio/junior project/daily-expense-tracker/main.py

"""
Main Module
Entry point for the daily-expense-tracker application.
"""

import os
import sys
from datetime import datetime
from decimal import Decimal

from config.database_config import DatabaseConfig
from services.expense_service import ExpenseService
from services.export_service import ExportService
from services.database_service import DatabaseService
from utils.date_utils import get_current_month_year, get_month_name
from utils.formatters import format_currency, format_date, format_category, format_percentage
from utils.validation import validate_date, validate_amount, parse_amount
from visualization.chart_service import ChartService


class ExpenseTrackerApp:
    def __init__(self):
        self.expense_service = ExpenseService()
        self.export_service = ExportService()
        self.database_service = DatabaseService()
        self.chart_service = ChartService()
        self.chart_service = ChartService()
        self.current_month, self.current_year = get_current_month_year()
        
        db_config = DatabaseConfig()
        db_config.initialize_database()
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self, title):
        self.clear_screen()
        print("=" * 60)
        print(f"DAILY EXPENSE TRACKER".center(60))
        print(f"{title}".center(60))
        print("=" * 60)
        print()
    
    def wait_for_enter(self):
        input("\nPress Enter to continue...")
    
    def input_expense(self):
        self.display_header("TAMBAH PENGELUARAN BARU")
        
        try:
            while True:
                date_input = input("Tanggal (YYYY-MM-DD) [kosongkan untuk hari ini]: ").strip()
                if not date_input:
                    date_input = datetime.now().strftime('%Y-%m-%d')
                    break
                elif validate_date(date_input):
                    break
                else:
                    print("Format tanggal tidak valid. Gunakan format YYYY-MM-DD")
            
            categories = self.expense_service.get_available_categories()
            print("\nPilih Kategori:")
            for i, category in enumerate(categories, 1):
                print(f" {i}. {format_category(category)}")
            
            while True:
                try:
                    cat_choice = int(input(f"\nPilih kategori (1-{len(categories)}): "))
                    if 1 <= cat_choice <= len(categories):
                        category = categories[cat_choice - 1]
                        break
                    else:
                        print("Pilihan tidak valid")
                except ValueError:
                    print("Masukkan angka")
            
            while True:
                amount_input = input("\nJumlah Pengeluaran: Rp ").strip()
                if validate_amount(amount_input):
                    amount = parse_amount(amount_input)
                    break
                else:
                    print("Jumlah tidak valid")
            
            description = input("\nKeterangan (opsional): ").strip()
            
            print(f"\nRingkasan Pengeluaran:")
            print(f" Tanggal : {format_date(date_input)}")
            print(f" Kategori : {format_category(category)}")
            print(f" Jumlah : {format_currency(amount)}")
            print(f" Keterangan : {description or '-'}")
            
            confirm = input("\nSimpan pengeluaran? (y/n): ").lower()
            
            if confirm == 'y':
                result = self.expense_service.create_expense(
                    date_input, category, str(amount), description
                )
                
                if result['success']:
                    print(result['message'])
                else:
                    print(result['error'])
            else:
                print("Pengeluaran dibatalkan")
                
        except KeyboardInterrupt:
            print("\nInput dibatalkan")
        except Exception as e:
            print(f"Error: {e}")
        
        self.wait_for_enter()
    
    def view_history(self):
        self.display_header("HISTORY PENGELUARAN")
        
        try:
            print("Filter Options:")
            print("1. Lihat semua")
            print("2. Filter berdasarkan bulan")
            print("3. Filter berdasarkan kategori")
            print("4. Filter bulan dan kategori")
            
            choice = input("\nPilih filter (1-4): ").strip()
            filters = {}
            
            if choice in ['2', '4']:
                year = input("Tahun (YYYY): ").strip()
                month = input("Bulan (1-12): ").strip()
                if year.isdigit() and month.isdigit():
                    filters['year'] = int(year)
                    filters['month'] = int(month)
            
            if choice in ['3', '4']:
                categories = self.expense_service.get_available_categories()
                print("\nKategori tersedia:")
                for i, cat in enumerate(categories, 1):
                    print(f"{i}. {cat}")
                
                cat_choice = input("Pilih kategori: ").strip()
                if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                    filters['category'] = categories[int(cat_choice) - 1]
            
            expenses = self.expense_service.get_expense_history(filters)
            
            if not expenses:
                print("\nTidak ada data pengeluaran")
                self.wait_for_enter()
                return
            
            total = sum(expense['amount'] for expense in expenses)
            print(f"\nTotal {len(expenses)} transaksi: {format_currency(Decimal(total))}")
            
            print("\n" + "-" * 80)
            print(f"{'Tanggal':12} {'Kategori':20} {'Jumlah':15} {'Keterangan':25}")
            print("-" * 80)
            
            for expense in expenses:
                print(f"{format_date(expense['date']):12} "
                      f"{format_category(expense['category']):20} "
                      f"{format_currency(Decimal(expense['amount'])):15} "
                      f"{expense['description'][:23]:25}")
            
            print("-" * 80)
            
            export = input("\nExport ke file? (y/n): ").lower()
            
            if export == 'y':
                format_choice = input("Format (1-CSV, 2-Excel): ").strip()
                
                if format_choice == '1':
                    filepath = self.export_service.export_to_csv(expenses)
                    print(f"Data diexport ke: {filepath}")
                elif format_choice == '2':
                    filepath = self.export_service.export_to_excel(expenses)
                    print(f"Data diexport ke: {filepath}")
                    
        except Exception as e:
            print(f"Error: {e}")
        
        self.wait_for_enter()
    
    def monthly_summary(self):
        self.display_header("RINGKASAN BULANAN")
        
        try:
            year = input(f"Tahun [{self.current_year}]: ").strip()
            month = input(f"Bulan (1-12) [{self.current_month}]: ").strip()
            
            year = int(year) if year.isdigit() else self.current_year
            month = int(month) if month.isdigit() and 1 <= int(month) <= 12 else self.current_month
            
            analysis = self.expense_service.get_monthly_analysis(year, month)
            
            print(f"\nRingkasan Pengeluaran {get_month_name(month)} {year}")
            print("=" * 50)
            print(f"Total Pengeluaran: {format_currency(Decimal(analysis['total_expenses']))}")
            print(f"Jumlah Kategori : {len(analysis['category_breakdown'])}")
            
            print("\nBreakdown per Kategori:")
            print("-" * 50)
            
            for item in analysis['category_breakdown']:
                percentage = item.get('percentage', 0)
                print(f"{format_category(item['category']):25} "
                      f"{format_currency(Decimal(item['total'])):15} "
                      f"({percentage:.1f}%)")
            
            export_report = input("\nExport laporan lengkap? (y/n): ").lower()
            
            if export_report == 'y':
                expenses = self.expense_service.get_expense_history({'year': year, 'month': month})
                filepath = self.export_service.export_monthly_report(analysis, expenses)
                print(f"Laporan diexport ke: {filepath}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        self.wait_for_enter()

    def generate_chart_menu(self):
        self.display_header("GENERATE CHART")
        
        try:
            year = input(f"Tahun [{self.current_year}]: ").strip()
            month = input(f"Bulan (1-12) [{self.current_month}]: ").strip()
            
            year = int(year) if year.isdigit() else self.current_year
            month = int(month) if month.isdigit() and 1 <= int(month) <= 12 else self.current_month
            
            analysis = self.expense_service.get_monthly_analysis(year, month)
            
            if not analysis.get('category_breakdown'):
                print("Tidak ada data untuk generate chart")
                self.wait_for_enter()
                return
            
            print(f"\nData untuk {month}/{year}:")
            print(f"   Total pengeluaran: {format_currency(Decimal(analysis['total_expenses']))}")
            print(f"   Jumlah kategori: {len(analysis['category_breakdown'])}")
            
            confirm = input("\nGenerate pie chart? (y/n): ").lower()
            
            if confirm == 'y':
                chart_path = self.chart_service.generate_pie_chart(
                    analysis['category_breakdown'], year, month
                )
                print(f"\nChart berhasil digenerate")
                print(f"File: {chart_path}")
                
                view_chart = input("\nTampilkan chart? (y/n): ").lower()
                if view_chart == 'y':
                    import os
                    if os.name == 'nt':
                        os.startfile(chart_path)
                    else:
                        print(f"Open file manually: {chart_path}")
            
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error generating chart: {e}")
        
        self.wait_for_enter()
    
    def view_monthly_analysis(self):
        self.display_header("ANALISIS BULANAN")
        
        try:
            year = input(f"Tahun [{self.current_year}]: ").strip()
            month = input(f"Bulan (1-12) [{self.current_month}]: ").strip()
            
            year = int(year) if year.isdigit() else self.current_year
            month = int(month) if month.isdigit() and 1 <= int(month) <= 12 else self.current_month
            
            analysis = self.expense_service.get_monthly_analysis(year, month)
            
            month_names = [
                'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
            ]
            
            print(f"\nAnalisis Pengeluaran {month_names[month-1]} {year}")
            print("=" * 60)
            
            total = analysis.get('total_expenses', 0)
            print(f"Total Pengeluaran: {format_currency(Decimal(total))}")
            print(f"Jumlah Transaksi: {analysis.get('transaction_count', 0)}")
            print(f"Rata-rata: {format_currency(Decimal(total/max(analysis.get('transaction_count', 1), 1)))}")
            
            print("\nBreakdown per Kategori:")
            print("-" * 60)
            print(f"{'Kategori':25} {'Jumlah':15} {'Persentase':10}")
            print("-" * 60)
            
            for item in analysis.get('category_breakdown', []):
                category = format_category(item['category'])
                amount = format_currency(Decimal(item['total']))
                percentage = format_percentage(item.get('percentage', 0))
                print(f"{category:25} {amount:15} {percentage:10}")
            
            generate_chart = input("\nGenerate chart? (y/n): ").lower()
            if generate_chart == 'y':
                self.generate_chart_menu()
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.wait_for_enter()

    def generate_chart_menu(self):
        self.display_header("GENERATE CHART")
        
        try:
            year = input(f"Tahun [{self.current_year}]: ").strip()
            month = input(f"Bulan (1-12) [{self.current_month}]: ").strip()
            
            year = int(year) if year.isdigit() else self.current_year
            month = int(month) if month.isdigit() and 1 <= int(month) <= 12 else self.current_month
            
            analysis = self.expense_service.get_monthly_analysis(year, month)
            
            if not analysis.get('category_breakdown'):
                print("Tidak ada data untuk generate chart")
                self.wait_for_enter()
                return
            
            print(f"\nData untuk {month}/{year}:")
            print(f"   Total pengeluaran: {format_currency(Decimal(analysis['total_expenses']))}")
            print(f"   Jumlah kategori: {len(analysis['category_breakdown'])}")
            
            confirm = input("\nGenerate pie chart? (y/n): ").lower()
            
            if confirm == 'y':
                chart_path = self.chart_service.generate_pie_chart(
                    analysis['category_breakdown'], year, month
                )
                print(f"\nChart berhasil digenerate")
                print(f"File: {chart_path}")
                
                view_chart = input("\nTampilkan chart? (y/n): ").lower()
                if view_chart == 'y':
                    import os
                    if os.name == 'nt':
                        os.startfile(chart_path)
                    else:
                        print(f"Open file manually: {chart_path}")
            
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error generating chart: {e}")
        
        self.wait_for_enter()
    
    def view_monthly_analysis(self):
        self.display_header("ANALISIS BULANAN")
        
        try:
            year = input(f"Tahun [{self.current_year}]: ").strip()
            month = input(f"Bulan (1-12) [{self.current_month}]: ").strip()
            
            year = int(year) if year.isdigit() else self.current_year
            month = int(month) if month.isdigit() and 1 <= int(month) <= 12 else self.current_month
            
            analysis = self.expense_service.get_monthly_analysis(year, month)
            
            month_names = [
                'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
            ]
            
            print(f"\nAnalisis Pengeluaran {month_names[month-1]} {year}")
            print("=" * 60)
            
            total = analysis.get('total_expenses', 0)
            print(f"Total Pengeluaran: {format_currency(Decimal(total))}")
            print(f"Jumlah Transaksi: {analysis.get('transaction_count', 0)}")
            print(f"Rata-rata: {format_currency(Decimal(total/max(analysis.get('transaction_count', 1), 1)))}")
            
            print("\nBreakdown per Kategori:")
            print("-" * 60)
            print(f"{'Kategori':25} {'Jumlah':15} {'Persentase':10}")
            print("-" * 60)
            
            for item in analysis.get('category_breakdown', []):
                category = format_category(item['category'])
                amount = format_currency(Decimal(item['total']))
                percentage = format_percentage(item.get('percentage', 0))
                print(f"{category:25} {amount:15} {percentage:10}")
            
            generate_chart = input("\nGenerate chart? (y/n): ").lower()
            if generate_chart == 'y':
                self.generate_chart_menu()
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.wait_for_enter()
    
    def export_data_menu(self):
        self.display_header("EXPORT DATA")
        
        try:
            print("Pilih jenis export:")
            print("1. Export data transaksi")
            print("2. Export laporan bulanan")
            
            choice = input("\nPilih jenis (1-2): ").strip()
            
            if choice == '1':
                self.export_transactions()
            elif choice == '2':
                self.export_monthly_report_menu()
            else:
                print("Pilihan tidak valid")
                
        except Exception as e:
            print(f"Error: {e}")
        
        self.wait_for_enter()
    
    def export_transactions(self):
        print("\nPilih data yang akan diexport:")
        print("1. Semua data")
        print("2. Data bulan tertentu")
        
        choice = input("Pilih (1-2): ").strip()
        filters = {}
        
        if choice == '2':
            year = input("Tahun (YYYY): ").strip()
            month = input("Bulan (1-12): ").strip()
            
            if year.isdigit() and month.isdigit():
                filters['year'] = int(year)
                filters['month'] = int(month)
        
        expenses = self.expense_service.get_expense_history(filters)
        
        if not expenses:
            print("Tidak ada data untuk diexport")
            return
        
        format_choice = input("Format (1-CSV, 2-Excel): ").strip()
        
        if format_choice == '1':
            filepath = self.export_service.export_to_csv(expenses)
            print(f"Data diexport ke: {filepath}")
        elif format_choice == '2':
            filepath = self.export_service.export_to_excel(expenses)
            print(f"Data diexport ke: {filepath}")
        else:
            print("Format tidak valid")
    
    def export_monthly_report_menu(self):
        year = input(f"Tahun [{self.current_year}]: ").strip()
        month = input(f"Bulan (1-12) [{self.current_month}]: ").strip()
        
        year = int(year) if year.isdigit() else self.current_year
        month = int(month) if month.isdigit() and 1 <= int(month) <= 12 else self.current_month
        
        analysis = self.expense_service.get_monthly_analysis(year, month)
        expenses = self.expense_service.get_expense_history({'year': year, 'month': month})
        
        if not expenses:
            print("Tidak ada data untuk laporan")
            return
        
        filepath = self.export_service.export_monthly_report(analysis, expenses)
        print(f"Laporan bulanan diexport ke: {filepath}")
    
    def main_menu(self):
        while True:
            self.display_header("MENU UTAMA")
            
            print("1. Tambah Pengeluaran")
            print("2. Lihat History")
            print("3. Analisis Bulanan")
            print("4. Generate Chart")
            print("5. Export Data")
            print("6. Keluar")
            
            choice = input("\nPilih menu (1-6): ").strip()
            
            if choice == '1':
                self.input_expense()
            elif choice == '2':
                self.view_history()
            elif choice == '3':
                self.view_monthly_analysis()  
            elif choice == '4':
                self.generate_chart_menu()    
            elif choice == '5':
                self.export_data_menu()
            elif choice == '6':
                print("\nTerima kasih telah menggunakan Expense Tracker")
                break
            else:
                print("Pilihan tidak valid")
                self.wait_for_enter()


def main():
    app = ExpenseTrackerApp()
    app.main_menu()


if __name__ == "__main__":
    main()