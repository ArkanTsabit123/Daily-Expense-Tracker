# visualization/chart_service.py

"""
Chart Service
Provides functionalities to generate various charts for expense visualization.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


class ChartService:
    """Service for generating charts from expense data"""
    
    def __init__(self):
        self.output_dir = Path(__file__).parent.parent / "charts"
        self.output_dir.mkdir(exist_ok=True)

        # ============================================================
        # FIX: Gunakan font yang tersedia di Windows
        # ============================================================
        try:
            # Coba gunakan font yang tersedia di Windows
            from matplotlib import font_manager
            available_fonts = [f.name for f in font_manager.fontManager.ttflist]
            
            # Prioritaskan font yang umum di Windows
            preferred_fonts = ['Segoe UI', 'Arial', 'Tahoma', 'DejaVu Sans', 'sans-serif']
            
            for font in preferred_fonts:
                if font in available_fonts or font == 'sans-serif':
                    plt.rcParams["font.family"] = font
                    break
            else:
                plt.rcParams["font.family"] = "sans-serif"
                
            plt.rcParams["axes.unicode_minus"] = False
            
        except Exception:
            # Fallback jika error
            plt.rcParams["font.family"] = "sans-serif"
            plt.rcParams["axes.unicode_minus"] = False

    def generate_pie_chart(
        self, 
        category_data: List[Dict], 
        month: int, 
        year: int
    ) -> Optional[str]:
        """
        Generate pie chart from category data
        
        Args:
            category_data: List of dict with 'category' and 'total'
            month: Month number (1-12)
            year: Year
            
        Returns:
            Path to saved chart or None if error
        """
        # ============================================================
        # VALIDASI DATA
        # ============================================================
        if not category_data or len(category_data) == 0:
            logger.warning("No data for chart generation")
            print("❌ No data available for pie chart")
            return None
        
        # Validasi format data
        for item in category_data:
            if 'category' not in item or 'total' not in item:
                logger.error("Invalid category data format")
                print("❌ Invalid category data format")
                return None
        
        # Filter data dengan total > 0
        valid_data = [item for item in category_data if item.get('total', 0) > 0]
        
        if not valid_data:
            logger.warning("No valid category data (all totals are 0)")
            print("❌ No valid data for pie chart (all categories have 0 total)")
            return None

        try:
            categories = [item["category"] for item in valid_data]
            amounts = [item["total"] for item in valid_data]
            total_amount = sum(amounts)

            fig, ax = plt.subplots(figsize=(12, 8))

            colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
            wedges, texts, autotexts = ax.pie(
                amounts,
                labels=categories,
                autopct=lambda p: f"{p:.1f}%",
                startangle=90,
                colors=colors,
            )

            plt.setp(autotexts, size=10, weight="bold", color="white")
            plt.setp(texts, size=9)

            # ============================================================
            # FIX: Month names safe access
            # ============================================================
            month_names = [
                "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"
            ]
            
            month_name = month_names[month - 1] if 1 <= month <= 12 else f"Bulan {month}"

            ax.set_title(
                f"Distribusi Pengeluaran - {month_name} {year}\n"
                f"Total: Rp {total_amount:,.0f}",
                fontsize=14,
                fontweight="bold",
                pad=20,
            )

            ax.axis("equal")

            legend_labels = [f"{cat}: Rp {amt:,.0f}" for cat, amt in zip(categories, amounts)]

            ax.legend(
                wedges,
                legend_labels,
                title="Kategori",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
            )

            plt.tight_layout()

            filename = f"expense_chart_{year}_{month:02d}.png"
            filepath = self.output_dir / filename

            plt.savefig(filepath, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
            plt.close()

            logger.info(f"Chart saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating pie chart: {e}")
            print(f"❌ Error generating pie chart: {e}")
            return None

    def generate_monthly_trend_chart(self, monthly_data: List[Dict]) -> Optional[str]:
        """
        Generate monthly trend chart
        
        Args:
            monthly_data: List of dict with 'month', 'year', 'total'
            
        Returns:
            Path to saved chart or None if error
        """
        # ============================================================
        # VALIDASI DATA
        # ============================================================
        if not monthly_data or len(monthly_data) == 0:
            logger.warning("No data for trend chart")
            print("❌ No data for trend chart")
            return None
        
        # Validasi format data
        for item in monthly_data:
            if 'month' not in item or 'year' not in item or 'total' not in item:
                logger.error("Invalid monthly data format")
                print("❌ Invalid monthly data format")
                return None

        try:
            months = [f"{item['month']:02d}/{item['year']}" for item in monthly_data]
            totals = [item["total"] for item in monthly_data]

            fig, ax = plt.subplots(figsize=(12, 6))

            ax.plot(
                months,
                totals,
                marker="o",
                linewidth=2,
                markersize=8,
                color="#FF6B6B",
                markerfacecolor="#4ECDC4",
            )

            ax.set_title("Trend Pengeluaran Bulanan", fontsize=14, fontweight="bold", pad=20)
            ax.set_xlabel("Bulan-Tahun", fontweight="bold")
            ax.set_ylabel("Total Pengeluaran (Rp)", fontweight="bold")

            plt.xticks(rotation=45)

            for i, total in enumerate(totals):
                ax.annotate(
                    f"Rp {total:,.0f}",
                    (months[i], totals[i]),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontweight="bold",
                )

            ax.grid(True, alpha=0.3)
            plt.tight_layout()

            filename = "monthly_trend_chart.png"
            filepath = self.output_dir / filename

            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close()

            logger.info(f"Trend chart saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating trend chart: {e}")
            print(f"❌ Error generating trend chart: {e}")
            return None

    def generate_category_trend_chart(self, category_trend_data: List[Dict]) -> Optional[str]:
        """
        Generate category trend chart
        
        Args:
            category_trend_data: List of dict with 'category', 'month', 'year', 'amount'
            
        Returns:
            Path to saved chart or None if error
        """
        # ============================================================
        # VALIDASI DATA
        # ============================================================
        if not category_trend_data or len(category_trend_data) == 0:
            logger.warning("No data for category trend chart")
            print("❌ No data for category trend chart")
            return None
        
        # Validasi format data
        for item in category_trend_data:
            required_keys = ['category', 'month', 'year', 'amount']
            if not all(key in item for key in required_keys):
                logger.error("Invalid category trend data format")
                print("❌ Invalid category trend data format")
                return None

        try:
            fig, ax = plt.subplots(figsize=(14, 8))

            categories = list(set(item["category"] for item in category_trend_data))

            for category in categories:
                category_data = [item for item in category_trend_data if item["category"] == category]
                category_data.sort(key=lambda x: (x["year"], x["month"]))

                months = [f"{item['month']:02d}/{item['year']}" for item in category_data]
                amounts = [item["amount"] for item in category_data]

                ax.plot(months, amounts, marker="o", linewidth=2, label=category, markersize=6)

            ax.set_title("Trend Pengeluaran per Kategori", fontsize=14, fontweight="bold", pad=20)
            ax.set_xlabel("Bulan-Tahun", fontweight="bold")
            ax.set_ylabel("Total Pengeluaran (Rp)", fontweight="bold")

            plt.xticks(rotation=45)
            ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
            ax.grid(True, alpha=0.3)

            plt.tight_layout()

            filename = "category_trend_chart.png"
            filepath = self.output_dir / filename

            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close()

            logger.info(f"Category trend chart saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating category trend chart: {e}")
            print(f"❌ Error generating category trend chart: {e}")
            return None