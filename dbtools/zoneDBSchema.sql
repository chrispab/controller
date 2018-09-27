
-- thdata stores data samples
create table thdata (
    id          integer primary key autoincrement not null,
    sample_dt   TEXT key,
    temperature REAL,
    humidity    REAL,
    heaterstate INT,
    ventstate   INT,
    fanstate    INT
);

create table config (
    id           integer primary key  not null,
    tempSPLOn    REAL not null,
    tempSPLOff   REAL not null,
    systemUpTime TEXT not null,
    processUptime TEXT not null,
    systemMessage TEXT not null,
    controllerMessage TEXT not null,
    miscMessage    text not null,
    lightState   integer not null
);
