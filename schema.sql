create table if not exists users (
	id integer primary key auto_increment,
	first_name text not null,
	last_name text not null,
	created datetime not null,
	number text null
	);

create table if not exists destinations (
	id integer primary key auto_increment,
	user_id integer not null,
	did text null,
	number text null,
	created datetime not null,
	expires datetime null,
	record tinyint null,
	auth_did tinyint null,
	auth_gw tinyint null,
	gateway text null,
	channel text null,
	own text null,
	foreign key(user_id) references users(id)
	);

create table if not exists calls (
	id integer primary key auto_increment,
	user_id integer not null,
	channel text not null,
	date datetime not null,
	source text not null,
	destination text null,
	status text null,
	duration integer null,
	has_recording tinyint null,
	foreign key(user_id) references users(id)
	);
