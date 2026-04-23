from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "clave123"

# almacenamiento temporal
data = []

# LOGIN
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    usuario = request.form['usuario']
    clave = request.form['clave']

    if usuario == "SMI-LE" and clave == "SMI-LE26":
        session['user'] = usuario
        return redirect('/panel')
    else:
        return "Credenciales incorrectas"

# PANEL
@app.route('/panel')
def panel():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html', data=data)

# AGREGAR
@app.route('/agregar', methods=['POST'])
def agregar():
    fila = [
        request.form['expediente'],
        request.form['p1'],
        request.form['p2'],
        request.form['a1'],
        request.form['a2'],
        request.form['identidad'],
        request.form['fecha'],
        request.form['sexo'],
        request.form['departamento'],
        request.form['municipio'],
        request.form['aldea']
    ]
    data.append(fila)
    return redirect('/panel')

# ELIMINAR UNO
@app.route('/eliminar/<int:id>')
def eliminar(id):
    if 0 <= id < len(data):
        data.pop(id)
    return redirect('/panel')

# ELIMINAR TODO
@app.route('/eliminar_todo')
def eliminar_todo():
    data.clear()
    return redirect('/panel')

if __name__ == '__main__':
    app.run(debug=True)