drop table if exists exercises;
create table exercises (
  id integer primary key autoincrement,
  name text not null,
  description text not null,
  img text not null
);