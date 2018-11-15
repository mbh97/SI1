from flask import Flask, render_template, request ,redirect, session, flash, url_for, jsonify, make_response
import json
import hashlib
import md5
import os
from random import randint
import random
import string
import time
import database as db

app = Flask(__name__)
app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)for _ in range(20))
catalogo = json.loads(open(os.path.join(app.root_path,'catalogo.json')).read(), strict=False)

@app.route('/')
def index():
	content_dict = {}

	if session.get('logged_in') == None:
		session['logged_in'] = False
		db.iniciarCarrito()
	
	#borrar en el futuro
	if session.get("carrito") == None:
		session['carrito'] = []
	if session.get("precio") == None:
		session['precio'] = 0

	content_dict['peliculas'] = db.getNovedades()
	content_dict['categoriaActual'] = 'Ultimas novedades'
	content_dict['categorias'] = db.getCategorias()
	return render_template('index.html', content = content_dict)

@app.route('/categorias/<categoria>')
def mostrar_categoria(categoria):
	content_dict = {}
	content_dict['categoriaActual'] = categoria
	content_dict['peliculas'] = db.getCategoria(categoria)
	content_dict['categorias'] = db.getCategorias()
	return render_template('index.html', content = content_dict)

@app.route('/peliculas/<prod_id>')
def pelicula(prod_id):
	content={}
	content['pelicula']= db.getInfo(prod_id)
	content['categorias'] = db.getCategorias()
	return render_template('pelicula.html', content=content)

@app.route('/search' ,methods=['POST'])
def buscar():
	titulo = request.form['titulo']
	if 'FiltrarPorGenero' not in request.form:
		if titulo == "":
			return index()
		pelis = db.getPelis(titulo)
		if pelis == []:
			return render_template('pelicula.html', content = pelis)
		if len(pelis) == 1:
			return pelicula(pelis[0])

		content_dict ={}
		content_dict['peliculas'] = pelis
		content_dict['categoriaActual'] = titulo
		content_dict['categorias'] = db.getCategorias()
		return render_template('index.html', content=content_dict)

	genero = request.form['FiltrarPorGenero']
	if titulo == "":
		return mostrar_categoria(genero)
	
	pelis = db.pertenece(titulo, genero)
	if pelis == []:
		return render_template('pelicula.html', content = pelis)
	if len(pelis) == 1:
			return pelicula(pelis[0])
	content_dict ={}
	content_dict['peliculas'] = pelis
	content_dict['categoriaActual'] = titulo
	content_dict['categorias'] = db.getCategorias()
	return render_template('index.html', content=content_dict)

@app.route('/micuenta')
def micuenta():
	if session.get('logged_in') == False:
		email = getCookie()
		return render_template('sesion.html', content = email)
	# USUARIO LOGEADO ==> HISTORIAL
	customerid = session['customerid']
	datos = db.getDatosUsuario(customerid)

	usuario_dict = {}
	usuario_dict['nombre'] = datos['firstname']
	usuario_dict['email'] = datos['email']
	usuario_dict['saldo'] = datos['income']
	historial = db.getHistorialUsuario(customerid)
	return render_template('micuenta.html', usuario = usuario_dict, historial = historial)

@app.route('/top_ventas')
def top():
	content_dict = {}
	content_dict['categoriaActual'] = 'TOP VENTAS'
	content_dict['peliculas'] = db.getTopVentas()
	content_dict['categorias'] = db.getCategorias()
	return render_template('index.html', content = content_dict)

@app.route('/registro')
def registro():
	content_dict = {}
	return render_template('registro.html', content = content_dict)

def get_datos_usuario(usuario):
	try:
		f = open(os.path.join(app.root_path,"usuarios/" + str(usuario) + "/" + "datos.dat"), 'r')
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
	password = request.form['password']
	r = db.login(email, password)
	if(r == email):
		customerid = db.getID(email)
		session['logged_in'] = True
		session['customerid'] = customerid
		session.modified = True
	return jsonify(result=r)


@app.route('/registro_usuario',methods=['POST'])
def signUp():
	content_dict = {}
	email = request.form['email']
	nombre = request.form['nombre']
	contrasenna1 = request.form['contrasenna1']
	tarjeta = request.form['tarjeta']
	r = db.crearUsuario(email, nombre, contrasenna1, tarjeta)
	if r != "ERROR_EMAIL":
		session['logged_in'] = True
		session['customerid'] = r #id
		return jsonify(result=email)

	return jsonify(result=r)

@app.route('/cerrar_sesion')
def signOut():
	session['logged_in'] = None
	#hay que eliminar carrito
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
	orderid = db.getIDCarrito()
	carrito = db.getOrderdetails(orderid)
	categorias = db.getCategorias()
	return render_template('carrito.html', carrito = carrito['orderdetail'], precio = carrito['precio'], categorias= categorias)

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
	prod_id = id
	orderid = db.getIDCarrito()
	if db.inCarrito(id, orderid) == False: #la peli no esta en el carrito
		db.insertOrderdetail(orderid, prod_id, n)
	else: #modificar cantidad de dicha peli
		db.updateOrderdetail(orderid, prod_id, n)
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

	path = os.path.join(app.root_path,"usuarios/"+str(usuario))

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

	with open(os.path.join(app.root_path,'catalogo.json'), 'w') as file:
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
	app.run(debug = True)
