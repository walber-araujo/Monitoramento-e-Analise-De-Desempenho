import pandas as pd
import argparse
import os
import plotly.express as px

# Argumentos para o arquivo CSV de entrada e o diretório de saída para gráficos
parser = argparse.ArgumentParser(description="Análise de desempenho da aplicação")
parser.add_argument("-i", "--input", type=str, required=True, help="Arquivo CSV de entrada")
parser.add_argument("-o", "--output", type=str, default="output_graphs", help="Diretório de saída para gráficos")
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

# Função para salvar gráficos
def save_graphs(df):
    def save_plot(column, title, ylabel, filename, highlight_anomalies=False):
        fig = px.line(
            df, x='timestamp', y=column,
            title=title,
            labels={'timestamp': 'Horário', column: ylabel},
            line_shape='linear'
        )
        
        # Adiciona marcadores para anomalias de CPU
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

    # Gráficos gerais
    save_plot('cpu_usage_percent', "Uso de CPU (%)", "Uso de CPU (%)", "cpu_usage")
    save_plot('memory_usage_percent', "Uso de Memória (%)", "Uso de Memória (%)", "memory_usage_percent")
    save_plot('memory_usage_mb', "Uso de Memória (MB)", "Memória Usada (MB)", "memory_usage_mb")

    # Gráficos com destaques de anomalias de CPU
    save_plot('cpu_usage_percent', "Uso de CPU com Anomalias", "Uso de CPU (%)", "cpu_anomalies", highlight_anomalies=True)

# Salva os gráficos
save_graphs(df)
