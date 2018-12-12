# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine, text, func, exc

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False, execution_options={"autocommit":False})

def dbConnect():
    return db_engine.connect()

def dbCloseConnect(db_conn):
    db_conn.close()

def getListaCliMes(db_conn, mes, anio, iumbral, iintervalo, use_prepare, break0, niter):

    # TODO: implementar la query; asignar nombre 'cc' al contador resultante
    orderdate = anio+mes
    if use_prepare:
        query = text("PREPARE getListaCliMes(varchar, integer) as SELECT count(DISTINCT customerid) FROM orders WHERE totalamount > $2 and TO_CHAR(orderdate, 'YYYYMM') = $1;")
        db_conn.execute(query)

    # TODO: ejecutar la query 
    # - mediante PREPARE, EXECUTE, DEALLOCATE si use_prepare es True
    # - mediante db_conn.execute() si es False

    # Array con resultados de la query para cada umbral
    dbr=[]

    for ii in range(niter):

        if use_prepare:
            query = text('EXECUTE getListaCliMes(:o,:t)') 
        else:
            query = text("SELECT count(DISTINCT customerid) FROM orders WHERE totalamount > :t and TO_CHAR(orderdate, 'YYYYMM') = :o;")

        res = list(db_conn.execute(query, o = orderdate, t=iumbral).fetchall())
        # Guardar resultado de la query
        dbr.append({"umbral":iumbral,"contador":res[0][0]})

        # TODO: si break0 es True, salir si contador resultante es cero
        if break0 == True and res[0][0] == 0:
            break
    
        # Actualizacion de umbral
        iumbral = iumbral + iintervalo

    if use_prepare:
        query = text('DEALLOCATE getListaCliMes')
        db_conn.execute(query)
                
    return dbr

def getMovies(anio):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select movietitle from imdb_movies where year = '" + anio + "'"
    resultproxy=db_conn.execute(query)

    a = []
    for rowproxy in resultproxy:
        d={}
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for tup in rowproxy.items():
            # build up the dictionary
            d[tup[0]] = tup[1]
        a.append(d)
        
    resultproxy.close()  
    
    db_conn.close()  
    
    return a
    
def getCustomer(username, password):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select * from customers where username='" + username + "' and password='" + password + "'"
    res=db_conn.execute(query).first()
    
    db_conn.close()  

    if res is None:
        return None
    else:
        return {'firstname': res['firstname'], 'lastname': res['lastname']}
    
def delCustomer(customerid, bFallo, bSQL, duerme, bCommit):
    
    # Array de trazas a mostrar en la página
    dbr=[]

    # TODO: Ejecutar querys de borrado
    # - ordenar querys según se desee provocar un error (bFallo True) o no
    # - ejecutar commit intermedio si bCommit es True
    # - usar sentencias SQL ('BEGIN', 'COMMIT', ...) si bSQL es True
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para forzar deadlock
    # - ir guardando trazas mediante dbr.append()
    
    query1 = text("DELETE FROM orderdetail USING orders WHERE orderdetail.orderid = orders.orderid AND orders.customerid= :c;")
    query2 = text("DELETE FROM orders WHERE customerid= :c;")
    query3 = text("DELETE FROM customers WHERE customerid= :c;")   

    if bSQL == True:
        db_conn = db_engine.connect()
        try:
            db_conn.execute("BEGIN")
            db_conn.execute(query1, c=customerid)
            dbr.append('se ha borrado orderdetail')
            if bCommit == True:
                db_conn.execute("COMMIT")
                dbr.append('se ha commiteado')
                db_conn.execute("BEGIN")
            
            if bFallo == True: 
                db_conn.execute(query3, c=customerid)
                dbr.append('se ha borrado customers')
                db_conn.execute(query2, c=customerid)
                dbr.append('se ha borrado orders')
            else:
                db_conn.execute(query2, c=customerid)
                dbr.append('se ha borrado orders')
                db_conn.execute(query3, c=customerid)
                dbr.append('se ha borrado customers')

            query = text("SELECT * FROM pg_sleep(:d)")
            db_conn.execute(query, d= duerme)
            
            db_conn.execute("COMMIT")
            dbr.append('se ha comiteado todo')
        except exc.IntegrityError:
            db_conn.execute("ROLLBACK;")
            dbr.append('ha habido un error y se ha hecho rollback')
    else:
        connection = dbConnect()
        trans = connection.begin()
        try:
            connection.execute(query1, c=customerid)
            dbr.append('se ha borrado orderdetail')
            if bCommit == True: 
                trans.commit()
                dbr.append('se ha commiteado')
                trans = connection.begin()
                if bFallo == True:
                    connection.execute(query3, c=customerid)
                    dbr.append('se ha borrado customers')
                    connection.execute(query2, c=customerid)
                    dbr.append('se ha borrado orders')
                else:
                    connection.execute(query2, c=customerid)
                    dbr.append('se ha borrado orders')
                    connection.execute(query3, c=customerid)
                    dbr.append('se ha borrado customers')
            trans.commit()
            dbr.append('se ha comiteado todo')
        except exc.IntegrityError:
            trans.rollback()
            dbr.append('ha habido un error y se ha hecho rollback')
        finally:
            dbCloseConnect(trans)

    return dbr

