from flask import Flask, render_template, request
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

	return null

@app.route('/<categoria>/<pelicula>')
def pelicula(categoria, pelicula):
	content = encontrar_peli(catalogo['peliculas'], pelicula.replace ("%20", ""))
	return render_template('pelicula.html', content=content)

if __name__ == '__main__':
	app.run(debug = True)