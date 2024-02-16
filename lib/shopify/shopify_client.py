from lib.shopify.resource_base import ShopifyResource, Orders
from rich import print
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)


class ShopifyClient:
    def __init__(self, resource: ShopifyResource) -> None:
        self.resource = resource
        self.Orders = Orders(resource)
        # TODO: Add self.Products = Products(resource)
    
    def status(self):
        status = self.resource.get("/orders.json")
        return status.status_code


if __name__ == "__main__":
    resource = ShopifyResource(token=os.getenv(
        "SHOPIFY_API_KEY"), store="b59bb6-2")
    client = ShopifyClient(resource)
    orders = client.Orders.get_orders()

    if orders.status_code == 200:
        print("HTTP/1.1 200 OK | API Works!")
    else:
        print(f"HTTP/1.1 {orders.status_code} {orders.text} | API Error!")
