import os
from sqlalchemy import create_engine, text
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select

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


def login(email, password):
    query = text('select * from customers where email=:e')
    result = list(db_conn.execute(query, e = email).fetchall())
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

# ultimas novedades: select * from imdb_movies order by year desc limit 30;

# top ventas: 
    #select movietitle 
    #from (select movieid, sum(quantity) AS top
    #        from orderdetail 
    #        inner join products using(prod_id)
    #        inner join imdb_movies using(movieid)
    #        group by movieid
    #        order by top desc) as aux
    #inner join imdb_movies using(movieid)
    #limit 20;
    
# mostrarCategoria(category):
#    select movietitle
#    from imdb_movies
#    inner join imdb_moviegenres using(movieid)
#    inner join imdb_genres using(genreid)
#    where genre = category