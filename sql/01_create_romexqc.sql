/*
============================================================
  ROMEX QC DESKTOP v2.0 — Script único para SQL Server (SSMS)
  Exportadora Romex S.A. · Planta Chincha
============================================================
  Cómo usarlo:
  1. Abre SQL Server Management Studio
  2. Conéctate a tu instancia (normalmente localhost o .\SQLEXPRESS)
  3. Abre este archivo
  4. Presiona F5 (o Ejecutar)
  5. Debe terminar con el mensaje de éxito
============================================================
*/

USE master;
GO

IF DB_ID(N'RomexQC') IS NOT NULL
BEGIN
    ALTER DATABASE RomexQC SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE RomexQC;
    PRINT 'Base RomexQC anterior eliminada.';
END
GO

CREATE DATABASE RomexQC;
GO
PRINT 'Base de datos RomexQC creada.';
GO

USE RomexQC;
GO

CREATE TABLE dbo.Productos (
    Id          INT IDENTITY(1,1) PRIMARY KEY,
    Codigo      VARCHAR(50)   NOT NULL,
    Nombre      NVARCHAR(120) NOT NULL,
    Lote        VARCHAR(30)   NOT NULL,
    Activo      BIT           NOT NULL CONSTRAINT DF_Productos_Activo DEFAULT (1),
    CreadoEn    DATETIME2     NOT NULL CONSTRAINT DF_Productos_Creado DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT UQ_Productos_Codigo UNIQUE (Codigo)
);
PRINT 'Tabla Productos creada.';
GO

CREATE TABLE dbo.ResultadosMicro (
    Id               INT IDENTITY(1,1) PRIMARY KEY,
    ProductoId       INT           NOT NULL,
    Anio             INT           NOT NULL,
    Mes              INT           NOT NULL,
    FechaAnalisis    DATE          NULL,
    RTAMV            INT           NOT NULL CONSTRAINT DF_Micro_RTAMV DEFAULT (0),
    Mohos            INT           NOT NULL CONSTRAINT DF_Micro_Mohos DEFAULT (0),
    Coliformes       INT           NOT NULL CONSTRAINT DF_Micro_Col DEFAULT (0),
    EColi            INT           NOT NULL CONSTRAINT DF_Micro_EC DEFAULT (0),
    Enterobacterias  INT           NOT NULL CONSTRAINT DF_Micro_Ent DEFAULT (0),
    Levaduras        INT           NOT NULL CONSTRAINT DF_Micro_Lev DEFAULT (0),
    SAureus          INT           NOT NULL CONSTRAINT DF_Micro_SA DEFAULT (0),
    Estado           VARCHAR(20)   NOT NULL CONSTRAINT DF_Micro_Estado DEFAULT ('LIBERADO'),
    Analista         NVARCHAR(80)  NULL,
    LiberadoPor      NVARCHAR(80)  NULL,
    Notas            NVARCHAR(500) NULL,
    ActualizadoEn    DATETIME2     NOT NULL CONSTRAINT DF_Micro_Upd DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT FK_Micro_Producto FOREIGN KEY (ProductoId) REFERENCES dbo.Productos(Id),
    CONSTRAINT CK_Micro_Mes CHECK (Mes BETWEEN 1 AND 12),
    CONSTRAINT UQ_Micro_Prod_Anio_Mes UNIQUE (ProductoId, Anio, Mes)
);
PRINT 'Tabla ResultadosMicro creada.';
GO

