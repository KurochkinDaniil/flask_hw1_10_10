create TABLE if not exists mainmenu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title text not null,
    url text not null
);

create table if not exists post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title text not null unique,
    description text not null,
    updated_at integer not null
);

create table if not exists user_ (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email text not null unique,
    password text not null,
    registered_at integer not null
)
