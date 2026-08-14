
from flask import Flask, send_from_directory, request, jsonify
import sqlite3, os, datetime

# pasta do projeto no Render (funciona em qualquer lugar)
BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

def db():
    db_path = os.path.join(BASE, "database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def h(): return send_from_directory(BASE,'index.html')

@app.route('/cliente')
def cliente_page(): return send_from_directory(BASE,'cliente.html')

@app.route('/cliente.html')
def cli(): return send_from_directory(BASE,'cliente.html')

@app.route('/admin')
def admin_page(): return send_from_directory(BASE,'admin.html')

@app.route('/admin.html')
def admin_html(): return send_from_directory(BASE,'admin.html')

@app.route('/dashboard')
@app.route('/dashboard.html')
def dashboard(): return send_from_directory(BASE,'dashboard.html')

@app.route('/api/produtos', methods=['GET','POST','PUT'])
def produtos():
    c=db()
    if request.method=='GET':
        rows=c.execute("SELECT * FROM produtos").fetchall(); c.close(); return jsonify([dict(r) for r in rows])
    if request.method=='POST':
        j=request.json; c.execute("INSERT INTO produtos (nome,preco_base,preco_final,foto,descricao) VALUES (?,?,?,?,?)",(j['nome'],j['preco_base'],j['preco_final'],j['foto'],j['descricao'])); c.commit(); c.close(); return jsonify({"ok":True})
    if request.method=='PUT':
        j=request.json; c.execute("UPDATE produtos SET preco_final=?, foto=?, descricao=? WHERE id=?",(j['preco_final'],j['foto'],j['descricao'],j['id'])); c.commit(); c.close(); return jsonify({"ok":True})

@app.route('/api/vendas', methods=['GET','POST'])
def vendas():
    c=db()
    if request.method=='POST':
        j=request.json
        prod=c.execute("SELECT * FROM produtos WHERE id=?",(j['produto_id'],)).fetchone()
        preco_final = prod['preco_final'] if prod else j.get('preco_final',0)
        cur=c.execute("INSERT INTO vendas (cliente,telefone,produto_id,preco_final,status,criado) VALUES (?,?,?,?,?,?)",(j['cliente'],j['telefone'],j['produto_id'],preco_final,'comprado',datetime.datetime.now().strftime("%d/%m"))).lastrowid
        c.commit(); c.close(); return jsonify({"id":cur, "preco":preco_final})
    cliente=request.args.get('cliente')
    if cliente: rows=c.execute("SELECT v.*, p.nome as produto_nome FROM vendas v JOIN produtos p ON v.produto_id=p.id WHERE v.cliente LIKE? ORDER BY v.id DESC",(f"%{cliente}%",)).fetchall()
    else: rows=c.execute("SELECT v.*, p.nome as produto_nome FROM vendas v JOIN produtos p ON v.produto_id=p.id ORDER BY v.id DESC").fetchall()
    c.close(); return jsonify([dict(r) for r in rows])

@app.route('/api/etapas', methods=['GET','POST'])
def etapas():
    c=db()
    if request.method=='POST':
        j=request.json; c.execute("INSERT INTO etapas (venda_id,tipo,data,hora,foto,obs) VALUES (?,?,?,?,?,?)",(j['venda_id'],j['tipo'],j['data'],j['hora'],j.get('foto',''),j.get('obs',''))); c.commit(); c.close(); return jsonify({"ok":True})
    venda_id=request.args.get('venda_id')
    rows=c.execute("SELECT * FROM etapas WHERE venda_id=? ORDER BY id",(venda_id,)).fetchall(); c.close(); return jsonify([dict(r) for r in rows])

@app.route('/<path:f>')
def files(f): return send_from_directory(BASE,f)

if __name__=='__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
