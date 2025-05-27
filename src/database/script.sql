CREATE DATABASE toniscore;


USE toniscore;

-- Crear la tabla de equipos
CREATE TABLE equipos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    pais VARCHAR(100) NOT NULL,
    codigo VARCHAR(10) NOT NULL,
    logo VARCHAR(255) NOT NULL,
    league_id INT NOT NULL
);

-- Crear la tabla de usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    contrasena VARCHAR(255) NOT NULL, 
    correo VARCHAR(100) NOT NULL UNIQUE
);

-- Crear la tabla intermedia favoritos
CREATE TABLE favoritos (
    id_usuario INT NOT NULL,
    id_equipo INT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_equipo),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id) ON DELETE CASCADE
);