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
    """Analyze unique personal data transfers by domain and port for Case 3."""
    data = []

    # Directorio relevante para el Caso 3
    relevant_directory = "case3_loggingDynVsIdle"

    # Mapeo de nombres amigables para las fases
    phase_mapping = {
        "dynamic": "Dinámica",
        "idle": "Estática"
    }

    if relevant_directory in results:
        for app_name, app_results in results[relevant_directory].items():
            for phase in ["dynamic", "idle"]:
                detailed_transfers = app_results.get(f"{phase}_detailed_transfers", [])
                for transfer in detailed_transfers:
                    data.append({
                        "Fase": phase_mapping[phase],  # Usar nombres amigables
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
    analysis_dir = create_directories(base_dir, "case3_unique_transfers")

    # Resumen tabular: Conteo de transferencias únicas por fase
    summary = unique_transfers_df.groupby("Fase").size().reset_index(name="Transferencias Únicas")

    print("Resumen de transferencias únicas:")
    print(summary)

    # Gráfico: Número de transferencias únicas
    plt.figure(figsize=(10, 6))
    sns.barplot(data=summary, x="Fase", y="Transferencias Únicas", hue="Fase", palette="Oranges", dodge=False, legend=False)
    plt.title("Número de transferencias únicas de datos personales por fase")
    plt.xlabel("Fase")
    plt.ylabel("Transferencias únicas")
    plt.tight_layout()
    plt.savefig(os.path.join(analysis_dir, "unique_pii_transfers.png"))
    plt.close()

if __name__ == "__main__":
    results = parse_logs()
    analyze_unique_pii_transfers(results)
