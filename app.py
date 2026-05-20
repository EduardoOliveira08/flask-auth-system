from flask import Flask, render_template
from flask import request
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, url_for

app = Flask(__name__)

app.secret_key = 'qualquer_coisa_segura'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():    
    if request.method == 'POST':
        usr = request.form.get('usrLogin')
        senha = request.form.get('senhaLogin')

        if not usr or not senha:
            return "Preencha todos os campos"

        conexao = conectar_db()
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT password FROM usuarios WHERE username = %s",
            (usr,)
        )
        resultado = cursor.fetchone()

        cursor.close()
        conexao.close()

        if resultado:
            senha_hash = resultado[0]

            if check_password_hash(senha_hash, senha):
                session['usuario'] = usr
                return redirect(url_for('dashboard'))
            else:
                return "Senha incorreta"
        else:
            return "Usuário não existe"

    return render_template('login.html')

@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    if request.method == 'POST':
        usr = request.form.get('usr')
        senha = request.form.get('senha')

        if not usr or not senha:
            return "Preencha todos os campos"
        
        senha_hash = generate_password_hash(senha)

        # Conectar ao banco de dados
        conexao = conectar_db()
        cursor = conexao.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (usr,))
        if cursor.fetchone():
            cursor.close()
            conexao.close()
            return "Usuário já existe"

        # Inserir novo usuário
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (usr, senha_hash))
        conexao.commit()
        

        # Fechar conexão
        cursor.close()
        conexao.close()

        return f'Usuário cadastrado: {usr}'
    
    return render_template('cadastro.html')

@app.route('/admin')
def admin():
    if 'usuario' not in session:
        return "Acesso negado"
    
    return f"Bem-vindo, {session['usuario']}"

@app.route('/logout')
def logout():

    session.pop('usuario', None)

    return redirect(url_for('login'))

def conectar_db():
    return mysql.connector.connect(
        host='localhost',
        user='SEU_USUÁRIO',
        password='SUA_SENHA',
        database='sistema'
    )

@app.route('/dashboard')
def dashboard():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    return render_template(
        'dashboard.html',
        usuario=session['usuario']
    )


if __name__ == '__main__':
    app.run(port=5001)