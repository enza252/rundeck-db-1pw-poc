# /bin/python3
import psycopg2
from os import getenv
from datetime import datetime
from onepasswordconnectsdk.client import (Client, new_client)
from onepasswordconnectsdk.models import Item, ItemVault, Field, GeneratorRecipe
from psycopg2.sql import SQL, Identifier

# get email of requesting user from rundeck: $RD_JOB_USERNAME (?)
REQUESTING_USER: str = getenv("RD_JOB_USERNAME").replace(".", "")

REQUESTED_DATABASE: str = getenv("RD_OPTION_DATABASE")
REQUESTED_TABLES: str = getenv("RD_OPTION_TABLES")
REQUESTED_PRIVILEGES: str = getenv("RD_OPTION_PRIVILEGES")

OP_CONNECT_TOKEN: str = getenv("OP_CONNECT_TOKEN")
OP_CONNECT_API_SERVER: str = getenv("OP_CONNECT_API_SERVER")

POSTGRES_USER: str = getenv("POSTGRES_USER")
POSTGRES_PASSWORD: str = getenv("POSTGRES_PASSWORD")
POSTGRES_DB: str = getenv("POSTGRES_DB")
POSTGRES_HOST: str = getenv("POSTGRES_HOST")

if REQUESTING_USER is None or REQUESTED_DATABASE is None or REQUESTED_TABLES is None or REQUESTED_PRIVILEGES is None:
    raise Exception("User input values not set")

if OP_CONNECT_TOKEN is None:
    raise Exception("OP_CONNECT_TOKEN not set")

# generate db user username: <username>
# probably needs some sanitization here
user = (REQUESTING_USER + REQUESTED_DATABASE).lower()

# establish database connection

print("Attempting to establish connection with database")
db_client = psycopg2.connect(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}")
print("Database connection established!")

# establish 1pw connection
print("Attempting to establish connection with 1Password Connect")
connect_client: Client = new_client(url=OP_CONNECT_API_SERVER, token=OP_CONNECT_TOKEN)
print("1Password Connect connection established!")

vault_id = connect_client.get_vault_by_title("poc-test").id
credential_title = f"{REQUESTED_DATABASE} {REQUESTED_TABLES} poc {REQUESTING_USER}"

# Check db connection & tables exist

cursor = db_client.cursor()

tables_list = REQUESTED_TABLES.split(",")
for table in tables_list:
    cursor.execute(SQL("SELECT * FROM {}").format(Identifier(table)))

# Would want to check the credential doesn't already exist, or if it's active (not tagged, or something similar)

# generate credential name "<DATABASE> <ENV> <REQUESTED_USER_EMAIL> <DATETIME?>"
date_now = datetime.today().strftime('%Y-%m-%d')
item = Item(
    vault=ItemVault(id=vault_id),
    id=f"{user}_{date_now}",
    title=credential_title,
    category="LOGIN",
    tags=["active"],
    fields=[Field(value=user, purpose="USERNAME"), Field(purpose="PASSWORD", generate=True,
                                                         recipe=GeneratorRecipe(length=16,
                                                                                character_sets=['LETTERS', 'SYMBOLS']))]
)

print("Attempting to create credential in 1Password vault")
created_credential = connect_client.create_item(vault_id, item)
print("Successfully stored credential")

username = ""
password = ""

for field in created_credential.fields:
    if field.purpose == "USERNAME":
        username = field.value
    if field.purpose == "PASSWORD":
        password = field.value

# create user in database

cursor.execute(SQL("CREATE USER {} WITH PASSWORD %s IN ROLE {}").format(Identifier(username), Identifier("dbuser")),
               (password,))

print(f"Created user {username}")

# this is hacky and bit naff and I hate it but here we go, it's a poc.
# this is so anti n+1 etc, but again.. it's a poc.
for table in tables_list:
    if "SELECT" in REQUESTED_PRIVILEGES:
        cursor.execute(SQL("GRANT SELECT ON {} TO {}").format(
            Identifier(table), Identifier(username))
        )
    if "DELETE" in REQUESTED_PRIVILEGES:
        cursor.execute(SQL("GRANT DELETE ON {} TO {}").format(
            Identifier(table), Identifier(username))
        )
    if "UPDATE" in REQUESTED_PRIVILEGES:
        cursor.execute(SQL("GRANT UPDATE ON {} TO {}").format(
            Identifier(table), Identifier(username))
        )
    if "TRUNCATE" in REQUESTED_PRIVILEGES:
        cursor.execute(SQL("GRANT DELETE ON {} TO {}").format(
            Identifier(table), Identifier(username))
        )
    if "REFERENCES" in REQUESTED_PRIVILEGES:
        cursor.execute(SQL("GRANT REFERENCES ON {} TO {}").format(
            Identifier(table), Identifier(username))
        )
    if "TRIGGER" in REQUESTED_PRIVILEGES:
        cursor.execute(SQL("GRANT REFERENCES ON {} TO {}").format(
            Identifier(table), Identifier(username))
        )
    if "CREATE" in REQUESTED_PRIVILEGES:
        cursor.execute(SQL("GRANT REFERENCES ON {} TO {}").format(
            Identifier(table), Identifier(username))
        )

# Maybe there are groups that already exist on the DB that a user can be added to instead

print(f"Granted {REQUESTED_PRIVILEGES} to user {username} on tables {REQUESTED_TABLES}")

db_client.commit()

db_client.close()
