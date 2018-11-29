DROP
  FUNCTION IF EXISTS getTopVentas(integer);
CREATE
OR REPLACE FUNCTION getTopVentas(integer) RETURNS TABLE(
  annio double precision,
  titulo CHARACTER VARYING(255),
  sales integer
) AS $$ DECLARE a alias for $1;
BEGIN return query(
  SELECT
    yy,
    movietitle,
    cast(top AS integer)
  FROM
    (
      SELECT
        DISTINCT ON (yy) yy,
        movieid,
        sum(quantity) AS top
      FROM
        (
          SELECT
            date_part('year', orderdate) AS yy,
            *
          FROM
            orders
        ) AS aux1
        INNER JOIN orderdetail USING(orderid)
        INNER JOIN products USING(prod_id)
      GROUP BY
        yy,
        movieid
      ORDER BY
        yy asc,
        top desc
    ) AS aux2
    INNER JOIN imdb_movies USING(movieid)
  WHERE
    cast(yy AS integer) >= a
  ORDER BY
    yy
);
END;
$$ LANGUAGE plpgsql;
SELECT
  *
FROM
  getTopVentas(1999);
