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
    """Analyze the average transfers per unique domain for authentication states."""
    data = []

    # Filtrar solo los directorios relevantes para el caso 2
    relevant_directories = ["case2_loggingAuthMonkey", "case2_loggingAuthManual"]

    for dir_name in relevant_directories:
        if dir_name in results:
            estado = "Autenticado" if "Manual" in dir_name else "No Autenticado"
            for app_name, app_results in results[dir_name].items():
                total_pii = app_results["dynamic_other_pii_count"]
                unique_domains = len(app_results["dynamic_unique_domains"])

                data.append({
                    "Estado": estado,
                    "Total PII": total_pii,
                    "Dominios Únicos": unique_domains
                })

    df = pd.DataFrame(data)

    if df.empty:
        print("No hay datos para analizar. Verifique los directorios de resultados.")
        return

    # Agrupar por estado y calcular el promedio global
    grouped_df = df.groupby("Estado").sum()
    grouped_df["Promedio por Dominio"] = grouped_df["Total PII"] / grouped_df["Dominios Únicos"]
    grouped_df["Porcentaje por Dominio"] = (grouped_df["Promedio por Dominio"] / grouped_df["Total PII"]) * 100
    print(grouped_df)

    # Crear directorios para guardar imágenes
    base_dir = "analysis_images"
    analysis_dir = create_directories(base_dir, "case2_domain_percentages")

    # Gráfico: Promedio por dominio único
    plt.figure(figsize=(10, 6))
    sns.barplot(data=grouped_df.reset_index(), x="Estado", y="Promedio por Dominio", hue="Estado", palette="Purples_d", legend=False)
    plt.title("Promedio de transferencias por dominio único por estado de autenticación")
    plt.xlabel("Estado de autenticación")
    plt.ylabel("Transferencias por dominio único")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "pii_per_domain.png"))
    plt.close()

    # Gráfico: Porcentaje de transferencias promedio por dominio respecto al total de PII
    plt.figure(figsize=(10, 6))
    sns.barplot(data=grouped_df.reset_index(), x="Estado", y="Porcentaje por Dominio", hue="Estado", palette="PuRd", legend=False)
    plt.title("Porcentaje de transferencias promedio por dominio respecto al total de PII")
    plt.xlabel("Estado de autenticación")
    plt.ylabel("Porcentaje por dominio")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "domain_percentage_ratio.png"))
    plt.close()

if __name__ == "__main__":
    results = parse_logs()
    analyze_domain_percentages(results)