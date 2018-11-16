import os
from sqlalchemy import create_engine, text, func
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select
from random import randint

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
# cargar las tablas desde una base de datos existente
db_meta = MetaData(bind=db_engine, reflect = True)
# conexion a la base de datos
db_conn = db_engine.connect()

def db_listOfMovies1949():
    try:
        # cargar tabla de la metadata
        db_table_movies = db_meta.tables['imdb_movies']
        # seleccionar las peliculas del anno 1949
        db_movies_1949 = select([db_table_movies]).where("year = '1949'")
        db_result = db_conn.execute(db_movies_1949)
        #db_result = db_conn.execute("Select * from imdb_movies where year = '1949'")
        return  list(db_result)
    except:
        return 'Something is broken'

def existeEmail(email):
    query = text('select * from customers where email=:e')
    return list(db_conn.execute(query, e = email).fetchall())

def login(email, password):
    result = existeEmail(email)
    if result == []:
        return "ERROR_EMAIL"
    if password != result[0]['password']:
        return "ERROR_PASSWORD"
    return email

def getID(email):
    query = text('select * from customers where email=:e')
    result = list(db_conn.execute(query, e = email).fetchall())
    return result[0]['customerid']

def getDatosUsuario(id):
    query = text('select * from customers where customerid=:i')
    result = list(db_conn.execute(query, i = id).fetchall())
    return result[0]

def getHistorialUsuario(id):
    query = text('select * from orders where customerid=:i')
    result = list(db_conn.execute(query, i = id).fetchall())
    historial = []
    for r in result:
        dic= {
            'id': r[0], #orderid
            'fecha': r[1], #orderdate
            'precio': r[3], #totalamount
            'status': r[6], #status
            'pelis': getDetalleHistorial(r[0])
        }
        historial.append(dic)

    return historial


def getDetalleHistorial(orderid):
    query = text('select movietitle, quantity, orderdetail.price \
                  from orderdetail inner join products using(prod_id) inner join imdb_movies using(movieid) \
                  where orderid=:o')
    result = list(db_conn.execute(query, o = orderid).fetchall())
    pelis = []
    for r in result:
        dic={
            'titulo':r[0], #movietitle
            'cantidad':r[1], #quantity
            'precio':r[2] #price
        }
        pelis.append(dic)

    return pelis

def crearUsuario(email, nombre, password, tarjeta):
    result = existeEmail(email)
    if(result != []):
        return "ERROR_EMAIL"
    query = text('insert into customers(email,firstname,password,creditcard,income) values(:e, :n, :p, :t, :d)')
    db_conn.execute(query, e = email, n=nombre, p=password, t=tarjeta, d=randint(10,100))
    actualizaIDCustomers()

    return getID(email)

def actualizaIDCustomers():
    query = text("SELECT setval('customers_customerid_seq', (SELECT max(customerid) FROM customers))")
    db_result = db_conn.execute(query).fetchall()

def getNovedades():
    query = text("select prod_id, movietitle, price from imdb_movies inner join products using(movieid) order by year desc limit 20")
    result = list(db_conn.execute(query).fetchall())
    pelis = []
    for r in result:
        dic={
            'id':r[0], 
            'titulo':r[1], 
            'precio':r[2] 
        }
        pelis.append(dic)
    return pelis


def getTopVentas():
    query = text('select distinct on (prod_id) prod_id,movietitle,price \
                  from imdb_movies\
                  inner join products using(movieid) \
                  inner join inventory using(prod_id) \
                  order by sales desc limit 20')
    result = list(db_conn.execute(query).fetchall())
    pelis = []
    for r in result:
        dic={
            'id':r[0], 
            'titulo':r[1], 
            'precio':r[2] 
        }
        pelis.append(dic)
    return pelis

def getCategoria(categoria):
    query = text('select prod_id,movietitle,price\
                  from imdb_movies \
                  inner join imdb_moviegenres using(movieid)\
                  inner join imdb_genres using(genreid)\
                  inner join products using(movieid)\
                  where genre = :c')
    result = list(db_conn.execute(query, c=categoria).fetchall())
    pelis = []
    for r in result:
        dic={
            'id':r[0], 
            'titulo':r[1], 
            'precio':r[2] 
        }
        pelis.append(dic)
    return pelis

