create database if not exists redCross;
use redCross;

create table office (
    id int auto_increment,
    name varchar(100) not null,
    primary key (id)
);

create table item (
    id int auto_increment,
    name varchar(100) not null,
    specification varchar(50),
    unit varchar(10),
    primary key (id)
);

create table donation (
    office_id int,
    item_id int,
    donate bool not null, # 0为接收，1为捐赠
    amount int not null,
    time varchar(20) not null,
    foreign key (office_id) references office (id),
    foreign key (item_id) references item (id)
);
