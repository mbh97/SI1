from flask import Flask, render_template, request ,redirect, session, flash, url_for, jsonify, make_response
import json
import hashlib
import md5
import os
from random import randint
import time

app = Flask(__name__)
app.secret_key = 'wquify832932403257'
catalogo = json.loads(open(os.path.join(app.root_path,'catalogo.json')).read(), strict=False)

@app.route('/')
def index():
	content_dict = {}
	if session.get("carrito") == None: 
		session['carrito'] = []
	if session.get("precio") == None: 
		session['precio'] = 0

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
	usuario = session['username']
	datos = get_datos_usuario(usuario)

	usuario_dict = {}
	usuario_dict['nombre'] = datos['nombre']
	usuario_dict['email'] = datos['email']
	usuario_dict['historial'] = {}

	path = str(os.getcwd())+"/usuarios/"+str(usuario)
	historial_dict = json.loads(open(path + '/historial.json').read(), strict=False)
	return render_template('micuenta.html', usuario = usuario_dict, historial = historial_dict['historial'])

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
			datos["saldo"] = eval(linea[2])
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

	datos = {
	    "historial": []
	}
	with open(path+"/historial.json", 'w') as file:
		json.dump(datos, file)

	session['logged_in'] = True
	session['username'] = usuario
	return jsonify(result=email)

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

@app.route('/carrito')
def carrito():
	return render_template('carrito.html', carrito = session['carrito'], precio = session['precio'])

def buscar_peli_id(id):
	for pelicula in catalogo['peliculas']:
		if pelicula['id'] == id:
			return pelicula

def calcular_precio():
	precio = 0
	for dic in session['carrito']:
		precio += dic['n']*dic['peli']['precio']

	return precio

@app.route('/add_carrito/<id>/<n>',methods=['GET','POST'])
def add_carrito(id, n):
	peli = buscar_peli_id(id)

	#si la peli esta ya en el carrito, aumentamos el numero de pelis
	for dic in session['carrito']:
		if dic['peli'] == peli:
			dic['n'] += eval(n)
			session['precio'] = calcular_precio()
			return jsonify()

	# peli no incluida en carrito
	dic = {}
	dic['peli'] = peli
	dic['n'] = eval(n)
	session['carrito'].append(dic)
	session['precio'] = calcular_precio()
	return jsonify()

@app.route('/comprar',methods=['GET','POST'])
def comprar():
	if session['precio'] == 0:
		return jsonify(result="NOT_CARRITO")

	if not session.get('logged_in'):
		return jsonify(result="NOT_SESSION")

	#comprobar que tenga dinero suficiente en su cuenta
	usuario = session['username']
	usuario_info = get_datos_usuario(usuario)
	if session['precio'] > usuario_info['saldo']:
		return jsonify(result="NOT_MONEY")

	path = str(os.getcwd())+"/usuarios/"+str(usuario)

	#restar dinero usuario
	f=open(path+"/datos.dat","w")
	f.write("nombre = "+ usuario_info['nombre'] +"\n")
	f.write("password = "+ usuario_info['password'] +"\n")
	f.write("email = "+ usuario_info['email'] +"\n")
	f.write("tarjeta = "+ usuario_info['tarjeta'] +"\n")
	new_saldo = usuario_info['saldo'] - session['precio']
	f.write("saldo = "+ str(new_saldo) +"\n")
	f.close()

	#aumentar ventas de las peliculas (para el futuro)
	for dic in session['carrito']:
		for peli in catalogo['peliculas']:
			if peli == dic['peli']:
				peli['ventas'] += dic['n']

	with open("catalogo.json", 'w') as file:
		json.dump(catalogo, file)

	#escribir historial
	historial = json.loads(open(path+"/historial.json").read(), strict=False)
	lastid = 0
	if historial['historial'] != []:
		lastid = historial['historial'][-1]['id']

	datos = {}
	datos['id'] = lastid +1
	datos['fecha'] = time.strftime("%d/%m/%y")
	datos['precio'] = session['precio']
	datos['pelis'] = []
	for dic in session['carrito']:
		datos['pelis'].append([dic['peli'], dic['n']])

	historial['historial'].append(datos)

	with open(path+"/historial.json", 'w') as file:
		json.dump(historial, file)

	session['carrito'] = []
	session['precio'] = 0

	return jsonify(result="OK")

@app.route('/borrar/<id>', methods=['GET','POST'])
def borrar(id):
	i = 0
	for dic in session['carrito']:
		if dic['peli']['id'] == id:
			session['precio'] -= dic['peli']['precio']*dic['n']
			session['carrito'].pop(i)
			return jsonify(result="OK", precio = session['precio'])
		i += 1

@app.route('/actualizar_banner', methods=['GET','POST'])
def actualizar_banner():
	conectados = randint(15,100)
	return jsonify(result="OK", conectados = conectados)

@app.route('/privacidad')
def privacidad():
	return render_template('privacidad.html')

if __name__ == '__main__':
	app.secret_key = os.urandom(12)
	app.run(debug = True)