def getCategorias():
    query = text('select genre from imdb_genres')
    result = list(db_conn.execute(query).fetchall())
    categorias = []
    for r in result:
        categorias.append(r[0])
    return categorias

def getPelis(titulo):
    query = text('select prod_id, price from imdb_movies inner join products using(movieid) where movietitle=:t')
    result = list(db_conn.execute(query, t=titulo).fetchall())
    pelis = []
    for r in result:
        dic={
            'id':r[0], 
            'titulo':titulo, 
            'precio':r[1] 
        }
        pelis.append(dic)
    return pelis

def pertenece(titulo, genero):
    query = text('select prod_id, price \
                  from imdb_movies \
                  inner join products using(movieid) \
                  inner join imdb_moviegenres using(movieid)\
                  inner join imdb_genres using(genreid)\
                  where movietitle=:t and genre=:g')
    result = list(db_conn.execute(query, t=titulo, g=genero).fetchall())
    pelis = []
    for r in result:
        dic={
            'id':r[0], 
            'titulo':titulo, 
            'precio':r[1] 
        }
        pelis.append(dic)
    return pelis

def getInfo(prod_id):
    query = text('select movietitle, imdb_movies.description, price, directorname,year \
                  from imdb_movies \
                  inner join products using(movieid) \
                  inner join imdb_directormovies using(movieid)\
                  inner join imdb_directors using(directorid)\
                  where prod_id=:i')
    print prod_id
    r = list(db_conn.execute(query, i=prod_id).fetchall())[0]
    dic={
        'id':prod_id, 
        'titulo':r[0], 
        'precio':r[2],
        'informacion':r[1],
        'director':r[3],
        'anno':r[4]
    }
    return dic

def iniciarCarrito():
    query = text('insert into orders(orderdate,netamount,tax,totalamount) values(CURRENT_DATE,0,0,0)')
    db_conn.execute(query)
    actualizaIDOrders()



def actualizaIDOrders():
    query = text("SELECT setval('orders_orderid_seq', (SELECT max(orderid) FROM orders))")
    db_result = db_conn.execute(query).fetchall()

def getIDCarrito():
    query = text('SELECT max(orderid) FROM orders')
    return list(db_conn.execute(query))[0][0]

def inCarrito(prod_id, orderid):
    query = text('select * from orderdetail inner join products using(prod_id) where orderid=:o and prod_id=:p')
    result = list(db_conn.execute(query, o=orderid, p=prod_id).fetchall())
    if result ==[]:
        return False
    return True

def insertOrderdetail(orderid, prod_id, n):
    query = text('insert into orderdetail(orderid,prod_id,price,quantity) values(:o,:p,(select price from products where prod_id=:p),:q)')
    db_conn.execute(query, o=orderid, p=prod_id, q=n)


def updateOrderdetail(orderid, prod_id, n):
    query = text('update orderdetail set quantity=quantity+:q where orderid=:o and prod_id=:p')
    db_conn.execute(query, o=orderid, p=prod_id, q=n)

def getOrderdetails(orderid):
    query = text('select prod_id, movietitle, quantity, orderdetail.price from orderdetail inner join products using(prod_id) inner join imdb_movies using(movieid) where orderid=:o')
    result = list(db_conn.execute(query, o=orderid).fetchall())
    orderdetail=[]
    for r in result:
        dic={
            'id': r[0],
            'titulo':r[1],
            'cantidad': r[2],
            'precio': r[3]
        }
        orderdetail.append(dic)
    precio = getTotal(orderid)

    carrito={
        'orderdetail':orderdetail,
        'precio': precio
    }
    return carrito

def deleteOrderdetail(orderid, prod_id):
    query = text('delete from orderdetail where prod_id=:p and orderid=:o')
    db_conn.execute(query, p=prod_id, o=orderid)

def getTotal(orderid):
    query = text('select totalamount from orders where orderid=:o')
    result = db_conn.execute(query, o=orderid).fetchall()
    price = result[0][0]
    return price 

def comprar(orderid, customerid):
    query = text('update orders set status=:s where orderid=:o')
    db_conn.execute(query, o=orderid, s='Paid')
    query = text('select totalamount from orders where orderid=:o')
    total = db_conn.execute(query, o=orderid).fetchall()[0][0]
    query = text('update customers set income = income -:n where customerid=:i')
    db_conn.execute(query, i=customerid, n=total)



