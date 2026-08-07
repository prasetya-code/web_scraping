import psycopg

class PostgresNoDuplicatesPipeline:

    def __init__(self):
        ## Connection Details
        hostname = 'localhost'
        username = 'postgres'
        password = '******'  # ganti dengan password kamu
        database = 'quotes'

        ## Create/Connect to database
        self.connection = psycopg.connect(
            host=hostname,
            user=username,
            password=password,
            dbname=database
        )

        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()

        ## Create quotes table if none exists
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS quotes(
                id SERIAL PRIMARY KEY,
                content TEXT UNIQUE,
                tags TEXT,
                author VARCHAR(255)
            )
        """)
        self.connection.commit()

    def process_item(self, item, spider):
        ## Check to see if text is already in database
        self.cur.execute("SELECT 1 FROM quotes WHERE content = %s", (item['text'],))
        result = self.cur.fetchone()

        if result:
            spider.logger.warning("Item already in database: %s" % item['text'])
        else:
            try:
                self.cur.execute(
                    "INSERT INTO quotes (content, tags, author) VALUES (%s, %s, %s)",
                    (
                        item["text"],
                        str(item["tags"]),
                        item["author"],
                    )
                )
                self.connection.commit()
            except psycopg.Error as e:
                self.connection.rollback()
                spider.logger.error("Error inserting item: %s" % e)

        return item

    def close_spider(self, spider):
        ## Close cursor & connection to database
        self.cur.close()
        self.connection.close()