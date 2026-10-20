-- Usuario de solo lectura para mostrar la información en la calificación (DBeaver).
-- instalar.sh lo ejecuta con: psql -v clave="'...'" -v bd=quetzalmart -f rol_consulta.sql
SELECT 'CREATE ROLE consulta LOGIN'
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'consulta')
\gexec
ALTER ROLE consulta WITH LOGIN PASSWORD :clave;
GRANT CONNECT ON DATABASE :"bd" TO consulta;
GRANT USAGE ON SCHEMA public TO consulta;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO consulta;
-- Las tablas que Odoo cree después (nuevos módulos) también serán legibles.
ALTER DEFAULT PRIVILEGES FOR ROLE odoo IN SCHEMA public GRANT SELECT ON TABLES TO consulta;
