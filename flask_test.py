
import io
import base64
from flask import Flask, render_template, request

# Mode headless pour Matplotlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Import de SymPy pour le calcul symbolique
import sympy as sp

app = Flask(__name__)

def generer_bode_avec_sympy(k_val, wc_val):
    # 1. Calcul symbolique avec SymPy
    omega, k, wc = sp.symbols('omega k wc', real=True, positive=True)
    j = sp.I
    
    # Définition symbolique de la fonction de transfert du passe-bas d'ordre 1
    H_sym = k / (1 + j * (omega / wc))
    
    # Optionnel : on peut par exemple afficher ou manipuler le module symbolique
    # module_sym = sp.simplify(sp.Abs(H_sym))
    
    # Conversion de l'expression en chaîne LaTeX pour l'afficher dans le HTML
    latex_expression = sp.latex(H_sym)

    # 2. Génération numérique pour Matplotlib
    omega_vals = np.logspace(np.log10(wc_val) - 2, np.log10(wc_val) + 2, 400)
    H_num = k_val / (1 + 1j * (omega_vals / wc_val))
    
    gain_db = 20 * np.log10(np.abs(H_num))
    phase_deg = np.angle(H_num, deg=True)

    # Création du graphique Matplotlib
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
    
    ax1.semilogx(omega_vals, gain_db, color='#1f77b4', lw=2)
    ax1.set_ylabel('Gain (dB)')
    ax1.grid(True, which="both", ls="--", alpha=0.5)
    ax1.set_title(f'Bode - k={k_val}, $\\omega_c$={wc_val}')

    ax2.semilogx(omega_vals, phase_deg, color='#ff7f0e', lw=2)
    ax2.set_ylabel('Phase (°)')
    ax2.set_xlabel('Pulsation $\\omega$ (rad/s)')
    ax2.grid(True, which="both", ls="--", alpha=0.5)

    plt.tight_layout()

    # Sauvegarde dans un buffer mémoire
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100)
    img_buffer.seek(0)
    plt.close(fig)

    img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    return latex_expression, img_str

@app.route('/', methods=['GET', 'POST'])
def index():
    k = 1.0
    wc = 100.0
    
    if request.method == 'POST':
        try:
            k = float(request.form.get('k', 1.0))
            wc = float(request.form.get('wc', 100.0))
            if wc <= 0: wc = 1.0
        except ValueError:
            pass

    latex_expr, img_data = generer_bode_avec_sympy(k, wc)
    return render_template('index.html', k=k, wc=wc, latex_expr=latex_expr, img_data=img_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
