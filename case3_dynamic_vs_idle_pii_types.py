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

def analyze_pii_types_by_phase(results):
    """Analyze PII types grouped by phase (dynamic vs idle)."""
    data = []

    # Filtrar solo el directorio relevante para el caso 3
    relevant_directory = "case3_loggingDynVsIdle"

    if relevant_directory in results:
        for app_name, app_results in results[relevant_directory].items():
            for pii_type, count in app_results["dynamic_other_pii_values"].items():
                data.append({
                    "Fase": "Dinámica",
                    "PII Tipo": pii_type,
                    "Frecuencia": count
                })
            for pii_type, count in app_results["idle_other_pii_values"].items():
                data.append({
                    "Fase": "Estática",
                    "PII Tipo": pii_type,
                    "Frecuencia": count
                })

    df = pd.DataFrame(data)

    if df.empty:
        print("No hay datos para analizar. Verifique los directorios de resultados.")
        return

    # Crear directorios para guardar imágenes
    base_dir = "analysis_images"
    analysis_dir = create_directories(base_dir, "case3_pii_types_by_phase")

    # Agrupar datos por Fase y Tipo de PII
    grouped_df = df.groupby(["Fase", "PII Tipo"])["Frecuencia"].sum().reset_index()

    # Crear el gráfico con barras ordenadas por fase
    plt.figure(figsize=(14, 8))
    sns.barplot(
        data=grouped_df,
        x="Fase",
        y="Frecuencia",
        hue="PII Tipo",
        dodge=True,
        palette="tab10",
        errorbar=None  # Eliminar barras de error
    )

    # Añadir líneas verticales entre las fases
    unique_phases = grouped_df["Fase"].unique()
    for i in range(1, len(unique_phases)):
        plt.axvline(i - 0.5, color="gray", linestyle="--", linewidth=0.8)  # Línea gris punteada

    plt.title("Frecuencia de cada tipo de datos personales por fase")
    plt.xlabel("Fase")
    plt.ylabel("Frecuencia")
    plt.legend(title="Tipo de PII", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "pii_types_by_phase.png"))
    plt.close()

if __name__ == "__main__":
    results = parse_logs()
    analyze_pii_types_by_phase(results)
