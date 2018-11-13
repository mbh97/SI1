

DROP FUNCTION IF EXISTS getTopMonths(integer, integer);
CREATE OR REPLACE FUNCTION getTopMonths(c integer, i integer)
RETURNS TABLE(annio double precision, mes double precision, import integer, cantidad integer) AS $$

DECLARE

BEGIN
	return query(
		SELECT anno, month, cast(importe AS integer) AS importe, cast(quantity AS integer) AS quantity
		FROM (SELECT date_part('year', orderdate) AS anno, date_part('month', orderdate) AS month, SUM(totalamount) AS importe
			FROM orders
			GROUP BY anno, month
			ORDER BY anno, month) AS aux1
		INNER JOIN (SELECT date_part('year', orderdate) AS anno, date_part('month', orderdate) AS month, SUM(quantity) AS quantity
					FROM orderdetail
					NATURAL JOIN orders
					GROUP BY anno, month
					) AS aux2 USING(anno, month)
		WHERE importe >= i OR quantity >= c
	);
END;

$$ LANGUAGE plpgsql;

SELECT * FROM getTopMonths(19000,320000);