CREATE TABLE dbo.ResultadosFisico (
    Id            INT IDENTITY(1,1) PRIMARY KEY,
    ProductoId    INT           NOT NULL,
    Anio          INT           NOT NULL,
    Mes           INT           NOT NULL,
    FechaAnalisis DATE          NULL,
    Humedad       DECIMAL(8,2)  NULL,
    PH            DECIMAL(6,2)  NULL,
    Ceniza        DECIMAL(8,2)  NULL,
    Grasa         DECIMAL(8,2)  NULL,
    Fineza        DECIMAL(8,2)  NULL,
    Acidez        DECIMAL(8,2)  NULL,
    Estado        VARCHAR(20)   NOT NULL CONSTRAINT DF_Fisico_Estado DEFAULT ('CONFORME'),
    Analista      NVARCHAR(80)  NULL,
    Notas         NVARCHAR(500) NULL,
    ActualizadoEn DATETIME2     NOT NULL CONSTRAINT DF_Fisico_Upd DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT FK_Fisico_Producto FOREIGN KEY (ProductoId) REFERENCES dbo.Productos(Id),
    CONSTRAINT CK_Fisico_Mes CHECK (Mes BETWEEN 1 AND 12),
    CONSTRAINT UQ_Fisico_Prod_Anio_Mes UNIQUE (ProductoId, Anio, Mes)
);
PRINT 'Tabla ResultadosFisico creada.';
GO

CREATE TABLE dbo.Usuarios (
    Id            INT IDENTITY(1,1) PRIMARY KEY,
    Usuario       VARCHAR(50)   NOT NULL,
    PasswordHash  VARCHAR(100)  NOT NULL,
    Nombre        NVARCHAR(120) NOT NULL,
    Rol           VARCHAR(20)   NOT NULL,
    Activo        BIT           NOT NULL CONSTRAINT DF_Usuarios_Activo DEFAULT (1),
    CreadoEn      DATETIME2     NOT NULL CONSTRAINT DF_Usuarios_Creado DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT UQ_Usuarios_Usuario UNIQUE (Usuario),
    CONSTRAINT CK_Usuarios_Rol CHECK (Rol IN ('ADMIN', 'LECTOR'))
);
PRINT 'Tabla Usuarios creada.';
GO

CREATE TABLE dbo.Auditoria (
    Id            INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioNombre NVARCHAR(120) NULL,
    Accion        VARCHAR(40)   NOT NULL,
    Entidad       VARCHAR(40)   NOT NULL,
    Codigo        VARCHAR(50)   NULL,
    Anio          INT           NULL,
    Mes           INT           NULL,
    Detalle       NVARCHAR(MAX) NULL,
    CreadoEn      DATETIME2     NOT NULL CONSTRAINT DF_Aud_Creado DEFAULT (SYSUTCDATETIME())
);
PRINT 'Tabla Auditoria creada.';
GO

CREATE INDEX IX_Micro_AnioMes ON dbo.ResultadosMicro (Anio, Mes);
CREATE INDEX IX_Fisico_AnioMes ON dbo.ResultadosFisico (Anio, Mes);
CREATE INDEX IX_Auditoria_Creado ON dbo.Auditoria (CreadoEn DESC);
GO

SET IDENTITY_INSERT dbo.Productos ON;
INSERT INTO dbo.Productos (Id, Codigo, Nombre, Lote) VALUES
(1, 'torta_natural',  N'Torta Natural de Cacao',  '44260304'),
(2, 'torta_alcalina', N'Torta Alcalina de Cacao', '13260318'),
(3, 'cocoa_natural',  N'Cocoa Natural',           '11260513'),
(4, 'cocoa_alcalina', N'Cocoa Alcalina',          '07260324'),
(5, 'licor',          N'Licor de Cacao',          '260516'),
(6, 'manteca',        N'Manteca de Cacao',        '19260321');
SET IDENTITY_INSERT dbo.Productos OFF;
PRINT '6 productos insertados.';
GO

INSERT INTO dbo.Usuarios (Usuario, PasswordHash, Nombre, Rol) VALUES
('admin',   'admin123',   N'Administrador',           'ADMIN'),
('rodrigo', 'rodrigo123', N'Rodrigo / Admin',         'ADMIN'),
('nereyda', 'romex2026',  N'Nereyda Huachua Flores', 'ADMIN'),
('lector',  'lector123',  N'Usuario Solo Lectura',   'LECTOR');
PRINT '4 usuarios insertados.';
GO

INSERT INTO dbo.ResultadosMicro
    (ProductoId, Anio, Mes, FechaAnalisis, RTAMV, Mohos, Coliformes, EColi, Enterobacterias, Levaduras, SAureus, Analista, LiberadoPor)
