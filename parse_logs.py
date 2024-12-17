import json
import os
import re
from collections import defaultdict

def process_log_file(file_path, results, phase, dir_name, app_name):
    """Procesa un archivo de log y actualiza los resultados."""
    host_pattern = re.compile(r'"host": "([^"]+)"')
    port_pattern = re.compile(r'"port_source": (\d+)')

    with open(file_path, 'r') as file:
        for line in file:
            try:
                data = json.loads(line)
                if 'PII' in data:
                    if data['PII'] == 'No-PII':
                        results[dir_name][app_name][f'{phase}_no_pii_count'] += 1
                    else:
                        results[dir_name][app_name][f'{phase}_other_pii_count'] += 1
                        results[dir_name][app_name][f'{phase}_other_pii_values'][data['PII']] += 1

                        # Extraer dominios y puertos asociados
                        hosts = host_pattern.findall(line)
                        ports = port_pattern.findall(line)

                        for host in hosts:
                            for port in ports:
                                results[dir_name][app_name][f'{phase}_unique_domains'].add((host, port))
                                # Añadir entradas detalladas para cada PII tipo, dominio y puerto
                                results[dir_name][app_name][f'{phase}_detailed_transfers'].append({
                                    "PII Tipo": data['PII'],
                                    "Dominio": host,
                                    "Puerto": port
                                })

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in file {file_path}, line: {line.strip()}. Error: {e}")

def parse_logs():
    """Parses log files in specified directories."""
    results = defaultdict(lambda: defaultdict(lambda: {
        'dynamic_no_pii_count': 0,
        'dynamic_other_pii_count': 0,
        'dynamic_other_pii_values': defaultdict(int),
        'dynamic_unique_domains': set(),
        'dynamic_detailed_transfers': [],
        'idle_no_pii_count': 0,
        'idle_other_pii_count': 0,
        'idle_other_pii_values': defaultdict(int),
        'idle_unique_domains': set(),
        'idle_detailed_transfers': []
    }))

    # Nuevas carpetas organizadas por caso de uso
    directories = {
        'case1_logging': '/home/privapp/new_traffic/logging/',
        'case1_loggingAppium': '/home/privapp/new_traffic/loggingAppium/',
        'case1_loggingManual': '/home/privapp/new_traffic/loggingManual/',
        'case2_loggingAuthMonkey': '/home/privapp/new_traffic/loggingAuthMonkey/',
        'case2_loggingAuthManual': '/home/privapp/new_traffic/loggingAuthManual/',
        'case3_loggingDynVsIdle': '/home/privapp/new_traffic/loggingDynVsIdle/'
    }

    for dir_name, base_directory_path in directories.items():
        for root, _, files in os.walk(base_directory_path):
            app_name = os.path.basename(os.path.dirname(root))
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name.endswith('-Results-dynamic-mitm.log'):
                    process_log_file(file_path, results, 'dynamic', dir_name, app_name)
                elif file_name.endswith('-Results-idle-mitm.log'):
                    process_log_file(file_path, results, 'idle', dir_name, app_name)

    return results

if __name__ == "__main__":
    results = parse_logs()
    with open('results.json', 'w') as f:
        json.dump(results, f, default=lambda o: list(o) if isinstance(o, set) else o, indent=4)