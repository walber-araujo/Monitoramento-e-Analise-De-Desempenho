import pandas as pd
import argparse
import os
import plotly.express as px

# Argumentos para o arquivo CSV de entrada, o diretório de saída para gráficos, o limite de CPU e o número de desvios padrão
parser = argparse.ArgumentParser(description="Análise de desempenho da aplicação")
parser.add_argument("-i", "--input", type=str, required=True, help="Arquivo CSV de entrada")
parser.add_argument("-o", "--output", type=str, default="output_graphs", help="Diretório de saída para gráficos")
parser.add_argument("-cpu", "--cpu_limit", type=float, default=1.0, help="Limite mínimo de uso de CPU para considerar anomalias")
parser.add_argument("-std", "--std_dev", type=int, default=3, help="Número de desvios padrão para detectar anomalias")
args = parser.parse_args()

# Cria o diretório de saída se não existir
os.makedirs(args.output, exist_ok=True)

# Carrega os dados do CSV
try:
    df = pd.read_csv(args.input, delimiter=";")
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')
except FileNotFoundError:
    print(f"Erro: O arquivo {args.input} não foi encontrado.")
    exit(1)
except pd.errors.ParserError:
    print(f"Erro: Não foi possível analisar o arquivo {args.input}. Verifique o formato CSV.")
    exit(1)

# Verifica se as colunas necessárias existem
required_columns = ['cpu_usage_percent', 'memory_usage_percent', 'memory_usage_mb', 'io_reads', 'network_connections', 'pid']
for column in required_columns:
    if column not in df.columns:
        print(f"A coluna '{column}' não está presente no arquivo CSV. Ajuste necessário.")
        exit(1)

# Adiciona uma coluna para a hora
df['hour'] = df['timestamp'].dt.hour

# Filtra horários fora do intervalo 00:00-08:00
df_filtered = df[df['hour'] >= 8]

# Função para calcular métricas e imprimir relatório
def print_detailed_report(df, filtered=False):
    report_title = "Relatório Detalhado (08:00-23:59)" if filtered else "Relatório Detalhado (Completo)"
    print("\n" + "=" * len(report_title))
    print(report_title)
    print("=" * len(report_title))

    current_df = df_filtered if filtered else df

    for column in ['cpu_usage_percent', 'memory_usage_percent', 'memory_usage_mb', 'io_reads', 'network_connections']:
        mean_value = current_df[column].mean()
        std_dev = current_df[column].std()
        data_count = len(current_df[column])
        anomaly_threshold_upper = mean_value + args.std_dev * std_dev
        anomaly_threshold_lower = mean_value - args.std_dev * std_dev

        # Conta anomalias acima e abaixo do limite
        anomalies_upper = current_df[current_df[column] > anomaly_threshold_upper]
        anomalies_lower = current_df[current_df[column] < anomaly_threshold_lower]
        total_anomalies = len(anomalies_upper) + len(anomalies_lower)

        print(f"\nMétrica: {column}")
        print(f"- Número de dados: {data_count}")
        print(f"- Média: {mean_value:.2f}")
        print(f"- Desvio padrão: {std_dev:.2f}")
        print(f"- Limite superior (anomalias): {anomaly_threshold_upper:.2f}")
        print(f"- Limite inferior (anomalias): {anomaly_threshold_lower:.2f}")
        print(f"- Total de anomalias: {total_anomalies}")
        print(f"  -> Acima do limite: {len(anomalies_upper)}")
        print(f"  -> Abaixo do limite: {len(anomalies_lower)}")

# Função para salvar gráficos com médias corretas
def save_graphs(df, filtered=False):
    # Define o prefixo para distinguir os gráficos filtrados
    prefix = "filtered_" if filtered else ""

    # Escolhe o DataFrame apropriado
    current_df = df_filtered if filtered else df

    def save_plot(column, title, ylabel, filename):
        fig = px.line(current_df, x='timestamp', y=column, title=title,
                      labels={'timestamp': 'Horário', column: ylabel},
                      line_shape='linear')

        # Média correta para o DataFrame atual
        mean_value = current_df[column].mean()
        fig.add_hline(y=mean_value, line_dash="dash", line_color='gray',
                      annotation_text=f"Média: {mean_value:.2f}")

        # Salvando o gráfico
        fig.write_html(f"{args.output}/{prefix}{filename}.html")
        fig.show()

    # Gráficos
    save_plot('cpu_usage_percent', f"Uso de CPU (%) {'(08:00-23:59)' if filtered else ''}", "Uso de CPU (%)", f"{prefix}cpu_usage")
    save_plot('memory_usage_percent', f"Uso de Memória (%) {'(08:00-23:59)' if filtered else ''}", "Uso de Memória (%)", f"{prefix}memory_usage_percent")
    save_plot('memory_usage_mb', f"Uso de Memória (MB) {'(08:00-23:59)' if filtered else ''}", "Memória Usada (MB)", f"{prefix}memory_usage_mb")
   # save_plot('io_reads', "Leituras de I/O", "Número de Leituras", f"{prefix}io_reads")
    #save_plot('network_connections', "Conexões de Rede", "Número de Conexões", f"{prefix}network_connections")

    print(f"Gráficos {'filtrados ' if filtered else ''}salvos no diretório especificado.")

# Executa as funções de relatório e gráficos
print_detailed_report(df, filtered=False)  # Relatório completo
print_detailed_report(df, filtered=True)   # Relatório filtrado
save_graphs(df, filtered=False)            # Gráficos gerais
save_graphs(df, filtered=True)             # Gráficos filtrados

