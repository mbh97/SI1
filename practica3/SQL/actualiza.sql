
-- Completar foreign keys
ALTER TABLE inventory
ADD FOREIGN KEY (prod_id)
REFERENCES products(prod_id)
ON DELETE CASCADE;

ALTER TABLE products
ADD FOREIGN KEY (movieid)
REFERENCES imbd_movie(movieid)
ON DELETE CASCADE;

ALTER TABLE orders 
ADD FOREIGN KEY (customerid) 
REFERENCES customers(customerid)
ON DELETE CASCADE;

ALTER TABLE orderdetail 
ADD FOREIGN KEY (orderid) 
REFERENCES orders(orderid)
ON DELETE CASCADE;

ALTER TABLE orderdetail 
ADD FOREIGN KEY (prod_id) 
REFERENCES products(prod_id)
ON DELETE CASCADE;

ALTER TABLE imdb_directormovies 
ADD FOREIGN KEY (directorid) 
REFERENCES imdb_directors(directorid)
ON DELETE CASCADE;

ALTER TABLE imdb_directormovies 
ADD FOREIGN KEY (movieid) 
REFERENCES imdb_movies(movieid)
ON DELETE CASCADE;

ALTER TABLE imdb_actormovies 
ADD FOREIGN KEY (actorid) 
REFERENCES imdb_actors(actorid)
ON DELETE CASCADE;

ALTER TABLE imdb_actormovies 
ADD FOREIGN KEY (movieid) 
REFERENCES imdb_movies(movieid)
ON DELETE CASCADE;

-- Integridad imbd_genres imbd_countries imbd_languages
-- Creacion
DROP TABLE IF EXISTS genres CASCADE;
CREATE TABLE imbd_genres(
	genreid serial NOT NULL,
	genre varchar(32), 
	CONSTRAINT genres_pkey PRIMARY KEY (genreid)
);

DROP TABLE IF EXISTS countries CASCADE;
CREATE TABLE imbd_countries(
	countryid serial NOT NULL,
	country varchar(32),
	CONSTRAINT countries_pkey PRIMARY KEY(countryid)
);

DROP TABLE IF EXISTS languages CASCADE;
CREATE TABLE imbd_languages(
	languageid serial NOT NULL,
	language varchar(32),
	CONSTRAINT languages_pkey PRIMARY KEY(languageid)
);

-- Poblar tablas
INSERT INTO imbd_genres(genre)
(SELECT DISTINCT genre
FROM imdb_moviegenres);

INSERT INTO imbd_countries(country)
(SELECT DISTINCT country
FROM imdb_moviecountries);

INSERT INTO imbd_languages(language)
(SELECT DISTINCT language
FROM imdb_movielanguages);

--Modifica relaciones
ALTER TABLE imdb_moviegenres 
ADD COLUMN genreid INTEGER 
CONSTRAINT imdb_moviegenres_genreid_fkey
REFERENCES imbd_genres(genreid)
ON DELETE CASCADE;

ALTER TABLE imdb_moviecountries 
ADD COLUMN countryid INTEGER 
CONSTRAINT imdb_moviecountries_countryid_fkey
REFERENCES imbd_countries(countryid)
ON DELETE CASCADE;

ALTER TABLE imdb_movielanguages 
ADD COLUMN languageid INTEGER 
CONSTRAINT imdb_movielanguages_languageid_fkey
REFERENCES imbd_languages(languageid)
ON DELETE CASCADE;

--Actualiza tablas
UPDATE imdb_moviegenres
SET genreid = imdb_genres.genreid 
FROM imdb_genres 
WHERE imdb_moviegenres.genre = imdb_genres.genre;

ALTER TABLE imdb_moviegenres 
DROP COLUMN genre;

UPDATE imdb_moviecountries
SET countryid = imdb_countries .countryid 
FROM imdb_countries 
WHERE imdb_moviecountries.country = imdb_countries .country;

ALTER TABLE imdb_moviecountries 
DROP COLUMN country;

UPDATE imdb_movielanguages
SET languageid = imdb_languages.languageid 
FROM imdb_languages 
WHERE imdb_movielanguages.language = imdb_languages.language;

ALTER TABLE imdb_movielanguages 
DROP COLUMN language;

-- Not null
ALTER TABLE customers ALTER COLUMN firstname DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN lastname DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN address1 DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN city DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN country DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN region DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN creditcardtype DROP NOT NULL;
ALTER TABLE customers ALTER COLUMN creditcardexpiration DROP NOT NULL;
