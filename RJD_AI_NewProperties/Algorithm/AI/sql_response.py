class SqlResponse:
    """
    Результат выполнения SQL-запроса
    """
    def __init__(self, rows):
        self.rows = rows  # Список строк, возвращаемых SQL-запросом

    def get_columns(self):
        """
        Возвращает названия столбцов для строк
        """
        if self.rows:
            return list(self.rows[0].keys())
        return []

    def get_values(self):
        """
        Возвращает значения для всех строк
        """
        return [list(row.values()) for row in self.rows]

    def get_row(self, index):
        """
        Получить конкретную строку по индексу
        """
        return self.rows[index] if 0 <= index < len(self.rows) else None

    def __repr__(self):
        return f"SqlResponse(rows={self.rows})"
