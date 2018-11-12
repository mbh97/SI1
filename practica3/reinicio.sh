psql -U alumnodb postgres
drop database si1; 
\q
createdb -U alumnodb si1
gunzip –c dump_v1.2.sql.gz | psql –U alumnodb si1
psql si1 < dump_v1.2.sql
psql si1 < SQL/actualiza.sql
