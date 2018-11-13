
DROP FUNCTION IF EXISTS f_updOrders() cascade;
CREATE OR REPLACE FUNCTION f_updOrders() RETURNS TRIGGER AS $$

BEGIN
	IF(TG_OP = 'INSERT') THEN -- INSERTA
		UPDATE orders SET netamount = netamount + new.price*new.quantity WHERE orderid=new.orderid;
		UPDATE orders SET totalamount = netamount * ((100 + tax)/100) WHERE orderid=new.orderid;
		RETURN NULL;
	ELSIF(TG_OP = 'DELETE') THEN
		UPDATE orders SET netamount = netamount - old.price*old.quantity WHERE orderid=old.orderid;
		UPDATE orders SET totalamount = netamount * ((100 + tax)/100) WHERE orderid=old.orderid;
		RETURN NULL;
	ELSIF(TG_OP = 'UPDATE') THEN -- Insertando pelicula ya en el carrito
		UPDATE orders SET netamount = netamount + new.price*new.quantity - old.price*old.quantity  WHERE orderid=old.orderid;
		UPDATE orders SET totalamount = netamount * ((100 + tax)/100) WHERE orderid=old.orderid;
		RETURN NULL;
	END IF;
END; 
$$ LANGUAGE plpgsql; 

DROP TRIGGER IF EXISTS updOrders ON orderdetail;
CREATE TRIGGER updOrders AFTER DELETE OR INSERT OR UPDATE ON orderdetail
FOR EACH ROW EXECUTE PROCEDURE f_updOrders();