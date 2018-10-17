from flask import Flask, render_template, request ,redirect, session, flash, url_for, jsonify, make_response
import json
import hashlib
import md5
import os
from random import randint

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

@app.route('/micuenta')
def micuenta():
	if not session.get('logged_in'):
		email = getCookie()
		return render_template('sesion.html', content = email)
	# USUARIO LOGEADO ==> HISTORIAL
	content_dict = {}
	usuario = session['username']
	datos = get_datos_usuario(usuario)
	content_dict['nombre'] = datos['nombre']
	content_dict['email'] = datos['email']
	content_dict['historial'] = {}
	return render_template('micuenta.html', content = content_dict)

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
			info = linea[2:]
			datos["nombre"] = " ".join(str(x) for x in info)
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

	email = request.form['email']
	usuario = email.split("@")[0]
	password = request.form['password']
	password_codificada = hashlib.md5(password.encode()).hexdigest()

	datos = get_datos_usuario(usuario)
	if datos == None:
		return jsonify(result="ERROR_EMAIL")

	password = datos['password']

	if(password == password_codificada):
		session['logged_in'] = True
		session['username'] = usuario
		return jsonify(result=email)

	return jsonify(result="ERROR_PASSWORD")


@app.route('/registro_usuario',methods=['POST'])
def signUp():
	content_dict = {}
	email = request.form['email']
	nombre = request.form['nombre']
	contrasenna1 = request.form['contrasenna1']
	tarjeta = request.form['tarjeta']
	usuario = usuario = email.split("@")[0]
	path = str(os.getcwd())+"/usuarios/"+str(usuario)

	list_user = os.listdir(str(os.getcwd())+"/usuarios")
	if list_user != []:
		if usuario in list_user:
			return jsonify(result="ERROR_EMAIL")
	
	os.mkdir(path)

	f=open(path+"/datos.dat","a")
	f.write("nombre = "+ nombre +"\n")
	contrasenna1 = hashlib.md5(contrasenna1.encode()).hexdigest()
	f.write("password = "+ contrasenna1 +"\n")
	f.write("email = "+ email +"\n")
	f.write("tarjeta = "+ tarjeta +"\n")
	saldo = randint(0,100)
	f.write("saldo = "+ str(saldo) +"\n")
	f.close()

	f=open(path+"/historial.json","a")
	f.close()

	session['logged_in'] = True
	session['username'] = usuario
	return jsonify(result="OK")

@app.route('/cerrar_sesion')
def signOut():
	session['logged_in'] = False
	return redirect(url_for('index'))

@app.route('/set_cookie/<usuario>')
def setCookie(usuario):
	resp = make_response(index())
	resp.set_cookie('userID', usuario)
	return resp

def getCookie():
	email = request.cookies.get('userID')
	return email


if __name__ == '__main__':
	app.secret_key = os.urandom(12)
	app.run(debug = True)
