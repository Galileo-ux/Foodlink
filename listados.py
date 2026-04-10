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
        <link rel="icon" type="image/png" href="/static/Avanzo.PNG">
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
        <div class="accion">
            <a href="/" class="boton-principal">← Volver</a>
        </div>
    </div>
    </body>
    </html>
    """

    return html

@app.route('/estadisticas')
def estadisticas():
    import pandas as pd
    import json
    import matplotlib.pyplot as plt
    import os

    # Cargar datos
    try:
        with open('donaciones.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = []

    if not data:
        return "<h2>No hay datos para analizar</h2><a href='/'>Volver</a>"

    df = pd.DataFrame(data)

    # Limpiar datos
    df['peso'] = pd.to_numeric(df['peso'], errors='coerce')
    df = df.dropna()

    # ----------- ANÁLISIS -----------

    # Conteo de donaciones
    conteo = df['tipo_institucion'].value_counts()

    # Suma de peso
    peso_total = df.groupby('tipo_institucion')['peso'].sum()

    top = conteo.idxmax()
    top_peso = peso_total.idxmax()

    # ----------- GRÁFICAS -----------

    # Crear carpeta si no existe
    if not os.path.exists('static'):
        os.makedirs('static')

    # Gráfica 1: número de donaciones
    plt.figure()
    conteo.plot(kind='bar')
    plt.title('Cantidad de Donaciones por Institución')
    plt.xlabel('Institución')
    plt.ylabel('Cantidad')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/grafica_conteo.png')
    plt.close()

    # Gráfica 2: peso total
    plt.figure()
    peso_total.plot(kind='bar')
    plt.title('Peso Total Donado por Institución')
    plt.xlabel('Institución')
    plt.ylabel('Peso (kg)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/grafica_peso.png')
    plt.close()

    # ----------- HTML -----------

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Estadísticas</title>
        <link rel="icon" type="image/png" href="/static/Avanzo.PNG">
        <link rel="stylesheet" href="/static/style.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    
    </head>
    <body>

    <div class="contenedor">

        <header class="cabecera animar-bajar">
            <h1><i class="fa-solid fa-chart-line"></i> Estadísticas</h1>
            <p class="subtitulo">Análisis de donaciones registradas</p>
        </header>

        <div class="tarjeta-grid">

            <div class="tarjeta animar-subir delay-1">
                <h2><i class="fa-solid fa-trophy"></i> Más donaciones</h2>
                <p>La institución que más dona es:</p>
                <p class="impacto">{top}</p>
            </div>

            <div class="tarjeta animar-subir delay-2">
                <h2><i class="fa-solid fa-scale-balanced"></i> Mayor peso donado</h2>
                <p>La institución que más aporta en peso es:</p>
                <p class="impacto">{top_peso}</p>
            </div>

        </div>

        <div class="tarjeta animar-subir delay-3">
            <h2><i class="fa-solid fa-chart-column"></i> Cantidad de donaciones</h2>
            <img src="/static/grafica_conteo.png" class="grafica">
        </div>

        <div class="tarjeta animar-subir delay-4">
            <h2><i class="fa-solid fa-box"></i> Peso total donado</h2>
            <img src="/static/grafica_peso.png" class="grafica">
        </div>
        <br><br>
        <div class="accion">
            <a href="/" class="boton-principal">← Volver</a>
        </div>

    </div>

    </body>
    </html>
    """
@app.route('/prediccion')
def prediccion():
    import json

    try:
        with open('donaciones.json', 'r', encoding='utf-8') as f:
            donaciones = json.load(f)
    except:
        donaciones = []

    if not donaciones:
        return "<h2>No hay datos suficientes</h2>"

    pesos = [float(d['peso']) for d in donaciones]

    promedio = sum(pesos) / len(pesos)

    prediccion = promedio * 5  # ejemplo: próximas 5 donaciones

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Predicción</title>
        <link rel="icon" type="image/png" href="/static/Avanzo.PNG">
        <link rel="stylesheet" href="/static/style.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    </head>
    <body>
    <div class="contenedor">

        <header class="cabecera">
            <h1><i class="fa-solid fa-eye"></i> Predicción básica</h1>
        </header>

        <div class="categoria">
            <h2> <i class="fa-solid fa-chart-pie"></i> Resultados</h2>
            <p><b>Promedio por donación:</b> {promedio:.2f} kg</p>
            <p><b>Estimación próximas 5 donaciones:</b> {prediccion:.2f} kg</p>
        </div>

        <div class="accion">
            <a href="/" class="boton-principal">← Volver</a>
        </div>

    </div>
    </body>
    </html>
    """
@app.route('/prediccion_ml')
def prediccion_ml():
    import json
    import numpy as np
    from sklearn.linear_model import LinearRegression

    try:
        with open('donaciones.json', 'r', encoding='utf-8') as f:
            donaciones = json.load(f)
    except:
        donaciones = []

    if len(donaciones) < 2:
        return "<h2>No hay suficientes datos para ML</h2>"

    # X = número de donación
    X = np.array(range(len(donaciones))).reshape(-1, 1)

    # Y = peso
    y = np.array([float(d['peso']) for d in donaciones])

    modelo = LinearRegression()
    modelo.fit(X, y)

    # Predecir siguiente donación
    siguiente = modelo.predict([[len(donaciones)]])
    
    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Predicción ML</title>
        <link rel="icon" type="image/png" href="/static/Avanzo.PNG">
        <link rel="stylesheet" href="/static/style.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    </head>
    <body>
    <div class="contenedor">

        <header class="cabecera">
            <h1><i class="fa-solid fa-chart-line"></i> Predicción con ML</h1>
        </header>

        <div class="categoria">
            <h2><i class="fa-solid fa-brain"></i> Resultado</h2>
            <p><b>Siguiente donación estimada:</b> {siguiente[0]:.2f} kg</p>
        </div>

        <div class="accion">
            <a href="/" class="boton-principal">← Volver</a>
        </div>

    </div>
    </body>
    </html>
    """
if __name__ == '__main__':
    app.run(debug=True)