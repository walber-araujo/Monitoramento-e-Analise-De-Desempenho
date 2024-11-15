import argparse
import csv
import subprocess
import json
import os
from datetime import datetime, timedelta

# Função para coletar logs do sistema relacionados ao PID
def get_logs_for_pid(pid, start_time, end_time):
    try:
        # Converte os tempos de início e fim para o formato necessário
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

        # Comando para buscar logs no macOS
        log_command = [
            "log", "show", 
            "--predicate", f"processID == {pid}",
            "--info",
            "--start", start_time_str,
            "--end", end_time_str,
            "--style", "syslog"
        ]
        
        # Executa o comando e captura a saída
        result = subprocess.run(log_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            print(f"Erro ao coletar logs para o PID {pid}: {result.stderr.decode('utf-8')}")
            return None
        
        # Retorna os logs como string
        return result.stdout.decode('utf-8').strip()

    except Exception as e:
        print(f"Erro ao obter logs para o PID {pid}: {e}")
        return None

# Função para analisar o relatório de anomalias e gerar auditoria
def analyze_anomalies_report(report_file, output_dir):
    try:
        # Cria o diretório de saída, se não existir
        os.makedirs(output_dir, exist_ok=True)

        audit_data = {"anomalies": []}

        with open(report_file, mode='r') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                timestamp_str = row['timestamp']
                pid = int(row['pid'])
                anomaly_type = row['anomaly_type']
                
                # Converte o timestamp para datetime
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                end_time = timestamp + timedelta(seconds=10)

                # Obtém os logs para o PID
                logs = get_logs_for_pid(pid, timestamp, end_time)
                
                anomaly_entry = {
                    "timestamp": timestamp_str,
                    "pid": pid,
                    "anomaly_type": anomaly_type,
                    "log_interval": {
                        "start": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        "end": end_time.strftime('%Y-%m-%d %H:%M:%S')
                    },
                    "logs": logs if logs else "Nenhum log encontrado no intervalo"
                }
                audit_data["anomalies"].append(anomaly_entry)
        
        # Salva o JSON no arquivo
        audit_filename = os.path.join(output_dir, "audit_logs.json")
        with open(audit_filename, 'w') as json_file:
            json.dump(audit_data, json_file, indent=4, ensure_ascii=False)
        
        print(f"Relatório de auditoria salvo em: {audit_filename}")
    
    except Exception as e:
        print(f"Erro ao processar o relatório de anomalias: {e}")

# Função principal para os argumentos
def main():
    parser = argparse.ArgumentParser(description="Análise de desempenho da aplicação")
    parser.add_argument("-i", "--input", type=str, required=True, help="Arquivo CSV de entrada")
    parser.add_argument("-o", "--output", type=str, default="auditoria", help="Diretório de saída para a auditoria")
    args = parser.parse_args()

    # Executa a análise
    analyze_anomalies_report(args.input, args.output)

# Executa o script
if __name__ == "__main__":
    main()

