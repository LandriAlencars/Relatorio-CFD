#!/bin/bash
#
# Script para encontrar todos os arquivos .csv de resultados,
# renomeá-los de forma descritiva e copiá-los para uma única pasta.

echo "===== INICIANDO COLETA DE ARQUIVOS DE RESULTADO (.csv) ====="

# --- CONFIGURAÇÃO ---
# Edite estas variáveis para corresponder à sua estrutura de pastas.

# 1. Diretório onde a busca deve começar.
SEARCH_DIR="/home/landri-alencar/CFD/Relatorio-cfd"

# 2. Nova pasta onde todos os arquivos CSV serão salvos.
DEST_DIR="${SEARCH_DIR}/resultados_csv_coletados"

# --- EXECUÇÃO ---

# Cria o diretório de destino, se ele não existir.
echo ">> Criando pasta de destino: ${DEST_DIR}"
mkdir -p "${DEST_DIR}"

# Encontra todos os arquivos .csv dentro do diretório de busca.
# O 'find' procura os arquivos e o 'while' processa cada um encontrado.
find "${SEARCH_DIR}" -type f -name "*.csv" | while IFS= read -r csv_file; do

    # --- Lógica para criar um novo nome descritivo ---
    # Remove o caminho base do nome do arquivo.
    # Ex: /path/to/agua/100/finer/case/perfil.csv -> agua/100/finer/case/perfil.csv
    temp_path="${csv_file#$SEARCH_DIR/}"

    # Substitui todas as barras '/' por underscores '_' para criar um nome único.
    # Ex: agua/100/finer/case/perfil.csv -> agua_100_finer_case_perfil.csv
    new_name="${temp_path//\//_}"

    # Copia o arquivo original para o diretório de destino com o novo nome.
    cp "${csv_file}" "${DEST_DIR}/${new_name}"

    echo "Copiado e renomeado: ${DEST_DIR}/${new_name}"

done

echo ""
echo "===== COLETA CONCLUÍDA! ====="
echo "Todos os arquivos .csv foram salvos em: ${DEST_DIR}"
