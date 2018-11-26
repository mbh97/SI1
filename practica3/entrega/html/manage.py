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

@app.route('/')
def index():
	content_dict = {}

	if session.get('logged_in') == None:
		session['logged_in'] = False
		db.iniciarCarrito()

	content_dict['peliculas'] = db.getNovedades()
	content_dict['categoriaActual'] = 'Ultimas novedades'
	content_dict['categorias'] = db.getCategorias()
	content_dict['top'] = db.getTop()
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
	content_dict ={}
	content_dict['categorias'] = db.getCategorias()

	if session.get('logged_in') == False:
		email = getCookie()
		content_dict['email'] = email
		return render_template('sesion.html', content=content_dict)
	# USUARIO LOGEADO ==> HISTORIAL
	customerid = session['customerid']
	datos = db.getDatosUsuario(customerid)

	usuario_dict = {}
	usuario_dict['nombre'] = datos['firstname']
	usuario_dict['email'] = datos['email']
	usuario_dict['saldo'] = datos['income']
	historial = db.getHistorialUsuario(customerid)
	return render_template('micuenta.html', usuario = usuario_dict, historial = historial, content=content_dict)

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
	content_dict['categorias'] = db.getCategorias()
	return render_template('registro.html', content = content_dict)

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
	precio = str(carrito['precio'])
	return render_template('carrito.html', carrito = carrito['orderdetail'], precio = precio[:precio.find(".")+2], categorias= categorias)

def buscar_peli_id(id):
	for pelicula in catalogo['peliculas']:
		if pelicula['id'] == id:
			return pelicula

@app.route('/add_carrito/<id>/<n>',methods=['GET','POST'])
def add_carrito(id, n):
	prod_id = id
	orderid = db.getIDCarrito()
	#comprobar que hay stock suficiente
	stock = db.getStock(prod_id)
	quantityEnCarrito = db.quantityEnCarrito(orderid,prod_id)
	if (stock - int(n) - quantityEnCarrito)<0:
		return jsonify(result=str(stock - quantityEnCarrito))
	
	if db.inCarrito(id, orderid) == False: #la peli no esta en el carrito
		db.insertOrderdetail(orderid, prod_id, n)
	else: #modificar cantidad de dicha peli
		db.updateOrderdetail(orderid, prod_id, n)
	return jsonify(result = "OK")

@app.route('/comprar',methods=['GET','POST'])
def comprar():
	orderid = db.getIDCarrito()
	if db.getTotal(orderid) == 0:
		return jsonify(result="NOT_CARRITO")

	if not session.get('logged_in'):
		return jsonify(result="NOT_SESSION")

	#comprobar que tenga dinero suficiente en su cuenta
	customerid = session['customerid']
	datos = db.getDatosUsuario(customerid)
	if db.getTotal(orderid) > datos['income']:
		return jsonify(result="NOT_MONEY")

	db.comprar(orderid, customerid)
	db.iniciarCarrito()

	return jsonify(result="OK")

@app.route('/borrar/<id>', methods=['GET','POST'])
def borrar(id):
	orderid = db.getIDCarrito()
	db.deleteOrderdetail(orderid, id)
	r = str(db.getTotal(db.getIDCarrito()))
	return jsonify(result="OK", precio = r[:r.find(".")+2])	

@app.route('/actualizar_banner', methods=['GET','POST'])
def actualizar_banner():
	conectados = randint(15,100)
	return jsonify(result="OK", conectados = conectados)

@app.route('/privacidad')
def privacidad():
	return render_template('privacidad.html')

if __name__ == '__main__':
	app.run(debug = True)

