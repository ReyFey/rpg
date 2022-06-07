import mysql.connector


class Database:
    def __init__(self, host, port, user, password, name):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.name = name
        self.connector = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=name
        )
        self.cursor = self.connector.cursor()
        self.tables = self.tables()

    def tables(self):
        self.cursor.execute("SHOW TABLES;")
        return self.cursor.fetchall()

    def select(self, table, properties):
        sql = f"SELECT {properties[0]}"
        for index in range(1, len(properties)):
            sql += f", {properties[index]}"
        sql += f" FROM {self.name}.{table};"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def select_by(self, table, properties, conditions, values):
        sql = f"SELECT {properties[0]}"
        for index in range(1, len(properties)):
            sql += f", {properties[index]}"
        sql += f" FROM {self.name}.{table} WHERE {conditions};"
        self.cursor.execute(sql, values)
        return self.cursor.fetchall()

    def sql_insert(self, table, properties, nb_values):
        sql = f"INSERT INTO {self.name}.{table} ({properties[0]}"
        for index in range(1, len(properties)):
            sql += f", {properties[index]}"
        sql += f") VALUES (%s"
        for index in range(1, nb_values):
            sql += ", %s"
        sql += ");"
        return sql

    def insert_one(self, table, properties, values):
        self.cursor.execute(self.sql_insert(table, properties, len(values)), values)
        self.connector.commit()

    def insert_many(self, table, properties, values):
        self.cursor.executemany(self.sql_insert(table, properties, len(values)), values)
        self.connector.commit()

    def update_one(self, table, properties, conditions, values):
        sql = f"UPDATE {self.name}.{table} SET {properties[0]} = %s"
        for index in range(1, len(properties)):
            sql += f", {properties[1]} = %s"
        sql += f" WHERE {conditions};"
        self.cursor.execute(sql, values)
        self.connector.commit()

    def update_many(self, table, properties, conditions, values):
        sql = f"UPDATE {self.name}.{table} SET {properties[0]} = %s"
        for index in range(1, len(properties)):
            sql += f", {properties[1]} = %s"
        sql += f" WHERE {conditions};"
        self.cursor.executemany(sql, values)
        self.connector.commit()

    def delete_by(self, table, conditions, values):
        self.cursor.execute(f"DELETE FROM {self.name}.{table} WHERE {conditions};", values)
        self.connector.commit()

    def delete_many_by(self, table, conditions, values):
        self.cursor.executemany(f"DELETE FROM {self.name}.{table} WHERE {conditions};", values)
        self.connector.commit()

    def clear_table(self, table):
        self.cursor.execute(f"TRUNCATE TABLE {self.name}.{table};")
        self.connector.commit()

    def clear_all(self):
        self.cursor.execute("ALTER TABLE rpg.personnage DROP CONSTRAINT IF EXISTS personnage_player_id_fk;")
        self.cursor.execute("ALTER TABLE rpg.personnage DROP CONSTRAINT IF EXISTS personnage_role_id_fk;")
        for result in self.tables:
            for table in result:
                self.cursor.execute(f"TRUNCATE TABLE {table};")
        self.cursor.execute("ALTER TABLE rpg.personnage "
                            "ADD CONSTRAINT personnage_player_id_fk "
                            "FOREIGN KEY (player_id) "
                            "REFERENCES player (id);")
        self.cursor.execute("ALTER TABLE rpg.personnage "
                            "ADD CONSTRAINT personnage_role_id_fk "
                            "FOREIGN KEY (role_id) "
                            "REFERENCES role (id);")
        self.connector.commit()
