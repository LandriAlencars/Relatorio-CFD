import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURAÇÃO ---
FILENAME = "resumo_analise_completa.csv"
OUTPUT_FILENAME = "grafico_convergencia_loglog_geral.png"

MESH_SIZE_MAP = {
    'coarse': 500,
    'normal': 1372,
    'fine': 3700,
    'finer': 9996
}

try:
    df = pd.read_csv(FILENAME)
    print(f"Arquivo '{FILENAME}' lido com sucesso.")
    
    # Adiciona número de células
    df['n_cells'] = df['malha'].map(MESH_SIZE_MAP)
    
    # VERIFICAÇÃO DOS DADOS
    print("\n=== ANÁLISE DETALHADA DOS DADOS ===")
    
    # Prepara a figura
    plt.figure(figsize=(12, 9))
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Processa cada caso
    for (fluid, flow_rate), group in df.groupby(['fluido', 'vazao_uL_min']):
        group = group.sort_values('n_cells')
        
        n_cells = group['n_cells'].values
        errors = group['erro_relativo_%'].values
        
        print(f"\n--- {fluid.capitalize()} Q={flow_rate} ---")
        print(f"Número de células: {n_cells}")
        print(f"Erros relativos (%): {errors}")
        
        # Verifica se os erros estão diminuindo com refinamento
        if len(errors) > 1:
            error_reduction = errors[:-1] / errors[1:]
            print(f"Redução do erro entre malhas: {error_reduction}")
        
        # Calcula logs
        log_n = np.log(n_cells)
        log_err = np.log(errors)
        
        print(f"Log(N): {log_n}")
        print(f"Log(Erro): {log_err}")
        
        # Regressão linear
        slope, intercept = np.polyfit(log_n, log_err, 1)
        p = -slope
        
        print(f"Inclinação (slope): {slope:.4f}")
        print(f"Ordem de convergência (p): {p:.4f}")
        
        # Coeficiente de determinação R²
        residuals = log_err - (slope * log_n + intercept)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((log_err - np.mean(log_err))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        print(f"R²: {r_squared:.4f}")
        
        # Plota
        label = f'{fluid.capitalize()} Q={int(flow_rate)} (p={p:.2f})'
        plt.plot(log_n, log_err, 'o-', markersize=8, label=label, alpha=0.8)
        
        # Linha de tendência
        trend = slope * log_n + intercept
        plt.plot(log_n, trend, '--', alpha=0.5)
    
    # Finaliza gráfico
    plt.xlabel('Log(Número de Células)', fontsize=12)
    plt.ylabel('Log(Erro Relativo %)', fontsize=12)
    plt.title('Gráfico de Convergência de Malha (Log-Log) para Todos os Casos', fontsize=14)
    plt.legend(title='Caso (Ordem de Convergência, p)', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, which="both", linestyle='--', alpha=0.7)
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    
    plt.savefig(OUTPUT_FILENAME, dpi=300, bbox_inches='tight')
    print(f"\nGráfico salvo como '{OUTPUT_FILENAME}'")

except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
