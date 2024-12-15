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

def analyze_dynamic_vs_idle(results):
    """Analyze differences between dynamic and idle phases."""
    data = []

    # Filtrar solo el directorio relevante para el caso 3
    relevant_directory = "case3_loggingDynVsIdle"

    if relevant_directory in results:
        for app_name, app_results in results[relevant_directory].items():
            data.append({
                "Fase": "Dinámica",
                "Aplicación": app_name,
                "Total PII": app_results["dynamic_other_pii_count"],
                "Tipos PII": set(app_results["dynamic_other_pii_values"].keys()),
                "Dominios únicos": len(app_results["dynamic_unique_domains"])
            })
            data.append({
                "Fase": "Estática",
                "Aplicación": app_name,
                "Total PII": app_results["idle_other_pii_count"],
                "Tipos PII": set(app_results["idle_other_pii_values"].keys()),
                "Dominios únicos": len(app_results["idle_unique_domains"])
            })

    df = pd.DataFrame(data)

    if df.empty:
        print("No hay datos para analizar. Verifique los directorios de resultados.")
        return

    # Crear directorios para guardar imágenes
    base_dir = "analysis_images"
    analysis_dir = create_directories(base_dir, "case3_dynamic_vs_idle")

    # Calcular métricas de resumen
    summary = (
        df.groupby("Fase").agg({
            "Total PII": "sum",
            "Tipos PII": lambda x: len(set.union(*x)),  # Unir todos los conjuntos y contar los únicos
            "Dominios únicos": "sum"
        }).reset_index()
    )

    # Gráfico 1: Número total de transferencias de datos personales
    plt.figure(figsize=(10, 6))
    sns.barplot(data=summary, x="Fase", y="Total PII", hue="Fase", palette="Blues_d", dodge=False, legend=False)
    plt.title("Número total de transferencias de datos personales por fase")
    plt.xlabel("Fase")
    plt.ylabel("Total de datos personales")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "total_pii_by_phase.png"))
    plt.close()

    # Gráfico 2: Número de tipos de datos personales transferidos
    plt.figure(figsize=(10, 6))
    sns.barplot(data=summary, x="Fase", y="Tipos PII", hue="Fase", palette="Greens_d", dodge=False, legend=False)
    plt.title("Tipos de datos personales transferidos por fase")
    plt.xlabel("Fase")
    plt.ylabel("Número de tipos de PII")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "types_of_pii_by_phase.png"))
    plt.close()

    # Gráfico 3: Número de dominios únicos
    plt.figure(figsize=(10, 6))
    sns.barplot(data=summary, x="Fase", y="Dominios únicos", hue="Fase", palette="Reds_d", dodge=False, legend=False)
    plt.title("Número de dominios únicos por fase")
    plt.xlabel("Fase")
    plt.ylabel("Número de dominios únicos")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "unique_domains_by_phase.png"))
    plt.close()

if __name__ == "__main__":
    results = parse_logs()
    analyze_dynamic_vs_idle(results)
