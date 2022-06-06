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

    def update(self, table, properties, conditions, values):
        sql = f"UPDATE {self.name}.{table} SET {properties[0]} = %s"
        for index in range(1, len(properties)):
            sql += f", {properties[1]} = %s"
        sql += f" WHERE {conditions};"
        self.cursor.execute(sql, values)
        self.connector.commit()

    def clear_table(self, table):
        self.cursor.execute(f"DELETE FROM {self.name}.{table} WHERE 1")
        self.connector.commit()

    def clear_all(self):
        # TODO : Clear all tables by select
        pass

    def delete_by(self, table, conditions, values):
        self.cursor.execute(f"DELETE FROM {self.name}.{table} WHERE {conditions}", values)
        self.connector.commit()
