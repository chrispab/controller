drop table if exists datalog;
create table datalog (
  id integer primary key autoincrement,
  capture_t datetime not null,
  temp float not null,
  humi float not null
);
