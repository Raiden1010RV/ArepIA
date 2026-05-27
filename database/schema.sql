-- Base de datos para gestión de inventarios y ventas de arepas

CREATE TABLE IF NOT EXISTS inventario (
    id SERIAL PRIMARY KEY,
    ingrediente VARCHAR(50) NOT NULL,
    cantidad_actual NUMERIC(10, 2) NOT NULL DEFAULT 0,
    unidad VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    tipo_arepa VARCHAR(50) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS variables_externas (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    clima VARCHAR(50),
    es_festivo BOOLEAN DEFAULT FALSE
);
