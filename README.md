# Projeto de Monitoramento e Análise de Desempenho

Este projeto oferece uma solução para monitoramento de processos, análise de desempenho e auditoria de anomalias em aplicações.
Ele coleta dados de uso de CPU, memória, E/S e conexões de rede, gera gráficos interativos, detecta anomalias e fornece relatórios detalhados para análise.

## Estrutura do Projeto

O projeto é composto por três scripts principais:
 
1. **monitor.py**: Coleta dados de desempenho de processos ou PIDs especificados.
2. **analise.py**: Realiza a análise dos dados coletados, gerando gráficos interativos e detectando anomalias.
3. **auditoria.py**: Realiza a auditoria das anomalias detectadas, coletando logs do sistema e gerando um relatório em formato JSON.

Além disso, o `Makefile` fornece uma maneira simples de executar as tarefas de monitoramento, auditoria e análise.

## Requisitos

- Python 3.x
- Bibliotecas Python:
   - `psutil`
   - `pandas`
   - `plotly`
- Sistema operacional macOS (para coleta de logs com `log show`)
- Dependências podem ser instaladas usando um ambiente virtual Python, como `venv`.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

Crie e ative um ambiente virtual:

```bash
python3 -m venv MyVenv
source MyVenv/bin/activate   # No macOS/Linux
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

# Uso

## Monitoramento

O script **monitor.py** coleta dados de desempenho de um processo específico ou PID. É possível monitorar um processo por nome ou um PID diretamente.
Os dados são salvos em um arquivo CSV.

Exemplo de uso:

Para monitorar um processo pelo nome, execute:

```bash
make monitor PROCESS_NAME="nome_do_processo" INTERVAL=1.0 OUTPUT_CSV="output.csv"
```

Ou, caso queira monitorar um processo pelo PID, execute:

```bash
make monitor PID=1234 INTERVAL=1.0 OUTPUT_CSV="output.csv"
```

**Parâmetros**:

- `PROCESS_NAME`: Nome do processo que será monitorado. Exemplo: "nome_do_processo".
- `PID`: ID do processo a ser monitorado. Pode ser usado em vez de `PROCESS_NAME`.
- `INTERVAL`: Intervalo de tempo (em segundos) entre as coletas de dados.
- `OUTPUT_CSV`: Nome do arquivo CSV onde os dados de desempenho serão salvos.

## Análise

O script **analise.py** recebe os dados de desempenho coletados e gera gráficos interativos, além de detectar anomalias com base no número de desvios padrão especificado.

Exemplo de uso:

```bash
make analysis INPUT_CSV="output.csv" GRAPH_DIR="graphs"
```

**Parâmetros**:

- `INPUT_CSV`: O arquivo CSV com os dados de desempenho a ser analisado.
- `GRAPH_DIR`: Diretório onde os gráficos gerados serão salvos.

## Auditoria

O script **auditoria.py** realiza a auditoria das anomalias detectadas, coletando logs do sistema para os PIDs com anomalias e gerando um relatório detalhado em formato JSON.

Exemplo de uso:

```bash
make audit
```

**Parâmetros**:

- `INPUT_CSV`: O arquivo CSV com as anomalias detectadas.
- `OUTPUT_DIR`: Diretório onde os relatórios de auditoria em formato JSON serão salvos.

Arquivos Gerados

Os seguintes arquivos podem ser gerados pelo projeto:

- **output.csv**: Arquivo CSV contendo os dados de desempenho coletados (timestamp, nome do processo, PID, uso de CPU, uso de memória, leituras de I/O, conexões de rede).
- **anomalies.csv**: Arquivo CSV contendo as anomalias detectadas durante a análise de desempenho.
- **graphs/**: Diretório contendo os gráficos gerados pelo script de análise, salvos no formato HTML.
- **auditoria/**: Diretório contendo os relatórios de auditoria em formato JSON.

Exemplo de Arquivo CSV de Saída

O arquivo `output.csv` gerado pelo script de monitoramento terá o seguinte formato:

```csv
timestamp;process_name;pid;cpu_usage_percent;memory_usage_percent;memory_usage_mb;io_reads;io_writes;network_connections
2024-11-15 19:48:47;nome_do_processo;1234;15.2;30.3;2048;500;300;3
2024-11-15 19:48:49;nome_do_processo;1234;14.7;31.0;2050;510;310;3
```
