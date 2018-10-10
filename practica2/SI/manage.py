from flask import Flask, render_template, request ,redirect
import json

app = Flask(__name__)
catalogo = json.loads(open('catalogo.json').read(), strict=False)

@app.route('/')
def index():
	content_dict = {}

	content_dict['peliculas'] = [pelicula for pelicula in catalogo['peliculas'] if pelicula['anno'] == 2018]
	content_dict['categoriaActual'] = 'Ultimas novedades'
	return render_template('index.html', content = content_dict)


def in_categoria(pelicula,categoria):
	return categoria in pelicula['categoria']

@app.route('/categorias/<categoria>')
def mostrar_categoria(categoria):
	content_dict = {}
	content_dict['categoriaActual'] = categoria
	content_dict['peliculas'] = [pelicula for pelicula in catalogo['peliculas'] if in_categoria(pelicula,categoria)]
	return render_template('index.html', content = content_dict)


def encontrar_peli(peliculas, titulo):
	for peli in peliculas:
		if peli['titulo'] == titulo:
			return peli
	return None

@app.route('/<categoria>/<pelicula>')
def pelicula(categoria, pelicula):
	content = encontrar_peli(catalogo['peliculas'], pelicula.replace ("%20", ""))
	return render_template('pelicula.html', content=content)

@app.route('/search' ,methods=['POST'])
def buscar():
	titulo = request.form['titulo']
	if 'FiltrarPorGenero' not in request.form:
		if titulo == "":
			return index()
		peli = encontrar_peli(catalogo['peliculas'],  titulo)
		return render_template('pelicula.html', content=peli)
	genero = request.form['FiltrarPorGenero']
	if titulo == "":
		return mostrar_categoria(genero)
	peli = encontrar_peli(catalogo['peliculas'],  titulo)
	if peli == None:
		return render_template('pelicula.html', content = peli)
	if in_categoria(peli,genero)==False:
		peli = None
		return render_template('pelicula.html', content = peli)
	return render_template('pelicula.html', content = peli)

@app.route('/sesion')
def micuenta():
	content_dict = {}
	return render_template('sesion.html', content = content_dict)

@app.route('/top_ventas')
def top():
	content_dict = {}
	top = sorted(catalogo['peliculas'], key=lambda x: -int(x['ventas']))
	content_dict['categoriaActual'] = 'TOP VENTAS'
	content_dict['peliculas'] = top[:10]
	return render_template('index.html', content = content_dict)

if __name__ == '__main__':
	app.run(debug = True)
