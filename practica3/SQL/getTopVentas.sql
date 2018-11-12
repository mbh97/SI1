
DROP FUNCTION IF EXISTS getTopVentas(integer);
CREATE OR REPLACE FUNCTION getTopVentas(integer)
RETURNS TABLE(annio integer, titulo CHARACTER VARYING(255), top integer) AS $$

DECLARE
	a alias for $1;

BEGIN
	return query(
		SELECT cast(anno as integer), movietitle, sales
		FROM (SELECT anno, max(sales) as sales
			  FROM (SELECT date_part('year', orderdate) as anno, * FROM orders) as aux1
		      INNER JOIN orderdetail USING(orderid)
			  INNER JOIN inventory USING(prod_id)
			  GROUP BY anno) as aux2
		INNER JOIN (SELECT date_part('year', orderdate) as anno, *
					FROM orders
					INNER JOIN orderdetail USING(orderid)
					INNER JOIN products USING(prod_id)
					INNER JOIN imdb_movies USING(movieid)
					INNER JOIN inventory USING(prod_id)) USING(anno, sales) as aux3
		WHERE cast(date_part('year', orderdate) as integer) >= a
		ORDER BY anno
	);
END;

$$ LANGUAGE plpgsql;

SELECT * FROM getTopVentas(2016);
