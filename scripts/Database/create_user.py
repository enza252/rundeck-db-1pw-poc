# /bin/python3
import psycopg2
from os import getenv
from datetime import datetime
from onepasswordconnectsdk.client import (Client, new_client)
from onepasswordconnectsdk.models import Item, ItemVault, Field, GeneratorRecipe

# get email of requesting user from rundeck: $RD_JOB_USERNAME (?)
REQUESTING_USER: str = getenv("RD_JOB_USERNAME").replace(".", "")

REQUESTED_DATABASE: str = getenv("RD_OPTION_DATABASE")
REQUESTED_TABLES: str = getenv("RD_OPTION_TABLES")
REQUESTED_PRIVILEGES: str = getenv("RD_OPTION_PRIVILEGES")

OP_CONNECT_TOKEN: str = getenv("OP_CONNECT_TOKEN")

if REQUESTING_USER is None or REQUESTED_DATABASE is None or REQUESTED_TABLES is None or REQUESTED_PRIVILEGES is None:
    raise Exception("User input values not set")

if OP_CONNECT_TOKEN is None:
    raise Exception("OP_CONNECT_TOKEN not set")

# generate db user username: <username>
# probably needs some sanitization here
user = (REQUESTING_USER + REQUESTED_DATABASE).lower()

# establish database connection

print("Attempting to establish connection with database")
db_client = psycopg2.connect("postgresql://dbuser:password@0.0.0.0:5432/sampledb")
print("Database connection established!")

# establish 1pw connection
print("Attempting to establish connection with 1Password Connect")
connect_client: Client = new_client(url="http://0.0.0.0:8080", token=OP_CONNECT_TOKEN)
print("1Password Connect connection established!")

vault_id = connect_client.get_vault_by_title("poc-test").id
credential_title = f"{REQUESTED_DATABASE} {REQUESTED_TABLES} poc {REQUESTING_USER}"

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

cursor = db_client.cursor()

# ToDo - this is currently not working due to a syntax error
create_user_sql = f"CREATE USER %(username)s WITH PASSWORD %(password)s"

create_user_data = {
    "username": username,
    "password": password
}

cursor.execute(create_user_sql, create_user_data)

print(f"Created user {username}")

grant_user_command = f"GRANT %(priv)s ON %(tables)s TO %(username)s"
grant_user_data = {
    "priv": REQUESTED_PRIVILEGES,
    "tables": REQUESTED_TABLES,
    "username": username
}

cursor.execute(grant_user_command, grant_user_data)
# Maybe there are groups that already exist on the DB that a user can be added to instead

print(f"Granted {REQUESTED_PRIVILEGES} to user {username} on tables {REQUESTED_TABLES}")