SELECT p.Id, 2026, m.Mes, DATEFROMPARTS(2026, m.Mes, 12),
    CASE p.Codigo
        WHEN 'torta_natural'  THEN 900 + (m.Mes - 5) * 15
        WHEN 'torta_alcalina' THEN 40  + (m.Mes - 5) * 5
        WHEN 'cocoa_natural'  THEN 1400 + (m.Mes - 5) * 20
        WHEN 'cocoa_alcalina' THEN 1100 + (m.Mes - 5) * 20
        WHEN 'licor'          THEN 300 + (m.Mes - 5) * 8
        WHEN 'manteca'        THEN 50  + (m.Mes - 5) * 3
        ELSE 0 END,
    CASE WHEN p.Codigo IN ('torta_natural', 'cocoa_natural') THEN 10 + (m.Mes - 5) ELSE 0 END,
    0, 0, 0, 0, 0, N'ZORKA', N'NEREYDA'
FROM dbo.Productos p
CROSS JOIN (VALUES (5),(6),(7),(8),(9),(10),(11),(12)) AS m(Mes);
PRINT 'Resultados microbiológicos insertados.';
GO

INSERT INTO dbo.ResultadosFisico
    (ProductoId, Anio, Mes, FechaAnalisis, Humedad, PH, Ceniza, Grasa, Fineza, Acidez, Analista)
SELECT p.Id, 2026, m.Mes, DATEFROMPARTS(2026, m.Mes, 12),
    CASE p.Codigo
        WHEN 'torta_natural'  THEN 2.22 + (m.Mes - 5) * 0.01
        WHEN 'torta_alcalina' THEN 3.54 + (m.Mes - 5) * 0.01
        WHEN 'cocoa_natural'  THEN 2.49 + (m.Mes - 5) * 0.01
        WHEN 'cocoa_alcalina' THEN 2.76 + (m.Mes - 5) * 0.01
        WHEN 'licor'          THEN 0.55 + (m.Mes - 5) * 0.01
        WHEN 'manteca'        THEN 0.02 + (m.Mes - 5) * 0.002
        ELSE NULL END,
    CASE WHEN p.Codigo = 'manteca' THEN NULL
         WHEN p.Codigo IN ('torta_alcalina', 'cocoa_alcalina') THEN 6.80 + (m.Mes - 5) * 0.01
         ELSE 5.40 + (m.Mes - 5) * 0.01 END,
    CASE WHEN p.Codigo = 'manteca' THEN NULL
         WHEN p.Codigo = 'torta_alcalina' THEN 11.60
         WHEN p.Codigo = 'cocoa_alcalina' THEN 10.30
         WHEN p.Codigo = 'licor' THEN 3.90
         ELSE 8.30 END,
    CASE WHEN p.Codigo = 'manteca' THEN NULL
         WHEN p.Codigo = 'licor' THEN 48.65 + (m.Mes - 5) * 0.05
         ELSE 11.80 + (m.Mes - 5) * 0.02 END,
    CASE WHEN p.Codigo IN ('cocoa_natural', 'cocoa_alcalina', 'licor') THEN 99.50 - (m.Mes - 5) * 0.01 ELSE NULL END,
    CASE WHEN p.Codigo IN ('licor', 'manteca') THEN 1.70 + (m.Mes - 5) * 0.02 ELSE NULL END,
    N'NEREYDA'
FROM dbo.Productos p
CROSS JOIN (VALUES (5),(6),(7),(8),(9),(10),(11),(12)) AS m(Mes);
PRINT 'Resultados físicoquímicos insertados.';
GO

PRINT '============================================================';
PRINT '  ROMEX QC — Base de datos lista';
PRINT '============================================================';
SELECT 'Productos' AS Tabla, COUNT(*) AS Filas FROM dbo.Productos
UNION ALL SELECT 'ResultadosMicro', COUNT(*) FROM dbo.ResultadosMicro
UNION ALL SELECT 'ResultadosFisico', COUNT(*) FROM dbo.ResultadosFisico
UNION ALL SELECT 'Usuarios', COUNT(*) FROM dbo.Usuarios;
PRINT 'Script completado. Ya puedes abrir la aplicación.';
GO
