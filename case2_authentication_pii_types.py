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

def analyze_authentication_pii_types(results):
    """Analyze PII types grouped by authentication status."""
    data = []

    # Filtrar solo los directorios relevantes para el caso 2
    relevant_directories = ["case2_loggingAuthMonkey", "case2_loggingAuthManual"]

    for dir_name in relevant_directories:
        if dir_name in results:
            auth_status = "Autenticado" if "Manual" in dir_name else "No Autenticado"
            for app_name, app_results in results[dir_name].items():
                for pii_type, count in app_results["dynamic_other_pii_values"].items():
                    data.append({
                        "Estado": auth_status,
                        "PII Tipo": pii_type,
                        "Frecuencia": count
                    })

    df = pd.DataFrame(data)

    if df.empty:
        print("No hay datos para analizar. Verifique los directorios de resultados.")
        return

    # Crear directorios para guardar imágenes
    base_dir = "analysis_images"
    analysis_dir = create_directories(base_dir, "case2_authentication_pii_types")

    # Agrupar datos por Estado y Tipo de PII
    grouped_df = df.groupby(["Estado", "PII Tipo"])["Frecuencia"].sum().reset_index()

    # Crear el gráfico con líneas verticales de separación
    plt.figure(figsize=(14, 8))
    sns.barplot(
        data=grouped_df,
        x="Estado",
        y="Frecuencia",
        hue="PII Tipo",
        dodge=True,
        palette="tab10",
        errorbar=None  # Desactivar barras de error
    )

    # Añadir líneas verticales entre los estados
    unique_states = grouped_df["Estado"].unique()
    for i in range(1, len(unique_states)):
        plt.axvline(i - 0.5, color="gray", linestyle="--", linewidth=0.8)  # Línea gris punteada

    plt.title("Frecuencia de cada tipo de datos personales por estado de autenticación")
    plt.xlabel("Estado de autenticación")
    plt.ylabel("Frecuencia")
    plt.legend(title="Tipo de PII", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "pii_types_by_authentication.png"))
    plt.close()

if __name__ == "__main__":
    results = parse_logs()
    analyze_authentication_pii_types(results)
