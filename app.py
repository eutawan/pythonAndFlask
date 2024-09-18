from flask import *
import psycopg2

app = Flask(__name__)
app.secret_key = 'secretkeytawan'

def get_db_connection():
    conn = psycopg2.connect(
        host = "localhost",
        database = "sistemaDeProdutos",
        user = "postgres",
        password = "tawandev"
    )
    return conn

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_user = request.form['loginUser']
        senha = request.form['senha']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM usuario WHERE loginUser = %s AND senha = %s', (login_user, senha))
        usuario = cur.fetchone()
        cur.close()
        conn.close()

        if usuario:
            session['loginUser'] = usuario[0]
            session['tipoUser'] = usuario[2]
            return redirect(url_for('cadastrar_produto'))
        else:
            flash('Credenciais inválidas', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/cadastrar_usuario', methods =['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        login_user = request.form['loginUser']
        senha = request.form['senha']
        tipo_user = request.form['tipoUser']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO usuario(loginUser, senha, tipoUser) VALUES (%s, %s, %s)',
                    (login_user, senha, tipo_user))
        conn.commit()
        cur.close()
        conn.close()

        flash('Usuário cadastrado com sucesso', 'sucess')
        return redirect(url_for('login'))
    return render_template('cadastrar_usuario.html')

@app.route('/cadastrar_produto', methods =['GET', 'POST'])
def cadastrar_produto():
    if 'loginUser' not in session:
        return redirect(url_for('login'))
    
    login_user = session['loginUser']
    tipo_user = session['tipoUser']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT COUNT(*) FROM produto WHERE loginUser = %s', (login_user,))
    total_produtos = cur.fetchone()[0]

    if request.method == 'POST':
        if tipo_user == 'normal' and total_produtos >= 3:
            flash('Usuário normal só pode cadastrar até 3 produtos', 'danger')
        else:
            nome = request.form['nome']
            qtde = request.form['qtde']
            preco = request.form['preco']
            cur.execute('INSERT INTO produto(nome, qtde, preco, loginUser) VALUES (%s, %s, %s, %s)', (nome, qtde, preco, login_user))
            conn.commit()
            flash('Produto cadastrado com sucesso', 'sucess')
    cur.execute('SELECT nome, qtde, preco FROM produto WHERE loginUser = %s', (login_user,))
    produtos = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('cadastrar_produto.html', produtos=produtos)

if __name__ == '__main__':
    app.run(debug=True)  