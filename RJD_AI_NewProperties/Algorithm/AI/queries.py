import json
import pyodbc
import requests
from Algorithm.config import API_KEY

# Установка соединения с БД (MS SQL Server)
connection_string = (
    r'Driver=ODBC Driver 17 for SQL Server;'
    r'Server=DESKTOP-3PSOM1R\MSSQLSERVERO;'
    r'Database=RJDDB;'
    r'Trusted_Connection=yes;'
)

cnxn = pyodbc.connect(connection_string)


def get_connection():
    return cnxn


def close_connection(connection):
    if connection:
        connection.close()


# Проверка доступности AI
def is_ai_available():
    api_url = "https://api.openai.com/v1/models"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def read_mtr_table(columns=None):
    if columns is None:
        columns = ['CodeSKMTR', 'Name', 'Label', 'Regulations', 'Properties', 'MeasurementBasicUnit', 'OKPD2']

    query = f"SELECT {', '.join(columns)} FROM MTR"
    cursor = get_connection().cursor()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()


def read_mtr_table_and_assign_categories():
    query = """
    WITH Keywords AS (
        SELECT 
            [Key] AS Keyword, 
            CategoryName
        FROM 
            Category
    )
    SELECT
        m.CodeSKMTR,
        m.Name,
        k.CategoryName,
        m.Properties
    FROM 
        MTR m
    LEFT JOIN 
        Keywords k ON m.Name LIKE '%' + k.Keyword + '%'
    ORDER BY 
        m.CodeSKMTR;
    """
    cursor = get_connection().cursor()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()


def send_to_ai_model(products, connection):
    api_url = "https://api.openai.com/v1/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    prompts = []
    for product in products:
        code = product[0]  # CodeSKMTR
        name = product[1]  # Name
        properties = product[3]  # Properties
        prompt = f"Product Code: {code}, Name: {name}, Properties: {properties}. What category does this product belong to, and what parameters should be considered?"
        prompts.append(prompt)

    # Создание тела запроса
    request_body = {
        "model": "text-davinci-003",
        "prompt": "\n\n".join(prompts),
        "max_tokens": 512,
        "temperature": 0.7
    }

    # Отправка POST-запроса к API
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(request_body))
        response.raise_for_status()
        response_data = response.json()
        choices = response_data.get("choices", [])

        # Сохранение категорий и параметров в базу данных
        for i, choice in enumerate(choices):
            if i < len(products):
                product = products[i]
                code_skmtr = product[0]  # CodeSKMTR
                result_text = choice.get("text", "").strip()

                category, parameters = parse_response(result_text)

                insert_category_if_not_exists(category, connection)

                insert_parameters_for_product(code_skmtr, parameters, connection)

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при вызове API: {e}")
        return None


def parse_response(response_text):
    lines = response_text.splitlines()
    category = ""
    parameters = []

    for line in lines:
        if line.startswith("Category:"):
            category = line[len("Category:"):].strip()
        elif line.startswith("Parameters:"):
            parameters = line[len("Parameters:"):].strip().split(', ')

    return category, parameters


def insert_category_if_not_exists(category_name, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Category WHERE CategoryName = ?", (category_name,))
    exists = cursor.fetchone()[0] > 0

    if not exists:
        cursor.execute("INSERT INTO Category (CategoryName) VALUES (?)", (category_name,))
        connection.commit()


def insert_parameters_for_product(code_skmtr, parameters, connection):
    cursor = connection.cursor()

    for param in parameters:
        name, value = param.split(': ')
        cursor.execute("""SELECT COUNT(*) FROM ProductParameters WHERE CodeSKMTR = ? AND ParameterName = ?""",
                       (code_skmtr, name.strip()))
        exists = cursor.fetchone()[0] > 0

        if not exists:
            cursor.execute("""
                INSERT INTO ProductParameters (CodeSKMTR, ParameterName, ParameterValue)
                VALUES (?, ?, ?)
            """, (code_skmtr, name.strip(), value.strip()))

    connection.commit()


def get_measurement_units():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT CodeME, Name, Description FROM ED_IZM")
    units = cursor.fetchall()
    cursor.close()
    return {unit[1]: unit[2] for unit in units}


def process_ai_response(response):
    pass


def process_properties():
    connection = get_connection()

    try:
        products = read_mtr_table_and_assign_categories()
        measurement_units = get_measurement_units()


    finally:
        close_connection(connection)


# Вызов функции
process_properties()
