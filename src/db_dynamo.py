import os
import boto3

TABLE_NAME = os.getenv("DYNAMODB_TABLE", "booksapi-local-books")

def get_dynamodb():
    ENV = os.getenv("ENV", "local")
    if ENV == "local":
        return boto3.resource(
            "dynamodb",
            endpoint_url="http://localhost:8000",
        )
    else:
        return boto3.resource("dynamodb")


def get_table():
    dynamodb = get_dynamodb()
    return dynamodb.Table(TABLE_NAME)


def create_book(book: dict):
    table = get_table()
    table.put_item(Item=book)


def get_book(raw_id: str):
    table = get_table()
    response = table.get_item(Key={"pk": raw_id})
    item = response.get("Item")

    if not item:
        return None

    return {k: v for k, v in item.items() if k != "pk"}


def list_books():
    table = get_table()

    # DynamoDB scan
    response = table.scan()
    items = response.get("Items", [])

    return items
