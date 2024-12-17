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

def analyze_unique_pii_transfers(results):
    """Analyze unique personal data transfers by domain and port for Case 2."""
    data = []

    # Directorios relevantes para el Caso 2
    relevant_directories = ["case2_loggingAuthMonkey", "case2_loggingAuthManual"]

    # Mapeo de nombres amigables para los estados de autenticación
    auth_mapping = {
        "case2_loggingAuthMonkey": "No Autenticado",
        "case2_loggingAuthManual": "Autenticado"
    }

    for dir_name in relevant_directories:
        if dir_name in results:
            for app_name, app_results in results[dir_name].items():
                detailed_transfers = app_results.get("dynamic_detailed_transfers", [])
                for transfer in detailed_transfers:
                    data.append({
                        "Estado": auth_mapping.get(dir_name, dir_name),  # Usar nombres amigables
                        "Aplicación": app_name,
                        "PII Tipo": transfer["PII Tipo"],
                        "Dominio": transfer["Dominio"],
                        "Puerto": str(transfer["Puerto"])  # Convertir a string por consistencia
                    })

    df = pd.DataFrame(data)

    if df.empty:
        print("No hay datos para analizar. Verifique los directorios de resultados.")
        return

    # Mostrar todas las filas del DataFrame
    pd.set_option("display.max_rows", None)  # Ajuste para mostrar todas las filas
    print("Datos antes de aplicar `drop_duplicates`:")
    print(df)

    # Filtrar datos únicos basados en `PII Tipo`, `Dominio` y `Puerto`
    unique_transfers_df = df.drop_duplicates(subset=["PII Tipo", "Dominio", "Puerto"])

    print("Datos después de aplicar `drop_duplicates`:")
    print(unique_transfers_df)

    # Crear directorios para guardar imágenes
    base_dir = "analysis_images"
    analysis_dir = create_directories(base_dir, "case2_unique_transfers")

    # Resumen tabular: Conteo de transferencias únicas por estado de autenticación
    summary = unique_transfers_df.groupby("Estado").size().reset_index(name="Transferencias Únicas")

    print("Resumen de transferencias únicas:")
    print(summary)

    # Gráfico: Número de transferencias únicas
    plt.figure(figsize=(10, 6))
    sns.barplot(data=summary, x="Estado", y="Transferencias Únicas", hue="Estado", palette="Oranges", dodge=False, legend=False)
    plt.title("Número de transferencias únicas de datos personales por estado de autenticación")
    plt.xlabel("Estado de autenticación")
    plt.ylabel("Transferencias únicas")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "unique_pii_transfers.png"))
    plt.close()

if __name__ == "__main__":
    results = parse_logs()
    analyze_unique_pii_transfers(results)
