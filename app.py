from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'supersecretkey'

FLAG = "ctf7{y0u_f0rg3d_4_pR1c3_h4ck}"

# Images
IMG_PRODUCT = "https://images.moneycontrol.com/static-mcnews/2025/09/20250910071127_iPhone-17-pro-2.png?impolicy=website&width=770&height=431"
IMG_INSUFF  = "https://i.makeagif.com/media/2-20-2024/rRQyAY.gif"  # show on insufficient funds / failed topup
IMG_AFTER   = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTtiQ2TBCEUk0Gh5xFS7bn6eU_uiJddQ-gbyw&s"  # after buying

PRODUCT = {
    "name": "iPhone 17 Pro Max",
    "price": 1099.00,
    "image_url": IMG_PRODUCT,
}

BASE_HTML = """
<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Buy the new iPhone 17 Pro Max</title>
<style>
  body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:#f0f2f5;margin:0;min-height:100vh;display:flex;justify-content:center}
  .header{position:fixed;left:0;right:0;top:0;background:#232f3e;color:#fff;padding:1rem 2rem;box-shadow:0 2px 10px rgba(0,0,0,.2)}
  .header h1{margin:0;color:#ff9900}
  .container{background:#fff;margin-top:100px;max-width:900px;padding:3rem;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,.1)}
  .product-card{display:flex;gap:2rem;align-items:center;justify-content:space-around;flex-wrap:wrap}
  .product-image{max-width:400px;border-radius:10px;box-shadow:0 4px 10px rgba(0,0,0,.1)}
  .price{font-size:2rem;color:#B12704;font-weight:700;margin:.25rem 0}
  .balance{font-size:1.25rem;color:#232f3e}
  .btn{background:#ff9900;color:#fff;border:0;padding:12px 22px;border-radius:8px;font-weight:700;cursor:pointer}
  .btn[disabled]{opacity:.6;cursor:not-allowed}
  .message-box{margin-top:1.25rem;padding:1rem;border-radius:10px;border:2px solid transparent}
  .success-message{color:#28a745;border-color:#28a745}
  .error-message{color:#dc3545;border-color:#dc3545}
  .topup-form{margin-top:1rem;background:#f8f8f8;padding:1rem;border-radius:8px}
  .payment-form-container{display:flex;gap:2rem;flex-wrap:wrap;align-items:center;justify-content:center}
  .card-container{perspective:1000px}
  .card{width:320px;height:200px;position:relative;transform-style:preserve-3d;transition:transform .6s;border-radius:15px;box-shadow:0 10px 20px rgba(0,0,0,.2)}
  .card.flipped{transform:rotateY(180deg)}
  .face{position:absolute;inset:0;backface-visibility:hidden;border-radius:15px;color:#fff;display:flex;flex-direction:column;justify-content:space-between;padding:20px}
  .front{background:linear-gradient(45deg,#007bff,#00c6ff)}
  .back{background:linear-gradient(45deg,#00c6ff,#007bff);transform:rotateY(180deg)}
  .strip{height:36px;background:#000;border-radius:4px;margin-top:6px}
  .cvvline{background:#fff;color:#000;padding:6px 8px;border-radius:4px;text-align:right;font-weight:700}
  .payment-form{background:#fff;padding:1.5rem;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,.08);max-width:480px}
  .payment-form input[type=text]{width:100%;padding:10px;margin-bottom:12px;border:1px solid #ccc;border-radius:5px}
  .progress-bar-container{width:80%;background:#e0e0e0;border-radius:5px;margin:20px auto;overflow:hidden}
  .progress-bar{height:30px;width:0;background:#ff9900;transition:width 1s;line-height:30px;color:#fff;font-weight:700;text-align:center}
  @media(max-width:768px){.product-card{flex-direction:column;text-align:center}}
</style>
</head><body>
<div class="header"><h1>Amazon CTF</h1></div>

<div class="container">
  {% if message %}
    <div class="message-box {{ 'success-message' if success else 'error-message' }}">{{ message }}</div>

    {% if show_insufficient_gif %}
      <div style="margin-top:10px;text-align:center">
        <img src="{{ insuff_gif }}" alt="Insufficient funds" style="max-width:360px;width:100%;border-radius:10px">
      </div>
    {% endif %}

    {% if show_after_buy_image %}
      <div style="margin-top:10px;text-align:center">
        <img src="{{ after_img }}" alt="Enjoy your iPhone" style="max-width:420px;width:100%;border-radius:10px">
      </div>
    {% endif %}

  {% else %}
    {% if request.path == '/topup' %}
      <div class="payment-form-container">
        <div class="card-container">
          <div class="card" id="card">
            <div class="face front">
              <div style="align-self:flex-end;font-weight:700">VISA</div>
              <div id="cc-num">4242 4242 4242 4242</div>
              <div style="display:flex;justify-content:space-between">
                <div id="cc-holder">CTF CHALLENGER</div>
                <div id="cc-exp">12/26</div>
              </div>
            </div>
            <div class="face back">
              <div class="strip"></div>
              <div class="cvvline">CVV: <span id="cvv-out">***</span></div>
            </div>
          </div>
        </div>
        <div class="payment-form">
          <h2>Credit Card Details</h2>
          <form action="/process_payment" method="post">
            <input type="text" name="card_number" id="in-card" value="4242 4242 4242 4242" required>
            <input type="text" name="expiry" id="in-exp" value="12/26" required>
            <input type="text" name="cvv" id="in-cvv" placeholder="CVV" maxlength="4" required>
            <input type="hidden" name="amount" value="{{ amount }}">
            <button type="submit" class="btn">Pay ${{ '%.2f' % amount }}</button>
          </form>
        </div>
      </div>

    {% elif request.path == '/payment_processing' %}
      <div class="payment-pending">
        <h2 style="color:#ff9900">Processing your payment…</h2>
        <div class="progress-bar-container"><div class="progress-bar" id="pb"></div></div>

        <!-- Auto-submit via GET; default = failed txn. -->
        <form action="/check_status" method="get" id="status-form">
          <input type="hidden" name="status"  id="status"  value="cancel">
          <input type="hidden" name="payment" id="payment" value="pending">
          <input type="hidden" name="amount"  value="{{ amount }}">
        </form>

        <script>
          const pb=document.getElementById('pb');
          let w=0; const t=setInterval(()=>{ w+=20; pb.style.width=w+'%'; pb.textContent=w+'%';
            if(w>=100){ clearInterval(t); document.getElementById('status-form').submit(); }
          },400);
        </script>
      </div>

    {% else %}
      <div class="product-card">
        <img src="{{ product.image_url }}" alt="Product Image" class="product-image">
        <div>
          <h1>{{ product.name }}</h1>
          <p class="price">US$ {{ '%.2f' % product.price }}</p>
          <p class="balance">Your Balance: US$ {{ '%.2f' % session.get('balance', 0) }}</p>
          <div style="display:flex;gap:1rem;margin-top:1rem">
            <form action="/purchase" method="post">
              <button type="submit" class="btn" {% if session.get('balance',0) < product.price %}disabled{% endif %}>Buy Now</button>
            </form>
          </div>
          <div class="topup-form">
            <form action="/topup" method="post">
              <label>Add funds (test gateway): </label>
              <input type="number" name="amount" value="500" min="1" step="1" required>
              <button type="submit" class="btn">Proceed to Pay</button>
            </form>
          </div>
        </div>
      </div>
    {% endif %}
  {% endif %}

  <div style="margin-top:2rem;color:#888">&copy; 2024 Amazon CTF</div>
</div>

<script>
  // Live card UI + CVV on the back
  const card=document.getElementById('card');
  const inCard=document.getElementById('in-card');
  const inExp=document.getElementById('in-exp');
  const inCVV=document.getElementById('in-cvv');
  const numOut=document.getElementById('cc-num');
  const expOut=document.getElementById('cc-exp');
  const cvvOut=document.getElementById('cvv-out');

  function fmtNum(s){ return s.replace(/\\D/g,'').slice(0,16).replace(/(.{4})/g,'$1 ').trim(); }
  if(inCard&&numOut){ inCard.addEventListener('input',()=>numOut.textContent=fmtNum(inCard.value)); }
  if(inExp&&expOut){ inExp.addEventListener('input',()=>expOut.textContent=inExp.value.toUpperCase()); }
  if(inCVV&&cvvOut){
    inCVV.addEventListener('focus',()=>card.classList.add('flipped'));
    inCVV.addEventListener('blur', ()=>card.classList.remove('flipped'));
    inCVV.addEventListener('input',()=>cvvOut.textContent=(inCVV.value.replace(/\\D/g,'').slice(0,4)||'***'));
  }
</script>
</body></html>
"""

