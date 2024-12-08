import psutil
import argparse
import csv
import time
from datetime import datetime

def get_process_name(pid):
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

def monitor_process(process_name, pid, interval, output_file):
    try:
        # Verificar processo inicial
        if pid and not psutil.pid_exists(pid):
            raise ValueError(f"Processo com PID {pid} não encontrado.")
        if not pid and not any(p.info['name'] == process_name for p in psutil.process_iter(['name'])):
            raise ValueError(f"Processo com nome '{process_name}' não encontrado.")

        # Configuração do CSV
        with open(output_file, mode='w', newline='') as file:
            fieldnames = [
                "timestamp", "process_name", "pid",
                "cpu_usage_percent", "memory_usage_percent",
                "memory_usage_mb", "io_reads", "io_writes",
                "network_connections"
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()

            # Loop de monitoramento
            while True:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                try:
                    for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                        if (process_name and process.info['name'] == process_name) or (pid and process.info['pid'] == pid):
                            pid = process.info['pid']
                            cpu_usage = round(process.info['cpu_percent'], 2)  # Duas casas decimais
                            memory_usage_percent = round(process.info['memory_percent'], 2)  # Duas casas decimais
                            memory_usage_mb = round(process.info['memory_info'].rss / (1024 * 1024), 2)  # MB, 2 casas decimais

                            # IO e conexões
                            try:
                                io_counters = process.io_counters()
                                io_reads = io_counters.read_count
                                io_writes = io_counters.write_count
                            except (psutil.AccessDenied, AttributeError):
                                io_reads = io_writes = 0

                            try:
                                connections = len(process.connections(kind='inet'))
                            except (psutil.AccessDenied, psutil.NoSuchProcess):
                                connections = 0

                            # Escreve no CSV
                            writer.writerow({
                                "timestamp": timestamp,
                                "process_name": process.info['name'],
                                "pid": pid,
                                "cpu_usage_percent": cpu_usage,
                                "memory_usage_percent": memory_usage_percent,
                                "memory_usage_mb": memory_usage_mb,
                                "io_reads": io_reads,
                                "io_writes": io_writes,
                                "network_connections": connections
                            })
                            file.flush()
                            break
                except psutil.NoSuchProcess:
                    print(f"O processo {process_name} com PID {pid} terminou.")
                    break
                time.sleep(interval)

    except KeyboardInterrupt:
        print("\nMonitoramento interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro: {e}")

def main():
    parser = argparse.ArgumentParser(description="Monitora o uso de recursos de um processo.")
    parser.add_argument("-n", "--name", type=str, help="Nome do processo para monitorar.")
    parser.add_argument("-p", "--pid", type=int, help="PID do processo para monitorar.")
    parser.add_argument("-i", "--interval", type=float, default=1.0, help="Intervalo entre leituras (em segundos).")
    parser.add_argument("-o", "--output", type=str, required=True, help="Arquivo de saída CSV.")
    args = parser.parse_args()

    if not args.name and not args.pid:
        print("Erro: É necessário fornecer o nome ou PID do processo.")
        return

    monitor_process(args.name, args.pid, args.interval, args.output)

if __name__ == "__main__":
    main()

