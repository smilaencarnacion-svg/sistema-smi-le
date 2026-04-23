from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "clave123"

data = []

# LOGIN
@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')
    clave = request.form.get('clave')

    if usuario == "admin" and clave == "123":
        session['user'] = usuario
        return redirect('/panel')
    else:
        return render_template('login.html', error="Credenciales incorrectas")

# PANEL
@app.route('/panel')
def panel():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html', datos=data)

# AGREGAR
@app.route('/agregar', methods=['POST'])
def agregar():
    fila = list(request.form.values())
    data.append(fila)
    return redirect('/panel')

# ELIMINAR
@app.route('/eliminar/<int:index>')
def eliminar(index):
    if 0 <= index < len(data):
        data.pop(index)
    return redirect('/panel')

# IMPORTAR EXCEL
@app.route('/importar', methods=['POST'])
def importar():
    file = request.files['archivo']
    if file:
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            data.append(list(row))
    return redirect('/panel')

if __name__ == '__main__':
    app.run(debug=True)