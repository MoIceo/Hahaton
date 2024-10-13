import pyodbc

class DAL:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None

    def open(self):
        self.connection = pyodbc.connect(self.connection_string)

    def close(self):
        if self.connection:
            self.connection.close()

    def get_products(self, start_index: int, count: int):
        products = []
        self.open()

        query = f"""
        SELECT * FROM [MTR]
        LEFT JOIN [OKPD_2] ON [MTR].[okpd2] = [OKPD_2].[okpd2_code]
        LEFT JOIN [ED_IZM] ON [MTR].[ed_izm] = [ED_IZM].[ei_code]
        ORDER BY [MTR].[scmtr_code]
        OFFSET {start_index} ROWS
        FETCH NEXT {count} ROWS ONLY;
        """

        cursor = self.connection.cursor()
        cursor.execute(query)

        for row in cursor.fetchall():
            product = {
                "scmtr_code": row.scmtr_code,
                "name": row.name,
                "marking": row.marking,
                "regulations": row.regulations,
                "parameters": row.parameters,
                "ed_izm": row.ed_izm,
                "category": row.category,
                "okpd2": row.okpd2,
                "okpd2_name": row.okpd2_name
            }
            products.append(product)

        self.close()
        return products

    def get_parameters(self, product_id: str):
        parameters = []
        self.open()

        query = f"SELECT * FROM [Parameters] WHERE [product_id] = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, product_id)

        for row in cursor.fetchall():
            parameter = {
                "parameter_name": row.name,
                "parameter_value": row.value
            }
            parameters.append(parameter)

        self.close()
        return parameters

    def update_group(self, product_id: str, group: str):
        self.open()

        query = f"UPDATE [MTR] SET category = ? WHERE [scmtr_code] = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, group, product_id)
        self.connection.commit()

        self.close()

    def add_parameters(self, product_id: str, parameters: list):
        if not parameters:
            return

        self.open()

        query = "INSERT INTO Parameters (product_id, name, value) VALUES (?, ?, ?)"
        cursor = self.connection.cursor()

        for item in parameters:
            cursor.execute(query, product_id, item.parameter_name, item.parameter_value)

        self.connection.commit()
        self.close()