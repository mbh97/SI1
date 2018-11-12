

DROP FUNCTION IF EXISTS getTopMonths(integer, numeric);
CREATE OR REPLACE FUNCTION getTopMonths(c integer, i numeric)
RETURNS TABLE(annio integer, mes integer, import numeric, cantidad numeric) AS $$

DECLARE

BEGIN
	return query(
		SELECT cast(anno AS integer) AS anno, cast(month AS integer) AS month, importe, quantity
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