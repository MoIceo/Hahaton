from queries import process_properties
from queries import get_connection


def main():
    connection = get_connection()
    if connection:
        print("Успешное подключение к базе данных!")
        process_properties()

    else:
        print("Не удалось подключиться к базе данных.")

if __name__ == "__main__":
    main()