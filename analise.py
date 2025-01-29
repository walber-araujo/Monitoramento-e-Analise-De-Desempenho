import pandas as pd
import argparse
import os
import plotly.express as px

# Argumentos para o arquivo CSV de entrada e o diretório de saída para gráficos
parser = argparse.ArgumentParser(description="Análise de desempenho da aplicação")
parser.add_argument("-i", "--input", type=str, required=True, help="Arquivo CSV de entrada")
parser.add_argument("-o", "--output", type=str, default="output_graphs", help="Diretório de saída para gráficos")
parser.add_argument("--std_dev", type=float, default=2.0, help="Multiplicador para desvio padrão nas análises de anomalia")
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
except Exception as e:
    print(f"Erro inesperado ao carregar o arquivo CSV: {e}")
    exit(1)

# Verifica se as colunas necessárias existem
required_columns = ['cpu_usage_percent', 'memory_usage_percent', 'memory_usage_mb']
for column in required_columns:
    if column not in df.columns:
        print(f"A coluna '{column}' não está presente no arquivo CSV. Ajuste necessário.")
        exit(1)

# Adiciona uma coluna para detectar anomalias de CPU
df['cpu_anomaly'] = df['cpu_usage_percent'] > 50

# Salva apenas as anomalias de CPU em um arquivo CSV
cpu_anomalies = df[df['cpu_anomaly']]
anomaly_file = os.path.join(args.output, "cpu_anomalies.csv")
cpu_anomalies.to_csv(anomaly_file, index=False, sep=';')
print(f"Arquivo de anomalias de CPU salvo em: {anomaly_file}")

# Função para gerar relatório detalhado
def print_detailed_report(df, std_dev_multiplier):
    print("\n===========================")
    print("      Relatório Detalhado")
    print("===========================")

    for column in ['cpu_usage_percent', 'memory_usage_percent', 'memory_usage_mb']:
        total_samples = len(df)
        mean_value = df[column].mean()
        std_dev = df[column].std()
        anomaly_threshold_upper = mean_value + std_dev_multiplier * std_dev
        anomaly_threshold_lower = mean_value - std_dev_multiplier * std_dev

        anomalies_upper = df[df[column] > anomaly_threshold_upper]
        anomalies_lower = df[df[column] < anomaly_threshold_lower]
        total_anomalies = len(anomalies_upper) + len(anomalies_lower)

        print(f"\nMétrica: {column}")
        print(f"- Total de amostras capturadas: {total_samples}")
        print(f"- Média: {mean_value:.2f}")
        print(f"- Desvio padrão: {std_dev:.2f}")
        print(f"- Limite superior (anomalias): {anomaly_threshold_upper:.2f}")
        print(f"- Limite inferior (anomalias): {anomaly_threshold_lower:.2f}")
        print(f"- Total de anomalias: {total_anomalies}")
        print(f"  -> Acima do limite: {len(anomalies_upper)}")
        print(f"  -> Abaixo do limite: {len(anomalies_lower)}")

# Função para salvar gráficos com linha da média
def save_graphs_with_mean(df):
    def save_plot_with_mean(column, title, ylabel, filename, highlight_anomalies=False):
        # Calcula a média
        mean_value = df[column].mean()

        fig = px.line(
            df, x='timestamp', y=column,
            title=title,
            labels={'timestamp': 'Horário', column: ylabel},
            line_shape='linear'
        )

        # Adiciona linha da média
        fig.add_scatter(
            x=df['timestamp'],
            y=[mean_value] * len(df),
            mode='lines',
            line=dict(dash='dot', color='green'),
            name='Média'
        )

        # Adiciona marcadores para anomalias de CPU (se aplicável)
        if highlight_anomalies and column == 'cpu_usage_percent':
            fig.add_scatter(
                x=df[df['cpu_anomaly']]['timestamp'],
                y=df[df['cpu_anomaly']]['cpu_usage_percent'],
                mode='markers',
                marker=dict(color='red', size=8),
                name='Anomalias de CPU'
            )

        # Salva o gráfico
        fig.write_html(f"{args.output}/{filename}.html")
        fig.show()

    # Gráficos gerais com linha da média
    save_plot_with_mean('cpu_usage_percent', "Uso de CPU (%)", "Uso de CPU (%)", "cpu_usage_with_mean", highlight_anomalies=True)
    save_plot_with_mean('memory_usage_percent', "Uso de Memória (%)", "Uso de Memória (%)", "memory_usage_percent_with_mean")
    save_plot_with_mean('memory_usage_mb', "Uso de Memória (MB)", "Memória Usada (MB)", "memory_usage_mb_with_mean")

# Imprime relatório detalhado no terminal
print_detailed_report(df, args.std_dev)

# Salva os gráficos com linha da média
save_graphs_with_mean(df)

