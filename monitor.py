import psutil
import argparse
import csv
import time
from datetime import datetime

# Função para obter o nome do processo a partir do PID
def get_process_name(pid):
    try:
        process = psutil.Process(pid)
        return process.name()
    except psutil.NoSuchProcess:
        return None

# Função principal para monitorar o processo
def monitor_process(process_name, pid, interval, output_file):
    try:
        # Se o PID for fornecido, buscar o nome do processo correspondente
        if pid:
            process_name = get_process_name(pid)
            if process_name is None:
                raise ValueError(f"Process with PID {pid} not found.")

        # Abre o arquivo CSV para escrita
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
                for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                    if process_name == process.info['name'] or (pid and pid == process.info['pid']):
                        pid = process.info['pid']
                        cpu_usage = process.info['cpu_percent']
                        memory_usage_percent = process.info['memory_percent']
                        memory_usage_mb = process.info['memory_info'].rss / (1024 * 1024)
                        
                        # Obtendo IO e conexões
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

                        # Escreve os dados no CSV
                        writer.writerow({
                            "timestamp": timestamp,
                            "process_name": process_name,
                            "pid": pid,
                            "cpu_usage_percent": cpu_usage,
                            "memory_usage_percent": memory_usage_percent,
                            "memory_usage_mb": memory_usage_mb,
                            "io_reads": io_reads,
                            "io_writes": io_writes,
                            "network_connections": connections
                        })
                        file.flush()  # Garante que os dados sejam salvos
                        break
                time.sleep(interval)
    except KeyboardInterrupt:
        print("Monitoramento interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro ao monitorar o processo: {e}")


def main():
    parser = argparse.ArgumentParser(description="Monitora o uso de recursos de um processo.")
    parser.add_argument("-n", "--name", type=str, help="Nome do processo para monitorar.")
    parser.add_argument("-p", "--pid", type=int, help="PID do processo para monitorar.")
    parser.add_argument("-i", "--interval", type=float, default=1.0, help="Intervalo entre leituras (em segundos).")
    parser.add_argument("-o", "--output", type=str, required=True, help="Arquivo de saída CSV.")
    args = parser.parse_args()

    if not args.name and not args.pid:
        print("Erro: É necessário fornecer o nome do processo ou o PID.")
        return

    # Monitorar com base no nome ou PID
    monitor_process(args.name, args.pid, args.interval, args.output)


if __name__ == "__main__":
    main()

