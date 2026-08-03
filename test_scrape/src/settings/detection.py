DETECTION = {

    # Export yang digunakan
    "backend": "sqlite",

    # =========================================
    # File Section
    # =========================================
    "csv": {
        "path": "storage/data/books.csv",
        "delimiter": ";",
        "encoding": "utf-8",
    },

    "json": {
        "path": "storage/data/books.json",
        "encoding": "utf-8",
        "indent": 4,
    },

    "xml": {
        "path": "storage/data/books.xml",
        "encoding": "utf-8",
        "root": "books",
        "item": "book",
    },

    # =========================================
    # Database
    # =========================================
    "sqlite": {
        "database": "storage/data/books.db",
        "table": "books",
    },

    "postgres": {
        "host": "localhost",
        "port": 5432,
        "database": "books",
        "user": "postgres",
        "password": "password",
        "table": "books",
    },

    "mysql": {
        "host": "localhost",
        "port": 3306,
        "database": "books",
        "user": "root",
        "password": "",
        "table": "books",
    },

    "mongodb": {
        "uri": "mongodb://localhost:27017",
        "database": "books",
        "collection": "books",
    }
}