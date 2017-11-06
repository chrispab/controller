-- Schema for to-do application examples.

-- thdata stores data samples
create table thdata (
    id          integer primary key autoincrement not null,
    sample_dt   TEXT key,
    temperature REAL,
    humidity REAL,
    heaterstate INT,
    ventstate INT,
    fanstate INT
    name        text primary key,
    description text,
    deadline    date
);

-- Tasks are steps that can be taken to complete a project
create table task (
id INT, tempSPLOn REAL, tempSPLOff REAL, systemUpTime TEXT, processUptime TEXT, systemMessage TEXT, lightState INT
    id           integer primary key autoincrement not null,
    priority     integer default 1,
    details      text,
    status       text,
    deadline     date,
    completed_on date,
    project      text not null references project(name)
);
