DETECTION = {

    # Export yang digunakan
    "backend": "sqlite",

    # File
    "csv": {
        "path": "storage/books.csv",
        "delimiter": ",",
        "encoding": "utf-8",
    },

    "json": {
        "path": "storage/books.json",
        "encoding": "utf-8",
        "indent": 4,
    },

    "xml": {
        "path": "storage/books.xml",
        "encoding": "utf-8",
        "root": "books",
        "item": "book",
    },

    # Database
    "sqlite": {
        "database": "storage/books.db",
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
    },

    # Detector
    "duplicate": {
        "enabled": True,
    },

    "incremental": {
        "enabled": True,
    },

    "change_detection": {
        "enabled": True,
    },

    "anomaly": {
        "enabled": False,
    },
}