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
    plt.style.use('default')  # Corrigido
    
    resultados = []  # Para armazenar resultados
    
    # Processa cada caso
    for (fluid, flow_rate), group in df.groupby(['fluido', 'vazao_uL_min']):
        group = group.sort_values('n_cells')
        
        n_cells = group['n_cells'].values
        errors = group['erro_relativo_%'].values
        
        print(f"\n--- {fluid.capitalize()} Q={flow_rate} ---")
        print(f"Número de células: {n_cells}")
        print(f"Erros relativos (%): {errors}")
        
        # Calcula h (tamanho característico) - CORREÇÃO IMPORTANTE
        h = n_cells**(-1/3)  # h ∝ N^(-1/3)
        log_h = np.log(h)
        log_err = np.log(errors)
        
        print(f"Tamanho característico h: {h}")
        print(f"Log(h): {log_h}")
        print(f"Log(Erro): {log_err}")
        
        # Regressão linear: log(erro) vs log(h)
        slope, intercept = np.polyfit(log_h, log_err, 1)
        p = slope  # CORREÇÃO: p = slope quando usamos log(erro) vs log(h)
        
        print(f"Inclinação (slope): {slope:.4f}")
        print(f"Ordem de convergência (p): {p:.4f}")
        
        # Coeficiente de determinação R²
        residuals = log_err - (slope * log_h + intercept)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((log_err - np.mean(log_err))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        print(f"R²: {r_squared:.4f}")
        
        # Armazena resultados
        resultados.append({
            'fluido': fluid,
            'vazao': flow_rate,
            'ordem_convergencia': p,
            'r_quadrado': r_squared
        })
        
        # Plota - CORRIGIDO: log(erro) vs log(N) para visualização
        label = f'{fluid.capitalize()} Q={int(flow_rate)} (p={p:.2f})'
        plt.plot(np.log(n_cells), log_err, 'o-', markersize=8, label=label, alpha=0.8)
        
        # Linha de tendência (opcional)
        trend = slope * log_h + intercept
        # Se quiser plotar no mesmo gráfico, converter de volta para log(N)
        trend_in_logN = slope * (-1/3) * np.log(n_cells) + intercept
        plt.plot(np.log(n_cells), trend_in_logN, '--', alpha=0.5)
    
    # Finaliza gráfico - CORRIGIDO rótulos
    plt.xlabel('Log(Número de Células)', fontsize=12)
    plt.ylabel('Log(Erro Relativo %)', fontsize=12)
    plt.title('Convergência de Malha - Log(Erro) vs Log(N)', fontsize=14)
    plt.legend(title='Caso (Ordem p)', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, which="both", linestyle='--', alpha=0.7)
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    
    plt.savefig(OUTPUT_FILENAME, dpi=300, bbox_inches='tight')
    print(f"\nGráfico salvo como '{OUTPUT_FILENAME}'")
    
    # Exibe resumo dos resultados
    print("\n=== RESUMO DAS ORDENS DE CONVERGÊNCIA ===")
    df_resultados = pd.DataFrame(resultados)
    print(df_resultados.to_string(index=False))
    
    # Estatísticas
    if len(resultados) > 0:
        p_values = [r['ordem_convergencia'] for r in resultados]
        print(f"\nOrdem de convergência média: {np.mean(p_values):.2f}")
        print(f"Desvio padrão: {np.std(p_values):.2f}")

except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
