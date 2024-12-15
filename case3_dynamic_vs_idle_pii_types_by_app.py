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

def analyze_pii_types_by_phase_and_app(results):
    """Analyze PII types grouped by phase, application, and type of PII."""
    data = []

    # Filtrar solo el directorio relevante para el caso 3
    relevant_directory = "case3_loggingDynVsIdle"

    if relevant_directory in results:
        all_apps = set()
        for app_name, app_results in results[relevant_directory].items():
            all_apps.add(app_name)
            for pii_type, count in app_results["dynamic_other_pii_values"].items():
                data.append({
                    "Fase": "Dinámica",
                    "Aplicación": app_name,
                    "PII Tipo": pii_type,
                    "Frecuencia": count
                })
            for pii_type, count in app_results["idle_other_pii_values"].items():
                data.append({
                    "Fase": "Estática",
                    "Aplicación": app_name,
                    "PII Tipo": pii_type,
                    "Frecuencia": count
                })
        
        # Asegurar que todas las aplicaciones estén representadas, incluso con frecuencia 0
        all_pii_types = {row["PII Tipo"] for row in data}
        for app_name in all_apps:
            for phase in ["Dinámica", "Estática"]:
                for pii_type in all_pii_types:
                    if not any(
                        d["Aplicación"] == app_name and d["Fase"] == phase and d["PII Tipo"] == pii_type
                        for d in data
                    ):
                        data.append({
                            "Fase": phase,
                            "Aplicación": app_name,
                            "PII Tipo": pii_type,
                            "Frecuencia": 0
                        })

    df = pd.DataFrame(data)

    if df.empty:
        print("No hay datos para analizar. Verifique los directorios de resultados.")
        return

    # Crear directorios para guardar imágenes
    base_dir = "analysis_images"
    analysis_dir = create_directories(base_dir, "case3_pii_types_by_phase_and_app")

    # Agrupar datos por Fase, Aplicación y Tipo de PII
    grouped_df = df.groupby(["Fase", "Aplicación", "PII Tipo"])["Frecuencia"].sum().reset_index()

    # Truncar los nombres de las aplicaciones a un máximo de 10 caracteres
    grouped_df["Aplicación"] = grouped_df["Aplicación"].apply(lambda x: x[:15] + "..." if len(x) > 10 else x)

    # Obtener el valor máximo de frecuencia para el escalado uniforme
    max_y = 20

    # Crear gráficos separados para cada fase
    for phase in grouped_df["Fase"].unique():
        phase_df = grouped_df[grouped_df["Fase"] == phase]

        plt.figure(figsize=(14, 8))
        sns.barplot(
            data=phase_df,
            x="Aplicación",
            y="Frecuencia",
            hue="PII Tipo",
            palette="tab10",
            dodge=True,
            errorbar=None,  # Desactivar barras de error
            width=1.0
        )

        # Añadir líneas verticales entre aplicaciones
        unique_apps = phase_df["Aplicación"].unique()
        for i in range(1, len(unique_apps)):
            plt.axvline(i - 0.5, color="gray", linestyle="--", linewidth=0.8)  # Línea gris punteada

        plt.title(f"Frecuencia de cada tipo de datos personales en fase {phase}")
        plt.xlabel("Aplicación")
        plt.ylabel("Frecuencia")
        plt.ylim(0, max_y)  # Aplicar el escalado uniforme
        plt.legend(title="Tipo de PII", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.xticks(rotation=45, ha="right")  # Rotar etiquetas de las aplicaciones
        plt.tight_layout()
        plt.savefig(os.path.join(analysis_dir, f"pii_types_{phase.lower()}_by_app.png"))
        plt.close()

if __name__ == "__main__":
    results = parse_logs()
    analyze_pii_types_by_phase_and_app(results)
