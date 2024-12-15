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

def analyze_authentication_pii_types_by_app(results):
    """Analyze PII types grouped by authentication status and application."""
    data = []

    # Filtrar solo los directorios relevantes para el caso 2
    relevant_directories = ["case2_loggingAuthMonkey", "case2_loggingAuthManual"]

    all_apps = set()

    for dir_name in relevant_directories:
        if dir_name in results:
            auth_status = "Autenticado" if "Manual" in dir_name else "No Autenticado"
            for app_name, app_results in results[dir_name].items():
                all_apps.add(app_name)
                for pii_type, count in app_results["dynamic_other_pii_values"].items():
                    data.append({
                        "Estado": auth_status,
                        "Aplicación": app_name,
                        "PII Tipo": pii_type,
                        "Frecuencia": count
                    })

    # Asegurar que todas las aplicaciones estén representadas, incluso con frecuencia 0
    all_pii_types = set(d["PII Tipo"] for d in data)
    for app_name in all_apps:
        for estado in ["Autenticado", "No Autenticado"]:
            for pii_type in all_pii_types:
                if not any(
                    d["Aplicación"] == app_name and d["Estado"] == estado and d["PII Tipo"] == pii_type
                    for d in data
                ):
                    data.append({
                        "Estado": estado,
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
    analysis_dir = create_directories(base_dir, "case2_authentication_pii_types_by_app")

    # Agrupar datos por Estado, Aplicación y Tipo de PII
    grouped_df = df.groupby(["Estado", "Aplicación", "PII Tipo"])["Frecuencia"].sum().reset_index()

    # Truncar los nombres de las aplicaciones a un máximo de 15 caracteres
    grouped_df["Aplicación"] = grouped_df["Aplicación"].apply(lambda x: x[:15] + "..." if len(x) > 15 else x)

    # Obtener el valor máximo de frecuencia para el escalado uniforme
    max_y = grouped_df["Frecuencia"].max() + 5  # Añadir un margen

    # Crear gráficos separados para cada estado
    for estado in grouped_df["Estado"].unique():
        estado_df = grouped_df[grouped_df["Estado"] == estado]

        plt.figure(figsize=(14, 8))
        sns.barplot(
            data=estado_df,
            x="Aplicación",
            y="Frecuencia",
            hue="PII Tipo",
            palette="tab10",
            dodge=True,
            errorbar=None  # Desactivar barras de error
        )

        # Añadir líneas verticales entre aplicaciones
        unique_apps = estado_df["Aplicación"].unique()
        for i in range(1, len(unique_apps)):
            plt.axvline(i - 0.5, color="gray", linestyle="--", linewidth=0.8)  # Línea gris punteada

        plt.title(f"Frecuencia de cada tipo de datos personales en estado {estado}")
        plt.xlabel("Aplicación")
        plt.ylabel("Frecuencia")
        plt.ylim(0, max_y)  # Aplicar el escalado uniforme
        plt.legend(title="Tipo de PII", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.xticks(rotation=45, ha="right")  # Rotar etiquetas de las aplicaciones
        plt.tight_layout()
        plt.savefig(os.path.join(analysis_dir, f"pii_types_by_app_and_authentication_{estado.lower()}.png"))
        plt.close()

if __name__ == "__main__":
    results = parse_logs()
    analyze_authentication_pii_types_by_app(results)
