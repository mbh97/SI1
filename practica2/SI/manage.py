from flask import Flask, render_template, request ,redirect
import json
import hashlib
import md5
import os

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

@app.route('/peliculas/<pelicula>')
def pelicula(pelicula):
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

@app.route('/registro')
def registro():
	content_dict = {}
	return render_template('registro.html', content = content_dict)

def get_datos_usuario(usuario):
	try:
		f = open(str(os.getcwd())+"/usuarios/" + str(usuario) + "/" + "datos.dat", "r") #usario no encontrado
 	except IOError:
 		return None

	datos = {}
	while True:
		linea = f.readline().split()
		if not linea:
			break
		if linea[0] == "nombre":
			datos["nombre"] = linea[2]
		if linea[0] == "password":
			datos["password"] = linea[2]
		if linea[0] == "email":
			datos["email"] = linea[2]
		if linea[0] == "tarjeta":
			datos["tarjeta"] = linea[2]
		if linea[0] == "saldo":
			datos["saldo"] = linea[2]
	return datos

@app.route('/inicio_sesion',methods=['POST'])
def signIn():
	content_dict = {}

	#cifrado = request.form['cifrado']
	email = request.form['email']
	usuario = email.split("@")[0]
	password_codificada = request.form['cifrado']
	if not email or not password_codificada: #esto lo podemos comprobar con javascruipt
		return render_template('sesion.html', content = content_dict)

	datos = get_datos_usuario(usuario)
	print datos
	if datos == None:
		return render_template('sesion.html', content = content_dict)

	password = datos['password']

	if(password == password_codificada):
		#cargar datos historial
		return index()

	else: # contrasena incorrecta!!
		return render_template('sesion.html', content = content_dict)


@app.route('/registro_usuario',methods=['POST'])
def signUp():
	content_dict = {}
	email = request.form['email']
	nombre = request.form['nombre']
	contrasenna1 = request.form['contrasenna1']
	tarjeta = request.form['tarjeta']
	usuario = usuario = email.split("@")[0]

	#if(os.path.exists("/usuarios/"+str(usuario))) #esto no funciona

	#os.mkdir(str(os.getcwd())+"/usuarios/"+str(usuario)) esto tampoco



if __name__ == '__main__':
	app.run(debug = True)
