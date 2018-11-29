DROP
  FUNCTION IF EXISTS f_updInventory() cascade;
CREATE
OR REPLACE FUNCTION f_updInventory() RETURNS TRIGGER AS $$ DECLARE temporal record;
BEGIN IF(new.status = 'Paid') THEN FOR temporal IN
SELECT
  inventory.prod_id,
  inventory.stock,
  inventory.sales,
  orderdetail.quantity
FROM
  orderdetail,
  inventory
WHERE
  new.orderid = orderid
  and inventory.prod_id = orderdetail.prod_id LOOP
UPDATE
  inventory
SET
  sales = sales + temporal.quantity
WHERE
  temporal.prod_id = inventory.prod_id;
UPDATE
  inventory
SET
  stock = stock - temporal.quantity
WHERE
  temporal.prod_id = inventory.prod_id;
IF(
  (
    temporal.stock - temporal.quantity
  ) = 0
) THEN INSERT INTO alerta(prod_id)
VALUES
  (temporal.prod_id);
END IF;
END LOOP;
END IF;
RETURN NULL;
END;
$$ LANGUAGE plpgsql;
DROP
  TRIGGER IF EXISTS updInventory ON orders;
CREATE TRIGGER updInventory
AFTER
UPDATE
  ON orders FOR EACH ROW EXECUTE PROCEDURE f_updInventory();
