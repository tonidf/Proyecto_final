-- Crear la base de datos
CREATE DATABASE bgykwxogdco1xjrwbavt;

-- Usar la base de datos
USE bgykwxogdco1xjrwbavt;

-- Crear la tabla de equipos
CREATE TABLE equipos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    api_id INT UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    pais VARCHAR(100) NOT NULL,
    codigo VARCHAR(10),
    logo VARCHAR(255),
    league_id INT NOT NULL,
    founded INT,
    venue_name VARCHAR(150),
    venue_capacity INT
);

-- Crear la tabla de usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    es_admin ENUM('SI', 'NO') NOT NULL DEFAULT 'NO',
    contrasena VARCHAR(255) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE
);

-- Crear la tabla intermedia favoritos
CREATE TABLE equipos_fav (
    id_usuario INT NOT NULL,
    id_equipo INT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_equipo),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id) ON DELETE CASCADE
);

CREATE TABLE jugadores (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    posicion VARCHAR(50),
    equipo_id INTEGER,
    nombre_lower VARCHAR(100) UNIQUE NOT NULL,
    foto_url VARCHAR(255),
    goles INTEGER DEFAULT 0,
    asistencias INTEGER DEFAULT 0,
    partidos INTEGER DEFAULT 0
);

CREATE TABLE partidos (
    id INTEGER PRIMARY KEY,
    equipo_local_id INTEGER NOT NULL,
    equipo_visitante_id INTEGER NOT NULL,
    fecha DATETIME,
    estadio VARCHAR(100)
);

CREATE TABLE partidos_fav (
    usuario_id INTEGER NOT NULL,
    partido_id INTEGER NOT NULL,
    PRIMARY KEY (usuario_id, partido_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (partido_id) REFERENCES partidos(id) ON DELETE CASCADE
);

CREATE TABLE jugadores_fav (
    usuario_id INTEGER NOT NULL,
    jugador_id INTEGER NOT NULL,
    PRIMARY KEY (usuario_id, jugador_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (jugador_id) REFERENCES jugadores(id) ON DELETE CASCADE
);

CREATE TABLE estadisticas_cache (
    team_id INT NOT NULL,
    league_id INT NOT NULL,
    season INT NOT NULL,
    data JSON NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (team_id, league_id, season)
);

CREATE TABLE rounds_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    league_id INT NOT NULL,
    season INT NOT NULL,
    round_name VARCHAR(100) NOT NULL,
    UNIQUE KEY unique_round (league_id, season, round_name)
);

CREATE TABLE fixtures_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    round_name VARCHAR(50),
    league_id INT,
    season INT,
    data LONGTEXT,
    updated_at DATETIME,
    UNIQUE KEY unique_round (round_name, league_id, season)
);