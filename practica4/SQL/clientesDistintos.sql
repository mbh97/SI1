drop 
  index if exists idx_orderdate;
drop 
  index if exists idx_totalamount;
explain 
SELECT 
  count(DISTINCT customerid) 
FROM 
  orders 
WHERE 
  totalamount > 100 
  and TO_CHAR(orderdate, 'YYYYMM') = '201504';
create index idx_orderdate ON orders (orderdate);
create index idx_totalamount ON orders (totalamount);
explain 
SELECT 
  count(DISTINCT customerid) 
FROM 
  orders 
WHERE 
  totalamount > 100 
  and TO_CHAR(orderdate, 'YYYYMM') = '201504';
