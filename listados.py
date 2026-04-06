
# Script simple: lee donaciones.json y genera reporte_listados.html agrupando por categoría
import json

donaciones = []
try:
    with open('donaciones.json', 'r', encoding='utf-8') as f:
        donaciones = json.load(f)
except Exception as e:
    print('No se pudo leer donaciones.json:', e)

categorias = {}
for d in donaciones:
    cat = d.get('tipo_institucion', 'Otro')
    if cat not in categorias:
        categorias[cat] = []
    categorias[cat].append(d)

html = '<html><head><meta charset="UTF-8"><title>Reporte</title></head><body>'
html += '<h1>Donaciones agrupadas por categoría</h1>'
if not donaciones:
    html += '<p>No hay donaciones registradas.</p>'
else:
    for cat, items in categorias.items():
        html += f'<h2>{cat}</h2><ul>'
        for item in items:
            html += f'<li><b>{item["nombre"]}</b> ({item["direccion"]}) - {item["descripcion"]} - {item["peso"]} kg - Contenedor: {item["contenedor"]} - Refrigerado: {item["temperatura"]}</li>'
        html += '</ul>'
html += '</body></html>'

with open('reporte_listados.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Reporte generado: reporte_listados.html')
from flask import Flask, request, redirect

app = Flask(__name__)
donaciones = []

@app.route('/donar', methods=['POST'])
def donar():
    datos = {
        'nombre': request.form['nombre'],
        'direccion': request.form['direccion'],
        'descripcion': request.form['descripcion'],
        'tipo_institucion': request.form['tipo_institucion'],
        'peso': request.form['peso'],
        'contenedor': request.form['contenedor'],
        'temperatura': request.form['temperatura']
    }
    donaciones.append(datos)
    return redirect('/listado')

@app.route('/listado')
def listado():
    categorias = {}
    for d in donaciones:
        cat = d['tipo_institucion']
        categorias.setdefault(cat, []).append(d)
    html = "<h1>Donaciones agrupadas por categoría</h1>"
    for cat, items in categorias.items():
        html += f"<h2>{cat}</h2><ul>"
        for item in items:
            html += f"<li><b>{item['nombre']}</b> ({item['direccion']}) - {item['descripcion']} - {item['peso']} kg - Contenedor: {item['contenedor']} - Refrigerado: {item['temperatura']}</li>"
        html += "</ul>"
    html += '<a href="/formulario.html">Volver</a>'
    return html

@app.route('/')
def inicio():
    return redirect('/formulario.html')

if __name__ == '__main__':
    app.run(debug=True)