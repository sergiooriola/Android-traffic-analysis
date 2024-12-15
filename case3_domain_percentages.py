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

def analyze_domain_percentages(results):
    """Analyze the average transfers per unique domain for dynamic and idle phases."""
    data = []

    # Filtrar solo el directorio relevante para el caso 3
    relevant_directory = "case3_loggingDynVsIdle"

    if relevant_directory in results:
        for app_name, app_results in results[relevant_directory].items():
            for phase in ["dynamic", "idle"]:
                phase_label = "Dinámica" if phase == "dynamic" else "Estática"
                total_pii = app_results[f"{phase}_other_pii_count"]
                unique_domains = len(app_results[f"{phase}_unique_domains"])

                data.append({
                    "Fase": phase_label,
                    "Total PII": total_pii,
                    "Dominios Únicos": unique_domains
                })

    df = pd.DataFrame(data)

    if df.empty:
        print("No hay datos para analizar. Verifique los directorios de resultados.")
        return

    # Agrupar por fase y calcular el promedio global
    grouped_df = df.groupby("Fase").sum()
    grouped_df["Promedio por Dominio"] = grouped_df["Total PII"] / grouped_df["Dominios Únicos"]
    grouped_df["Porcentaje por Dominio"] = (grouped_df["Promedio por Dominio"] / grouped_df["Total PII"]) * 100
    print(grouped_df)

    # Crear directorios para guardar imágenes
    base_dir = "analysis_images"
    analysis_dir = create_directories(base_dir, "case3_domain_percentages")

    # Gráfico: Promedio por dominio único
    plt.figure(figsize=(10, 6))
    sns.barplot(data=grouped_df.reset_index(), x="Fase", y="Promedio por Dominio", hue="Fase", palette="Purples_d", legend=False)
    plt.title("Promedio de transferencias por dominio único por fase")
    plt.xlabel("Fase")
    plt.ylabel("Transferencias por dominio único")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "pii_per_domain.png"))
    plt.close()

    # Gráfico: Porcentaje de transferencias promedio por dominio respecto al total de PII
    plt.figure(figsize=(10, 6))
    sns.barplot(data=grouped_df.reset_index(), x="Fase", y="Porcentaje por Dominio", hue="Fase", palette="PuRd", legend=False)
    plt.title("Porcentaje de transferencias promedio por dominio respecto al total de PII")
    plt.xlabel("Fase")
    plt.ylabel("Porcentaje por dominio")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "domain_percentage_ratio.png"))
    plt.close()

if __name__ == "__main__":
    results = parse_logs()
    analyze_domain_percentages(results)
