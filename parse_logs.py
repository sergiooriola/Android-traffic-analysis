import json
import os
import re
from collections import defaultdict

def process_log_file(file_path, results, phase, dir_name, app_name):
    """Procesa un archivo de log y actualiza los resultados."""
    host_pattern = re.compile(r'"host": "([^"]+)"')

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

                        # Extraer dominios y añadirlos al conjunto de dominios únicos solo si hay PII
                        hosts = host_pattern.findall(line)
                        results[dir_name][app_name][f'{phase}_unique_domains'].update(hosts)

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in file {file_path}, line: {line.strip()}. Error: {e}")

def parse_logs():
    """Parses log files in specified directories."""
    results = defaultdict(lambda: defaultdict(lambda: {
        'dynamic_no_pii_count': 0,
        'dynamic_other_pii_count': 0,
        'dynamic_other_pii_values': defaultdict(int),
        'dynamic_unique_domains': set(),
        'idle_no_pii_count': 0,
        'idle_other_pii_count': 0,
        'idle_other_pii_values': defaultdict(int),
        'idle_unique_domains': set()
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
    for dir_name, dir_results in results.items():
        print(f'Resultados para la carpeta: {dir_name}')
        for app_name, app_results in dir_results.items():
            print(f'  Resultados para la aplicación: {app_name}')
            print('  Resultados de la fase dinámica:')
            print(f'    No-PII: {app_results["dynamic_no_pii_count"]}')
            print(f'    Otro PII: {app_results["dynamic_other_pii_count"]}')
            for value, count in app_results['dynamic_other_pii_values'].items():
                print(f'      {value}: {count}')
            print(f'    Dominios únicos: {len(app_results["dynamic_unique_domains"])}')
            print('  Resultados de la fase idle:')
            print(f'    No-PII: {app_results["idle_no_pii_count"]}')
            print(f'    Otro PII: {app_results["idle_other_pii_count"]}')
            for value, count in app_results['idle_other_pii_values'].items():
                print(f'      {value}: {count}')
            print(f'    Dominios únicos: {len(app_results["idle_unique_domains"])}')
            print('  -----------------------------------')