from flask import Flask, request, redirect, render_template
import json
import uuid

app = Flask(__name__)

# ----------- RUTAS HTML -----------

@app.route('/')
def inicio():
    return render_template('index.html')  #directo


@app.route('/formulario.html')
def formulario():
    return render_template('formulario.html')


# ----------- GUARDAR DONACIÓN -----------

@app.route('/donar', methods=['POST'])
def donar():
    datos = {
        'id': str(uuid.uuid4()),  # ID único
        'nombre': request.form['nombre'],
        'direccion': request.form['direccion'],
        'descripcion': request.form['descripcion'],
        'tipo_institucion': request.form['tipo_institucion'],
        'peso': request.form['peso'],
        'contenedor': request.form['contenedor'],
        'temperatura': request.form['temperatura']
    }

    try:
        with open('donaciones.json', 'r', encoding='utf-8') as f:
            donaciones = json.load(f)
    except:
        donaciones = []

    donaciones.append(datos)

    with open('donaciones.json', 'w', encoding='utf-8') as f:
        json.dump(donaciones, f, indent=4, ensure_ascii=False)

    return redirect('/listado')


# ----------- ELIMINAR -----------

@app.route('/eliminar/<id>')
def eliminar(id):
    try:
        with open('donaciones.json', 'r', encoding='utf-8') as f:
            donaciones = json.load(f)
    except:
        donaciones = []

    donaciones = [d for d in donaciones if d.get('id') != id]

    with open('donaciones.json', 'w', encoding='utf-8') as f:
        json.dump(donaciones, f, indent=4, ensure_ascii=False)

    return redirect('/listado')


# ----------- LISTADO -----------

@app.route('/listado')
def listado():
    try:
        with open('donaciones.json', 'r', encoding='utf-8') as f:
            donaciones = json.load(f)
    except:
        donaciones = []

    categorias = {}
    for d in donaciones:
        cat = d.get('tipo_institucion', 'Otro')
        categorias.setdefault(cat, []).append(d)

    html = """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Listado de Donaciones</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
    <div class="contenedor">
        <header class="cabecera">
            <h1>Donaciones agrupadas por categoría</h1>
        </header>
    """

    if not donaciones:
        html += "<p>No hay donaciones registradas.</p>"
    else:
        for cat, items in categorias.items():
            nombre_cat = cat.replace('_', ' ').title()
            html += f"<div class='categoria'><h2>{nombre_cat}</h2><ul>"

            for item in items:
                html += f"""
                <li>
                <b>{item['nombre']}</b> ({item['direccion']}) - 
                {item['descripcion']} - {item['peso']} kg - 
                Contenedor: {item['contenedor']} - 
                Refrigerado: {item['temperatura']}               
                <a href="/eliminar/{item.get('id','')}" class="btn-eliminar" onclick="return confirm('¿Seguro que quieres eliminar esta donación?')">
                    Eliminar
                </a>
                </li>
                """

            html += "</ul></div>"

    html += """
        <div style="margin-top: 30px; text-align:center;">
            <a href="/" class="enlace-volver">← Volver</a>
        </div>
    </div>
    </body>
    </html>
    """

    return html


if __name__ == '__main__':
    app.run(debug=True)