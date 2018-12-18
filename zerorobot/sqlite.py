"""
This module holds the logic of indexing services using sqlite in memory database
It maps the in memory service object indexed by guid to a table in sqlite on which we
can execute query to fast search
"""

import sqlite3

_create_table_stmt = """
CREATE TABLE IF NOT EXISTS services (
    guid TEXT PRIMARY KEY UNIQUE,
    name TEXT,
    template_uid TEXT,
    template_host TEXT,
    template_account TEXT,
    template_repo TEXT,
    template_name TEXT,
    template_version TEXT
)
"""

_create_index_stmts = [
    "CREATE INDEX IF NOT EXISTS service_name ON services (name)",
    "CREATE INDEX IF NOT EXISTS service_template ON services (template_uid)",
    "CREATE INDEX IF NOT EXISTS service_template_detail ON services (template_host, template_account, template_repo, template_name, template_version)",
]

_add_service_stmt = "INSERT INTO services VALUES (?,?,?,?,?,?,?,?)"
_delete_service_stmt = "DELETE FROM services WHERE guid=?"
_find_services_stmt = "SELECT guid FROM services"


class SqliteIndex:

    def __init__(self):
        conn = sqlite3.connect(":memory:")
        self._cursor = conn.cursor()
        self._create_table()

    def close(self):
        conn = self._cursor.connection
        self._cursor.close()
        conn.close()

    def _create_table(self):
        self._cursor.execute(_create_table_stmt)
        for stmt in _create_index_stmts:
            self._cursor.execute(stmt)

    def add_service(self, service):
        t = (service.guid,
             service.name,
             str(service.template_uid),
             service.template_uid.host,
             service.template_uid.account,
             service.template_uid.repo,
             service.template_uid.name,
             service.template_uid.version)
        self._cursor.execute(_add_service_stmt, t)
        self._cursor.connection.commit()

    def delete_service(self, service):
        t = (service.guid,)
        self._cursor.execute(_delete_service_stmt, t)
        self._cursor.connection.commit()

    def find(self, **kwargs):
        stmt = _find_services_stmt
        t = tuple()
        if kwargs:
            stmt += " WHERE "
            where = []
            t = []
            for col, val in kwargs.items():
                where.append('%s=?' % col)
                t.append(val)
            stmt += ' AND '.join(where)

        self._cursor.execute(stmt, t)
        return [x[0] for x in self._cursor.fetchall()]

