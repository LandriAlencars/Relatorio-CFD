import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

# --- 1. CONFIGURAÇÃO ---
CSV_DIR = "resultados_csv_coletados"
OUTPUT_DIR = "graficos_comparativos_corrigidos"

# Dicionário com propriedades físicas dos fluidos
FLUID_PROPERTIES = {
    'agua': {'mu': 0.001, 'rho': 1000},
    'isopropilico': {'mu': 0.00204, 'rho': 786}
}

# --- Função robusta para ler CSV com separador automático ---
def ler_csv_robusto(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            amostra = f.read(2048)
            dialect = csv.Sniffer().sniff(amostra, delimiters=[',', ';', '\t'])
            sep = dialect.delimiter
        df = pd.read_csv(filepath, sep=sep, on_bad_lines='skip', engine='python')
        return df
    except Exception as e:
        print(f"!! Erro ao processar o arquivo {os.path.basename(filepath)}: {e}")
        return None

# --- 2. FUNÇÃO: PERFIL DE VELOCIDADE TEÓRICO ---
def theoretical_velocity_shape(y, z, H, W, n_terms=15):
    total = 0
    for n in range(1, 2 * n_terms, 2):  # Soma sobre n ímpares
        term1 = 1 / (n**3)
        term2 = 1 - (np.cosh(n * np.pi * z / H) / np.cosh(n * np.pi * W / (2 * H)))
        term3 = np.sin(n * np.pi * y / H)
        total += term1 * term2 * term3
    return total

# --- 3. LOOP PRINCIPAL DE ANÁLISE ---
os.makedirs(OUTPUT_DIR, exist_ok=True)
summary_results = []

print(f"Iniciando análise geral dos arquivos em '{CSV_DIR}'...")

for filename in os.listdir(CSV_DIR):
    if filename.endswith(".csv"):
        print(f"\nProcessando arquivo: {filename}")

        try:
            # --- Extração robusta de parâmetros do nome do arquivo ---
            parts = filename.replace('.csv', '').split('_')
            if len(parts) < 3:
                print(f"!! Nome de arquivo fora do padrão esperado: {filename}")
                continue

            fluid_name = parts[0].lower().strip()
            flow_rate_str = parts[1]
            mesh_level = parts[2]

            # Extrai apenas o número da vazão (ex: 100 de "100uLmin")
            flow_rate_q = float(re.findall(r"[\d.]+", flow_rate_str)[0])

            # --- Leitura do CSV com detecção automática ---
            filepath = os.path.join(CSV_DIR, filename)
            df_sim = ler_csv_robusto(filepath)
            if df_sim is None or df_sim.empty:
                continue

            # --- Determinar eixo vertical automaticamente ---
            coord_cols = [c for c in df_sim.columns if "Points:" in c]
            y_sim = None
            for col in coord_cols:
                valores = df_sim[col].values
                if np.ptp(valores) > 0:  # tem variação
                    y_sim = valores
                    break
            if y_sim is None:
                raise ValueError("Nenhuma coordenada espacial válida encontrada.")

            # --- Calcular magnitude da velocidade ---
            u_sim = np.sqrt(df_sim['U:0']**2 + df_sim['U:1']**2 + df_sim['U:2']**2)
            u_max_sim = u_sim.max()

            # --- Parâmetros físicos do canal e fluido ---
            H, W, A = 0.0001, 0.0001, 1e-8  # 100 µm × 100 µm
            mu = FLUID_PROPERTIES[fluid_name]['mu']

            # --- Vazão média e velocidade média ---
            Q_sim_si = flow_rate_q * 1.6667e-11  # µL/min → m³/s
            U_avg_sim = Q_sim_si / A

            # --- Umax teórico para canal quadrado ---
            U_max_teorico = 2.096 * U_avg_sim

            # --- Perfil teórico normalizado ---
            y_teorico = np.linspace(0, H, 200)
            shape_profile = theoretical_velocity_shape(y_teorico, 0, H, W)
            u_teorico = shape_profile * (U_max_teorico / shape_profile.max())

            # --- Erro relativo ---
            erro_relativo = abs(u_max_sim - U_max_teorico) / U_max_teorico * 100

            # --- Armazena resumo ---
            summary_results.append({
                'fluido': fluid_name,
                'vazao_uL_min': flow_rate_q,
                'malha': mesh_level,
                'u_max_simulacao': u_max_sim,
                'u_max_teorico': U_max_teorico,
                'erro_relativo_%': erro_relativo
            })

            # --- Gráfico comparativo ---
            plt.figure(figsize=(8, 10))
            plt.plot(y_teorico, u_teorico, 'r-', linewidth=2,
                     label=f'Solução Teórica (Umax={U_max_teorico:.6f} m/s)')
            plt.plot(y_sim, u_sim, 'bo', markerfacecolor='none',
                     label=f'Numérico (Umax={u_max_sim:.6f} m/s)')

            plt.xlabel('Altura do Canal (m)')
            plt.ylabel('Velocidade (m/s)')
            plt.title(f'Comparação - {fluid_name.capitalize()} | Q={flow_rate_q} µL/min | Malha {mesh_level}')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()

            output_plot_filename = f"grafico_{fluid_name}_{flow_rate_q}_{mesh_level}.png"
            plt.savefig(os.path.join(OUTPUT_DIR, output_plot_filename), dpi=300)
            plt.close()

            print(f"-> Gráfico salvo como '{output_plot_filename}'")

        except Exception as e:
            print(f"!! Erro ao processar o arquivo {filename}: {e}")

# --- 4. RESUMO FINAL ---
summary_df = pd.DataFrame(summary_results)
summary_df.to_csv('resumo_analise_completa.csv', index=False, float_format='%.6f')

print("\n===== ANÁLISE GERAL CONCLUÍDA! =====")
print(f"-> Todos os gráficos foram salvos em: '{OUTPUT_DIR}'")
print("-> Resumo com erros salvo em: 'resumo_analise_completa.csv'")

