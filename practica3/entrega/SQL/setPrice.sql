--Sabiendo que los precios de las películas se han ido incrementando un 2% anualmente,
--elaborar la consulta setPrice.sql que complete la columna 'price' de la tabla 'orderdetail',
--sabiendo que el precio actual es el de la tabla 'products'


UPDATE orderdetail
SET price = (SELECT products.price * (pow(0.98, (SELECT date_part('year', current_date)) - 
												(SELECT date_part('year', orderdate)
												 FROM orders
												 WHERE orders.orderid = orderdetail.orderid))) 
			 FROM products, orders
			 WHERE products.prod_id = orderdetail.prod_id
			 AND orders.orderid = orderdetail.orderid);