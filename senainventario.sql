drop database if exists invsena;
CREATE database invsena;
use invsena;

CREATE table rol (
    id_rol INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(255),
    fch_registro DATETIME,
    fch_ult_act DATETIME
) engine=InnoDB;

create Table usuario (
    id_usu int not NULL auto_increment PRIMARY KEY,
    cc VARCHAR(20) UNIQUE,
    nombre VARCHAR(255),
    apellido VARCHAR(255),
    correo VARCHAR(255),
    contrasena VARCHAR(255),
    id_rol_fk INT NOT NULL,
    fot_usu VARCHAR(255),
    INDEX (id_rol_fk),
    FOREIGN KEY (id_rol_fk) REFERENCES rol(id_rol) ON DELETE CASCADE ON UPDATE CASCADE
) engine=InnoDB;

CREATE table catalogo (
    id_cat INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre_catalogo VARCHAR(255),
    descripcion TEXT,
    fch_registro DATETIME,
    fch_ult_act DATETIME
) engine=InnoDB;

CREATE table usu_cat (
    id_usu_cat INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_usuario_fk INT NOT NULL,
    INDEX (id_usuario_fk),
    FOREIGN KEY (id_usuario_fk) REFERENCES usuario(id_usu) ON DELETE CASCADE ON UPDATE CASCADE,
    id_cat_fk INT NOT NULL,
    INDEX (id_cat_fk),
    FOREIGN KEY (id_cat_fk) REFERENCES catalogo(id_cat) ON DELETE CASCADE ON UPDATE CASCADE,
    fch_registro DATETIME,
    fch_ult_act DATETIME
) engine=InnoDB;

CREATE table producto (
    id_prod INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(255),
    descripcion TEXT,
    fot_prod VARCHAR(255),
    id_cat_fk INT NOT NULL,
    INDEX (id_cat_fk),
    FOREIGN KEY (id_cat_fk) REFERENCES catalogo(id_cat) ON DELETE CASCADE ON UPDATE CASCADE,
    fch_registro DATETIME,
    fch_ult_act DATETIME
) engine=InnoDB;

CREATE table disponibilidad (
    id_disp INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_prod_fk INT NOT NULL,
    INDEX (id_prod_fk),
    FOREIGN KEY (id_prod_fk) REFERENCES producto(id_prod) ON DELETE CASCADE ON UPDATE CASCADE,
    cantidad INT,
    stock INT,
    descr_dispo TEXT,
    fch_registro DATETIME,
    fch_ult_act DATETIME
) engine=InnoDB;

create Table auditorio (
    id_aud INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre_auditorio VARCHAR(255),
    descripcion TEXT,
    fch_registro DATETIME,
    fch_ult_act DATETIME,
    id_usu_cat_fk INT NOT NULL,
    INDEX (id_usu_cat_fk),
    FOREIGN KEY (id_usu_cat_fk) REFERENCES usu_cat(id_usu_cat) ON DELETE CASCADE ON UPDATE CASCADE
) engine=InnoDB;