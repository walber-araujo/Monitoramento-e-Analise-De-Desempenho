# Projeto de Monitoramento e Análise de Desempenho

Este projeto tem como objetivo monitorar processos ou PIDs no sistema, auditar e analisar o uso de CPU e memória, detectando anomalias e gerando gráficos interativos para visualização.

## Estrutura do Projeto

O projeto possui três componentes principais:

1. **monitor.py**: Script responsável por monitorar o uso de CPU e memória de processos ou PIDs específicos, gerando um arquivo CSV de saída.
2. **auditoria.py**: Script que realiza a auditoria de anomalias com base no arquivo CSV gerado pelo `monitor.py`.
3. **analise.py**: Script que realiza a análise de desempenho, gerando gráficos interativos a partir dos dados de entrada.

Além disso, o projeto inclui um **Makefile** para facilitar a execução dos scripts e automação de tarefas.

## Requisitos

Certifique-se de que você tenha o Python 3 instalado, assim como as dependências necessárias. Você pode instalar as dependências executando:

```bash
pip install -r requirements.txt
```

### Dependências

- **pandas**: Para manipulação de dados.
- **plotly**: Para gerar gráficos interativos.
- **argparse**: Para processar argumentos de linha de comando.

## Como Usar

### Passo 1: Monitorar um Processo

O Makefile permite monitorar um processo específico ou um PID. Para isso, você pode usar o alvo `monitor` no Makefile.

```bash
make monitor PROCESS_NAME="nome_do_processo" INTERVAL=1.0 OUTPUT_CSV="output.csv"
```

- **PROCESS_NAME**: Nome do processo que você deseja monitorar (exemplo: `python`).
- **PID**: Alternativamente, você pode fornecer o PID do processo em vez do nome do processo.
- **INTERVAL**: Intervalo de tempo em segundos para coleta de dados.
- **OUTPUT_CSV**: Arquivo CSV onde os dados serão armazenados.

Se você preferir monitorar por PID, passe o `PID` diretamente:

```bash
make monitor PID=12345 INTERVAL=1.0 OUTPUT_CSV="output.csv"
```

### Passo 2: Auditoria de Anomalias

Após coletar os dados de monitoramento, você pode realizar uma auditoria para detectar anomalias de uso de CPU e memória. Para isso, execute o alvo `audit` no Makefile.

```bash
make audit INPUT_CSV="output.csv" ANOMALY_THRESHOLD=2.0 STD_DEV=3
```

- **INPUT_CSV**: Arquivo CSV com os dados coletados (gerado pelo `monitor`).
- **ANOMALY_THRESHOLD**: Limiar de CPU para detecção de anomalias.
- **STD_DEV**: Número de desvios padrão para detectar anomalias.

### Passo 3: Análise de Desempenho e Geração de Gráficos

Com os dados de auditoria, você pode gerar gráficos interativos para visualizar o desempenho. Para isso, use o alvo `analysis` no Makefile:

```bash
make analysis OUTPUT_CSV="output.csv" GRAPH_DIR="graphs"
```

- **OUTPUT_CSV**: Arquivo CSV com os dados coletados.
- **GRAPH_DIR**: Diretório onde os gráficos serão salvos.

### Passo 4: Executar Todo o Processo

Se desejar executar todo o processo (monitoramento, auditoria e análise) em sequência, basta executar o alvo `all` no Makefile:

```bash
make all PROCESS_NAME="nome_do_processo" INTERVAL=1.0 OUTPUT_CSV="output.csv" INPUT_CSV="output.csv" ANOMALY_THRESHOLD=2.0 STD_DEV=3 GRAPH_DIR="graphs"
```

## Makefile

O **Makefile** facilita a execução das diferentes etapas do projeto, permitindo a configuração de variáveis e execução de alvos específicos. As variáveis definidas no Makefile são:

- **PROCESS_NAME**: Nome do processo a ser monitorado (padrão é "default_process").
- **PID**: PID do processo a ser monitorado (padrão é vazio).
- **INPUT_CSV**: Arquivo CSV de entrada para auditoria (padrão é "anomalies.csv").
- **OUTPUT_CSV**: Arquivo CSV de saída para monitoramento (padrão é "monitor_output.csv").
- **GRAPH_DIR**: Diretório onde os gráficos serão salvos (padrão é "graphs").

# Monitoramento-e-Analise-De-Desempenho
# Monitoramento-e-Analise-De-Desempenho
