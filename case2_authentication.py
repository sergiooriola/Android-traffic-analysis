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

def analyze_authentication_impact(results):
    """Analyze the impact of authentication on data transfers."""
    data = []

    # Filtrar solo los directorios relevantes para el caso 2
    relevant_directories = ["case2_loggingAuthMonkey", "case2_loggingAuthManual"]

    for dir_name in relevant_directories:
        if dir_name in results:
            auth_status = "Autenticado" if "Manual" in dir_name else "No Autenticado"
            for app_name, app_results in results[dir_name].items():
                data.append({
                    "Estado": auth_status,
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
    analysis_dir = create_directories(base_dir, "case2_authentication")

    # Resumen tabular
    summary = (
        df.groupby("Estado").agg({
            "Total PII": "sum",
            "Tipos PII": lambda x: len(set.union(*x)),  # Unir todos los conjuntos y contar los únicos
            "Dominios únicos": "sum"
        }).reset_index()
    )

    # Gráfico 1: Número total de datos personales transferidos
    plt.figure(figsize=(10, 6))
    sns.barplot(data=summary, x="Estado", y="Total PII", hue="Estado", palette="Blues_d", dodge=False, legend=False)
    plt.title("Número total de datos personales transferidos por estado de autenticación")
    plt.xlabel("Estado de autenticación")
    plt.ylabel("Total de datos personales")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "total_pii_by_authentication.png"))
    plt.close()

    # Gráfico 2: Número de tipos de datos personales transferidos
    plt.figure(figsize=(10, 6))
    sns.barplot(data=summary, x="Estado", y="Tipos PII", hue="Estado", palette="Greens_d", dodge=False, legend=False)
    plt.title("Tipos de datos personales transferidos por estado de autenticación")
    plt.xlabel("Estado de autenticación")
    plt.ylabel("Número de tipos de PII")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "types_of_pii_by_authentication.png"))
    plt.close()

    # Gráfico 3: Número de dominios únicos
    plt.figure(figsize=(10, 6))
    sns.barplot(data=summary, x="Estado", y="Dominios únicos", hue="Estado", palette="Reds_d", dodge=False, legend=False)
    plt.title("Número de dominios únicos por estado de autenticación")
    plt.xlabel("Estado de autenticación")
    plt.ylabel("Número de dominios únicos")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "unique_domains_by_authentication.png"))
    plt.close()

if __name__ == "__main__":
    results = parse_logs()
    analyze_authentication_impact(results)