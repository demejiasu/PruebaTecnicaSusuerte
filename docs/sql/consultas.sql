-- ============================================================
-- Parte 2.1 - Creacion de tablas con claves foraneas e indices
-- ============================================================

-- Tabla: usuarios
CREATE TABLE usuarios (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(255) NOT NULL,
    saldo DECIMAL(10, 2) NOT NULL DEFAULT 0,
    creado_en DATETIME NOT NULL
);

CREATE INDEX idx_usuario_nombre ON usuarios (nombre);

-- Tabla: tiquetes
CREATE TABLE tiquetes (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    usuario_id BIGINT NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(10) NOT NULL DEFAULT 'pendiente',
    creado_en DATETIME NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE INDEX idx_tiquete_usuario_id ON tiquetes (usuario_id);
CREATE INDEX idx_tiquete_usuario_estado ON tiquetes (usuario_id, estado);
CREATE INDEX idx_tiquete_creado_en ON tiquetes (creado_en);


-- ============================================================
-- Parte 2.2 - Top 3 usuarios con mayor monto apostado en
--            tiquetes ganadores (nombre y total)
-- ============================================================

SELECT
    u.nombre,
    SUM(t.monto) AS total_apostado
FROM usuarios u
INNER JOIN tiquetes t ON t.usuario_id = u.id
WHERE t.estado = 'ganador'
GROUP BY u.id, u.nombre
ORDER BY total_apostado DESC
LIMIT 3;


-- ============================================================
-- Parte 2.3 - Usuarios sin ningun tiquete registrado
-- ============================================================

SELECT u.id, u.nombre, u.saldo, u.creado_en
FROM usuarios u
LEFT JOIN tiquetes t ON t.usuario_id = u.id
WHERE t.id IS NULL;

-- Alternativa usando NOT EXISTS:
SELECT u.id, u.nombre, u.saldo, u.creado_en
FROM usuarios u
WHERE NOT EXISTS (
    SELECT 1 FROM tiquetes t WHERE t.usuario_id = u.id
);


-- ============================================================
-- Parte 2.4 - Explicacion del uso de transacciones al registrar
--            un tiquete que descuenta saldo del usuario
-- ============================================================

-- Cuando se registra un tiquete, ocurren dos operaciones en la
-- base de datos:
--   1. Insertar el tiquete en la tabla tiquetes.
--   2. Actualizar (descontar) el saldo del usuario en la tabla
--      usuarios.
--
-- Si no se usa una transaccion, puede ocurrir que el INSERT del
-- tiquete se ejecute pero la actualizacion del saldo falle (por
-- un error del servidor, un corte de energia, etc.). Esto
-- dejaria al usuario con un tiquete registrado pero sin el
-- descuento correspondiente, lo que es una inconsistencia grave.
--
-- Usando una transaccion (BEGIN/COMMIT), ambas operaciones se
-- ejecutan como una sola unidad atomica. Si algo falla, se
-- ejecuta ROLLBACK y la base de datos vuelve al estado anterior,
-- como si nada hubiera pasado.
--
-- Ejemplo de transaccion manual en SQL:

BEGIN;

-- 1. Insertar el tiquete
INSERT INTO tiquetes (usuario_id, monto, estado, creado_en)
VALUES (1, 100.00, 'pendiente', datetime('now'));

-- 2. Descontar el saldo del usuario
UPDATE usuarios
SET saldo = saldo - 100.00
WHERE id = 1;

-- Verificar que el saldo no quede negativo
-- (la validacion se hace en la aplicacion antes de la transaccion)

COMMIT;
-- Si ocurre un error, se ejecuta ROLLBACK en lugar de COMMIT.