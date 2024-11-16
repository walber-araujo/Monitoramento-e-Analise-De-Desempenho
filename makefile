# Makefile para execução das análises e auditorias

# Definição das variáveis com valores padrão
PROCESS_NAME ?= "default_process"  # Nome do processo, padrão é "default_process"
PID ?= ""  # PID, por padrão vazio
INPUT_CSV ?= "anomalies.csv"  # Arquivo CSV de entrada para auditoria
OUTPUT_CSV ?= "output.csv"  # Arquivo CSV de saída para análise
GRAPH_DIR ?= "graphs"  # Diretório de saída para gráficos
INTERVAL ?= 1.0  # Intervalo de coleta em segundos
ANOMALY_THRESHOLD ?= 2.0  # Limiar de CPU para análise (usado para auditoria)
STD_DEV ?= 3  # Número de desvios padrão para detecção de anomalias
OUTPUT_DIR ?= "auditoria"  # Diretório de saída para o relatório de auditoria

# Função strip para limpar espaços extras
PROCESS_NAME := $(strip $(PROCESS_NAME))
PID := $(strip $(PID))
INPUT_CSV := $(strip $(INPUT_CSV))
OUTPUT_CSV := $(strip $(OUTPUT_CSV))
GRAPH_DIR := $(strip $(GRAPH_DIR))
INTERVAL := $(strip $(INTERVAL))
ANOMALY_THRESHOLD := $(strip $(ANOMALY_THRESHOLD))
STD_DEV := $(strip $(STD_DEV))
OUTPUT_DIR := $(strip $(OUTPUT_DIR))

# Comandos que serão usados
PYTHON3 = sudo python3  # Inclui `sudo` no comando

# Alvo para executar o script de monitoramento
monitor:
	@echo "Executando monitoramento do processo ou PID..."
	@if [ -n "$(PID)" ] && [ "$(PID)" != " " ]; then \
		echo "Monitorando PID: $(PID) com intervalo de $(INTERVAL) segundos"; \
		$(PYTHON3) monitor.py -p "$(PID)" -o "$(OUTPUT_CSV)" -i "$(INTERVAL)"; \
	elif [ -n "$(PROCESS_NAME)" ] && [ "$(PROCESS_NAME)" != " " ]; then \
		echo "Monitorando processo: $(PROCESS_NAME) com intervalo de $(INTERVAL) segundos"; \
		$(PYTHON3) monitor.py -n "$(PROCESS_NAME)" -o "$(OUTPUT_CSV)" -i "$(INTERVAL)"; \
	else \
		echo "Erro: Nem PID nem PROCESS_NAME foram fornecidos."; \
		exit 1; \
	fi

# Alvo para realizar a auditoria de anomalias
audit:
	@echo "Iniciando auditoria de anomalias com o arquivo $(INPUT_CSV)..."
	$(PYTHON3) auditoria.py -i "$(INPUT_CSV)" -o "$(OUTPUT_DIR)" -t "$(ANOMALY_THRESHOLD)" -std $(STD_DEV)

# Alvo para realizar a análise de desempenho e gerar gráficos
analysis:
	@echo "Iniciando análise de desempenho e geração de gráficos..."
	$(PYTHON3) analise.py -i "$(OUTPUT_CSV)" -o "$(GRAPH_DIR)"

# Alvo para realizar toda a sequência de monitoramento, auditoria e análise
all: monitor audit analysis
	@echo "Processo completo de monitoramento, auditoria e análise finalizado!"

