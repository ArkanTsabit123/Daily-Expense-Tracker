# visualization/chart_service.py

"""
Chart Service
Provides functionalities to generate various charts for expense visualization.
"""

import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict
import logging
import numpy as np

logger = logging.getLogger(__name__)


class ChartService:
    def __init__(self):
        self.output_dir = Path(__file__).parent.parent / "charts"
        self.output_dir.mkdir(exist_ok=True)
        
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
    
    def generate_pie_chart(self, category_data: List[Dict], year: int, month: int) -> str:
        if not category_data:
            raise ValueError("No data for chart generation")
        
        categories = [item['category'] for item in category_data]
        amounts = [item['total'] for item in category_data]
        total_amount = sum(amounts)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
        wedges, texts, autotexts = ax.pie(
            amounts,
            labels=categories,
            autopct=lambda p: f'{p:.1f}%',
            startangle=90,
            colors=colors
        )
        
        plt.setp(autotexts, size=10, weight="bold", color='white')
        plt.setp(texts, size=9)
        
        month_names = [
            'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
            'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
        ]
        
        ax.set_title(
            f'Distribusi Pengeluaran - {month_names[month-1]} {year}\n'
            f'Total: Rp {total_amount:,.0f}',
            fontsize=14, fontweight='bold', pad=20
        )
        
        ax.axis('equal')
        
        legend_labels = [
            f"{cat}: Rp {amt:,.0f}"
            for cat, amt in zip(categories, amounts)
        ]
        
        ax.legend(wedges, legend_labels, title="Kategori", 
                 loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        
        filename = f"expense_chart_{year}_{month:02d}.png"
        filepath = self.output_dir / filename
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
        
        logger.info(f"Chart saved: {filepath}")
        return str(filepath)
    
    def generate_monthly_trend_chart(self, monthly_data: List[Dict]) -> str:
        if not monthly_data:
            raise ValueError("No data for trend chart")
        
        months = [f"{item['month']:02d}/{item['year']}" for item in monthly_data]
        totals = [item['total'] for item in monthly_data]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(months, totals, marker='o', linewidth=2, markersize=8,
               color='#FF6B6B', markerfacecolor='#4ECDC4')
        
        ax.set_title('Trend Pengeluaran Bulanan', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Bulan-Tahun', fontweight='bold')
        ax.set_ylabel('Total Pengeluaran (Rp)', fontweight='bold')
        
        plt.xticks(rotation=45)
        
        for i, total in enumerate(totals):
            ax.annotate(f'Rp {total:,.0f}',
                       (months[i], totals[i]),
                       textcoords="offset points",
                       xytext=(0, 10),
                       ha='center',
                       fontweight='bold')
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filename = "monthly_trend_chart.png"
        filepath = self.output_dir / filename
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Trend chart saved: {filepath}")
        return str(filepath)
    
    def generate_category_trend_chart(self, category_trend_data: List[Dict]) -> str:
        if not category_trend_data:
            raise ValueError("No data for category trend chart")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        categories = list(set(item['category'] for item in category_trend_data))
        
        for category in categories:
            category_data = [item for item in category_trend_data 
                           if item['category'] == category]
            category_data.sort(key=lambda x: (x['year'], x['month']))
            
            months = [f"{item['month']:02d}/{item['year']}" for item in category_data]
            amounts = [item['amount'] for item in category_data]
            
            ax.plot(months, amounts, marker='o', linewidth=2, 
                   label=category, markersize=6)
        
        ax.set_title('Trend Pengeluaran per Kategori', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Bulan-Tahun', fontweight='bold')
        ax.set_ylabel('Total Pengeluaran (Rp)', fontweight='bold')
        
        plt.xticks(rotation=45)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        filename = "category_trend_chart.png"
        filepath = self.output_dir / filename
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Category trend chart saved: {filepath}")
        return str(filepath)