@app.route("/")
def index():
    if "balance" not in session:
        session["balance"] = 69.00
    return render_template_string(BASE_HTML, product=PRODUCT)

@app.route("/topup", methods=["POST"])
def topup():
    amount = float(request.form.get("amount", "0") or 0)
    return render_template_string(BASE_HTML, amount=amount, product=PRODUCT)

@app.route("/process_payment", methods=["POST"])
def process_payment():
    # Cosmetic CVV gate for realism
    cvv = request.form.get("cvv","")
    amount = float(request.form.get("amount","0") or 0)
    if cvv != "123":
        return render_template_string(
            BASE_HTML, message="Invalid CVV.", success=False, product=PRODUCT,
            show_insufficient_gif=True, insuff_gif=IMG_INSUFF
        )
    return redirect(url_for("payment_processing", amount=amount))

@app.route("/payment_processing")
def payment_processing():
    amount = float(request.args.get("amount","0") or 0)
    return render_template_string(BASE_HTML, amount=amount, product=PRODUCT)

# Allow GET + POST so players can use URL or Burp
@app.route("/check_status", methods=["GET","POST"])
def check_status():
    p = request.values
    amount  = float(p.get("amount","0") or 0)
    status  = p.get("status","cancel")
    payment = p.get("payment","pending")

    # Vulnerable: trusts client-supplied params
    if status == "success" and payment == "success":
        session["balance"] = session.get("balance",0.0) + amount
        msg = f"Successfully added US$ {amount:.2f}. New balance: US$ {session['balance']:.2f}."
        return render_template_string(BASE_HTML, message=msg, success=True, product=PRODUCT)

    # Show the GIF on failed/pending payment
    return render_template_string(
        BASE_HTML,
        message="Payment failed or insuficient funds. No funds added.",
        success=False,
        product=PRODUCT,
        show_insufficient_gif=True,
        insuff_gif=IMG_INSUFF
    )

@app.route("/purchase", methods=["POST"])
def purchase():
    if session.get("balance",0.0) >= PRODUCT["price"]:
        session["balance"] -= PRODUCT["price"]
        msg = f"Congratulations! You bought the iPhone. Here's your flag: {FLAG}"
        return render_template_string(
            BASE_HTML, message=msg, success=True, product=PRODUCT,
            show_after_buy_image=True, after_img=IMG_AFTER
        )
    # Also show GIF here when buying fails due to low balance
    return render_template_string(
        BASE_HTML,
        message="Insufficient funds. Please top up your account.",
        success=False,
        product=PRODUCT,
        show_insufficient_gif=True,
        insuff_gif=IMG_INSUFF
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
