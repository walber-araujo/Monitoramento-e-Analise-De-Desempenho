import pandas as pd
import argparse
import os
import plotly.express as px
from datetime import timedelta

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
df = pd.read_csv(args.input, delimiter=";")
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')

# Verifica se as colunas necessárias existem
required_columns = ['cpu_usage_percent', 'memory_usage_percent', 'memory_usage_mb', 'io_reads', 'network_connections', 'pid']
for column in required_columns:
    if column not in df.columns:
        print(f"A coluna '{column}' não está presente no arquivo CSV. Ajuste necessário.")
        exit(1)

# Função para gerar e salvar gráficos interativos
def save_interactive_graphs(df):
    # Função auxiliar para configurar e salvar cada gráfico
    def save_plot(column, title, ylabel, color, filename):
        # Criação do gráfico interativo
        fig = px.line(df, x='timestamp', y=column, title=title,
                      labels={'timestamp': 'Horário', column: ylabel},
                      line_shape='linear')
        
        # Adiciona a linha de média
        mean_value = df[column].mean()
        fig.add_hline(y=mean_value, line_dash="dash", line_color='gray', annotation_text=f"Média: {mean_value:.2f}")
        
        # Anomalias (valores acima e abaixo de N desvios padrão)
        std_dev = df[column].std()
        anomaly_threshold_upper = mean_value + args.std_dev * std_dev
        anomaly_threshold_lower = mean_value - args.std_dev * std_dev

        # Se for CPU, não considerar anomalias abaixo do limite de CPU
        if column == 'cpu_usage_percent' and args.cpu_limit > 0:
            anomalies = df[(df[column] > anomaly_threshold_upper) & (df[column] >= args.cpu_limit)]
        else:
            anomalies = df[df[column] > anomaly_threshold_upper]

        # Adiciona as anomalias acima de N desvios
        fig.add_scatter(x=anomalies['timestamp'], y=anomalies[column], mode='markers', 
                        marker=dict(color='red', size=10), name=f"Anomalias (acima {args.std_dev} desvios)")

        # Adiciona as anomalias abaixo de N desvios
        anomalies_lower = df[df[column] < anomaly_threshold_lower]
        fig.add_scatter(x=anomalies_lower['timestamp'], y=anomalies_lower[column], mode='markers', 
                        marker=dict(color='orange', size=10), name=f"Anomalias (abaixo {args.std_dev} desvios)")
        
        # Salvando o gráfico interativo como HTML
        fig.write_html(f"{args.output}/{filename}.html")  # Salva como HTML para interatividade
        fig.show()

    # Gráficos
    save_plot('cpu_usage_percent', "Uso de CPU (%)", "Uso de CPU (%)", 'dodgerblue', 'cpu_usage')
    save_plot('memory_usage_percent', "Uso de Memória (%)", "Uso de Memória (%)", 'forestgreen', 'memory_usage_percent')
    save_plot('memory_usage_mb', "Uso de Memória (MB)", "Memória Usada (MB)", 'goldenrod', 'memory_usage_mb')
    save_plot('io_reads', "Leituras de I/O", "Número de Leituras", 'firebrick', 'io_reads')
    save_plot('network_connections', "Conexões de Rede", "Número de Conexões", 'purple', 'network_connections')

    print("Gráficos interativos salvos no diretório especificado.")

# Função para detectar anomalias e salvar em arquivo CSV
def detect_anomalies_and_save(df, cpu_limit, std_dev_value):
    anomaly_data = []

    # Detecta anomalias nos dados
    for column in ['cpu_usage_percent', 'memory_usage_percent', 'memory_usage_mb']:
        # Caso o limite de CPU seja maior que o valor mínimo e for CPU, aplicar a verificação
        if column == 'cpu_usage_percent' and cpu_limit > 0:
            df = df[df[column] >= cpu_limit]  # Filtra os dados que têm uso de CPU acima do limite mínimo

        std_dev = df[column].std()
        mean_value = df[column].mean()
        anomaly_threshold_upper = mean_value + std_dev_value * std_dev
        anomaly_threshold_lower = mean_value - std_dev_value * std_dev

        # Filtra as anomalias, mas exclui as de CPU abaixo do limite
        anomalies = df[(df[column] > anomaly_threshold_upper) | (df[column] < anomaly_threshold_lower)]
        
        # Exclui as anomalias de CPU que estão abaixo do limite configurado
        if column == 'cpu_usage_percent' and cpu_limit > 0:
            anomalies = anomalies[anomalies[column] >= cpu_limit]

        # Adiciona as anomalias aos dados
        for _, anomaly in anomalies.iterrows():
            anomaly_data.append({
                'timestamp': anomaly['timestamp'],
                'column': column,
                'value': anomaly[column],
                'pid': anomaly['pid'],  # Inclui o pid
                'anomaly_type': 'above' if anomaly[column] > anomaly_threshold_upper else 'below'
            })

    # Salva as anomalias em um arquivo CSV
    anomaly_df = pd.DataFrame(anomaly_data)
    anomaly_df.to_csv('anomalies.csv', index=False)
    print(f"Anomalias detectadas e salvas no arquivo 'anomalies.csv'.")

# Executa a análise e salva os gráficos e anomalias
save_interactive_graphs(df)
detect_anomalies_and_save(df, cpu_limit=args.cpu_limit, std_dev_value=args.std_dev)

