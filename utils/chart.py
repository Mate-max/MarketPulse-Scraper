import matplotlib.pyplot as plt
from typing import List, Tuple
from datetime import datetime

def generate_price_chart(product_title: str, history_data: List[Tuple[datetime, float]], output_filename: str = "chart.png") -> str:
    """
    history_data: [(datetime, price), ...]
    ქმნის ფასების ცვლილების გრაფიკს და ინახავს სურათად.
    """
    if not history_data:
        return None

    # თარიღების ტექსტურ ფორმატში გადაყვანა კონვერტაციის შეცდომის თავიდან ასაცილებლად
    dates_str = [item[0].strftime('%d/%m %H:%M') for item in history_data]
    prices = [item[1] for item in history_data]

    # გრაფიკის სტილის გამართვა
    plt.figure(figsize=(9, 4.5))
    plt.plot(dates_str, prices, marker='o', linestyle='-', color='#0088cc', linewidth=2.5, markersize=7)

    plt.title(f"ფასის ისტორია: {product_title[:30]}...", fontsize=12, fontweight='bold', pad=15)
    plt.xlabel("თარიღი/დრო", fontsize=10)
    plt.ylabel("ფასი (GEL)", fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)

    # თარიღების წარწერების გადახრა უკეთესი აღქმადობისთვის
    plt.xticks(rotation=30, ha='right', fontsize=9)
    plt.tight_layout()

    plt.savefig(output_filename, dpi=150)
    plt.close()

    return output_filename