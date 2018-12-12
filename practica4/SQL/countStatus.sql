Drop 
  index if exists idx_status;
-- ejecucion de consultas sin indices
explain 
select 
  count(*) 
from 
  orders 
where 
  status is null;
explain 
select 
  count(*) 
from 
  orders 
where 
  status = 'Shipped';
CREATE INDEX if not exists idx_status ON orders(status);
-- ejecucion de consultas con indices
explain 
select 
  count(*) 
from 
  orders 
where 
  status is null;
explain 
select 
  count(*) 
from 
  orders 
where 
  status = 'Shipped';
ANALYZE VERBOSE orders;
-- ejecucion de consultas y generacion de estadisticas 
explain 
select 
  count(*) 
from 
  orders 
where 
  status is null;
explain 
select 
  count(*) 
from 
  orders 
where 
  status = 'Shipped';
-- ejecucion de consultas y generacion de estadisticas 
explain 
select 
  count(*) 
from 
  orders 
where 
  status = 'Paid';
explain 
select 
  count(*) 
from 
  orders 
where 
  status = 'Processed';
