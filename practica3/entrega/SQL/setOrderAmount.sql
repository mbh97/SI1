-- netamount: suma de los precios de las películas del pedido
-- totalamount: 'netamount' más impuestos

CREATE OR REPLACE FUNCTION setOrderAmount()
RETURNS void AS $$

DECLARE

BEGIN
	UPDATE orders
	SET netamount = neta
	FROM (SELECT orderid, sum(price*quantity) AS neta
		  FROM orders
		  NATURAL JOIN orderdetail
		  GROUP BY orderid) AS aux
	WHERE orders.orderid = aux.orderid;

	UPDATE orders
	SET totalamount = total 
	FROM (SELECT orderid, netamount*(100+tax)/100 AS total
		  FROM orders 
		  NATURAL JOIN orderdetail
		  GROUP BY orderid) AS aux
	WHERE orders.orderid = aux.orderid;
END;

$$ language plpgsql;

SELECT setOrderAmount();
