from resource_base import ShopifyResource, Orders
from rich import print
import os
import time
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

    order_id = None
    order_number = None
    for order in orders.json()["orders"]:
        if order["customer"] is not None:
            if order["customer"]["phone"] == "+12512209809":
                item_names = [item["title"] for item in order["line_items"]]
                order_id = order["id"]
                order_number = order["order_number"]
                print(f"Order {order_id}: ", item_names)
                break

    
    print("Order ID:", order_id)
    print("Order Number:", order_number)
    update = client.resource.put(f"/orders/{order_id}.json", {"order": {"note": "Return initiated by customer through call"}}) # client.Orders.update_order(order_id, {"order": {"note": "Test"}}) 
    print(update.status_code, update.text) 

    if orders.status_code == 200:
        print("HTTP/1.1 200 OK | API Works!")
    else:
        print(f"HTTP/1.1 {orders.status_code} {orders.text} | API Error!")
