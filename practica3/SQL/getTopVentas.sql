
DROP FUNCTION IF EXISTS getTopVentas(integer);
CREATE OR REPLACE FUNCTION getTopVentas(integer)
RETURNS TABLE(annio text, titulo CHARACTER VARYING(255), top integer) AS $$

DECLARE
	anno alias for $1;

BEGIN
	return query(
		SELECT year, movietitle, sales
		FROM (SELECT year, max(sales) as sales
			  FROM products
			  NATURAL JOIN imdb_movies 
			  NATURAL JOIN inventory
			  GROUP BY year) as aux1
		NATURAL JOIN (SELECT *
					  FROM products
			  		  NATURAL JOIN imdb_movies 
			  		  NATURAL JOIN inventory) as aux2
		WHERE year >= cast(anno as text)
		ORDER BY year
	);
END;

$$ LANGUAGE plpgsql;

SELECT * FROM getTopVentas(1997);



