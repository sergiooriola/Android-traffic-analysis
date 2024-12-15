import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add the root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parse_logs import parse_logs

def create_directories(base_dir, analysis_name):
    """Create directories for storing images."""
    analysis_dir = os.path.join(base_dir, analysis_name)
    os.makedirs(analysis_dir, exist_ok=True)
    return analysis_dir

def analyze_monkey_vs_appium(results):
    """Analyze differences between Exerciser Monkey and Appium."""
    data = []

    # Filtrar solo los directorios relevantes para este análisis
    relevant_directories = ["case1_logging", "case1_loggingAppium"]

    for dir_name in relevant_directories:
        if dir_name in results:
            for app_name, app_results in results[dir_name].items():
                if dir_name == "case1_logging":
                    herramienta = "Exerciser Monkey"
                elif dir_name == "case1_loggingAppium":
                    herramienta = "Appium"
                else:
                    herramienta = dir_name  # En caso de que haya un nombre de directorio inesperado
    
                data.append({
                    "Herramienta": herramienta,
                    "Aplicación": app_name,
                    "Total PII": app_results["dynamic_other_pii_count"],
                    "Tipos PII": set(app_results["dynamic_other_pii_values"].keys()),
                    "Dominios únicos": len(app_results["dynamic_unique_domains"])
                })
    
    df = pd.DataFrame(data)

    if df.empty:
        print("No hay datos para analizar. Verifique los directorios de resultados.")
        return

    # Crear directorios para guardar imágenes
    base_dir = "analysis_images"
    analysis_dir = create_directories(base_dir, "case1_monkey_vs_appium")

    # Resumen tabular
    summary = (
        df.groupby("Herramienta").agg({
            "Total PII": "sum",
            "Tipos PII": lambda x: len(set.union(*x)),  # Unir todos los conjuntos y contar los únicos
            "Dominios únicos": "sum"
        }).reset_index()
    )

    # Gráfico 1: Número total de datos personales transferidos
    plt.figure(figsize=(10, 6))
    sns.barplot(data=summary, x="Herramienta", y="Total PII", hue="Herramienta", palette="Blues_d", dodge=False, legend=False)
    plt.title("Número total de datos personales transferidos por herramienta")
    plt.xlabel("Herramienta de interacción")
    plt.ylabel("Total de datos personales")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "total_pii_transferred.png"))
    plt.close()

    # Gráfico 2: Número de tipos de datos personales transferidos
    plt.figure(figsize=(10, 6))
    sns.barplot(data=summary, x="Herramienta", y="Tipos PII", hue="Herramienta", palette="Greens_d", dodge=False, legend=False)
    plt.title("Tipos de datos personales transferidos por herramienta")
    plt.xlabel("Herramienta de interacción")
    plt.ylabel("Número de tipos de PII")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "types_of_pii_transferred.png"))
    plt.close()

    # Gráfico 3: Número de dominios únicos
    plt.figure(figsize=(10, 6))
    sns.barplot(data=summary, x="Herramienta", y="Dominios únicos", hue="Herramienta", palette="Reds_d", dodge=False, legend=False)
    plt.title("Número de dominios únicos por herramienta")
    plt.xlabel("Herramienta de interacción")
    plt.ylabel("Número de dominios únicos")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "unique_domains.png"))
    plt.close()

if __name__ == "__main__":
    results = parse_logs()
    analyze_monkey_vs_appium(results)
