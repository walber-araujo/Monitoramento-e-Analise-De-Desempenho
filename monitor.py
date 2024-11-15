import time
import csv
import argparse
import psutil
import sys

# Define os argumentos do script
parser = argparse.ArgumentParser(description="Monitoramento de processos no macOS")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-p", "--pid", type=int, help="PID do processo alvo")
group.add_argument("-n", "--name", type=str, help="Nome do processo alvo")
parser.add_argument("-o", "--output", type=str, default="monitor_output.csv", help="Arquivo de saída CSV")
parser.add_argument("-i", "--interval", type=float, default=1.0, help="Intervalo de coleta de métricas em segundos")
args = parser.parse_args()

# Função para obter o PID pelo nome do processo
def get_pid_by_name(name):
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if process.info['name'] == name:
            return process.info['pid']
    return None

# Função para verificar se o PID está ativo e obter o nome do processo
def get_process_name(pid):
    try:
        process = psutil.Process(pid)
        return process.name()
    except psutil.NoSuchProcess:
        return None

# Função para verificar se o PID ainda está ativo
def is_pid_running(pid):
    return psutil.pid_exists(pid)

# Função para coletar o uso de CPU específico do processo
def get_process_cpu_usage(process):
    try:
        return process.cpu_percent(interval=None)  # Usa o intervalo já calculado pelo método
    except psutil.NoSuchProcess:
        return 0

# Função para obter uso de memória do processo em porcentagem e em MB
def get_process_memory_usage(process):
    try:
        memory_percent = process.memory_percent()  # Porcentagem de memória usada pelo processo
        memory_info = process.memory_info().rss / (1024 * 1024)  # Memória usada em MB
        return memory_percent, memory_info
    except psutil.NoSuchProcess:
        return 0, 0

# Função para coletar métricas de I/O do processo
def get_io_metrics(process):
    try:
        if hasattr(process, 'io_counters'):
            io_counters = process.io_counters()
            return io_counters.read_count, io_counters.write_count
        else:
            return 0, 0
    except psutil.NoSuchProcess:
        return 0, 0

# Função para coletar métricas de rede
def get_network_metrics(process):
    try:
        connections = process.connections(kind='inet')
        return len(connections)
    except psutil.NoSuchProcess:
        return 0

# Função para encontrar o processo baseado no nome ou PID
def find_process(name=None, pid=None):
    try:
        if pid:
            process = psutil.Process(pid)
        elif name:
            pid = get_pid_by_name(name)
            if pid:
                process = psutil.Process(pid)
            else:
                return None
        else:
            return None
        return process
    except psutil.NoSuchProcess:
        return None

# Determina o PID do processo
if args.name:
    process = find_process(name=args.name)
    if not process:
        print(f"Erro: O processo com nome '{args.name}' não está ativo.")
        sys.exit(1)
elif args.pid:
    process = find_process(pid=args.pid)
    if not process:
        print(f"Erro: O processo com PID {args.pid} não está ativo.")
        sys.exit(1)

# Verifica se o processo está ativo
pid = process.pid
process_name = get_process_name(pid)
if not process_name:
    print(f"Erro: O processo com PID {pid} não está ativo.")
    sys.exit(1)

# Abre o arquivo CSV para escrita com tratamento de exceção
try:
    with open(args.output, mode="w", newline="") as csvfile:
        fieldnames = [
            "timestamp", "process_name", "pid", "cpu_usage_percent", "memory_usage_percent",
            "memory_usage_mb", "io_reads", "io_writes", "network_connections"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        print(f"Monitorando o processo '{process_name}' com PID {pid}... Pressione Ctrl+C para interromper.")
        print(f"Os dados estão sendo salvos em '{args.output}'.")

        # Inicializa o cálculo de CPU
        process.cpu_percent(interval=None)  # Inicializa o cálculo

        # Verificação do intervalo
        if args.interval < 0.1:
            print("Aviso: Intervalo muito curto pode impactar o desempenho e a precisão.")

        try:
            while is_pid_running(pid):
                # Marca o início do ciclo
                start_time = time.time()
                
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                cpu_usage = get_process_cpu_usage(process)
                memory_usage_percent, memory_usage_mb = get_process_memory_usage(process)
                io_reads, io_writes = get_io_metrics(process)
                network_connections = get_network_metrics(process)

                # Coleta de dados
                row = {
                    "timestamp": timestamp,
                    "process_name": process_name,
                    "pid": pid,  # Adiciona o PID ao registro
                    "cpu_usage_percent": cpu_usage,
                    "memory_usage_percent": memory_usage_percent,
                    "memory_usage_mb": memory_usage_mb,
                    "io_reads": io_reads,
                    "io_writes": io_writes,
                    "network_connections": network_connections
                }

                writer.writerow(row)
                csvfile.flush()

                # Calcula o tempo gasto e ajusta para compensar
                elapsed_time = time.time() - start_time
                if elapsed_time < args.interval:
                    time.sleep(args.interval - elapsed_time)

        except KeyboardInterrupt:
            print("\nMonitoramento finalizado.")
except IOError as e:
    print(f"Erro ao abrir o arquivo CSV: {e}")
    sys.exit(1)

