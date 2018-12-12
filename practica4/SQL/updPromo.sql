-- Nueva columna promo en customers
ALTER TABLE 
  customers 
ADD 
  promo INTEGER;
DROP 
  TRIGGER IF EXISTS updPromo on customers;
-- modifica todos los campos promo a 0
UPDATE 
  customers 
SET 
  promo = 0;
DROP 
  FUNCTION IF EXISTS promo() cascade;
CREATE 
OR REPLACE FUNCTION promo() returns TRIGGER AS $$ DECLARE BEGIN 
UPDATE 
  orders 
SET 
  netamount = netamount *(100 - new.promo)/ 100 
WHERE 
  customerid = new.customerid 
  AND status = NULL;
PERFORM pg_sleep(30);
RETURN null;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER updPromo 
AFTER 
UPDATE 
  OR INSERT ON customers FOR EACH ROW EXECUTE PROCEDURE promo();
--Creacion de carritos (status a NULL) mediante la sentencia UPDATE.
UPDATE 
  orders 
SET 
  status = NULL 
WHERE 
  customerid < 100;
