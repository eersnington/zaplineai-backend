import requests
import time


class ShopifyResource(requests.Session):
    def __init__(self, token: str, store: str, api_version="2024-01") -> None:
        super().__init__()
        self.token = token
        self.store = store
        self.api_version = api_version
        self.baseurl = f"https://{self.store}.myshopify.com/admin/api/{self.api_version}"

        self.headers.update({
            "X-Shopify-Access-Token": self.token,
            "Content-Type": "application/json"
        })

        def rate_hook(r, *args, **kwargs):
            if "X-Shopify-Shop-Api-Call-Limit" in r.headers:
                print("rate:", r.headers["X-Shopify-Shop-Api-Call-Limit"])
            if r.status_code == 429:
                time.sleep(int(float(r.headers["Retry-After"])))
                print("rate limit reached, sleeping")

        self.hooks["response"].append(rate_hook)

    def request(self, method, url, *args, **kwargs):
        full_url = f"{self.baseurl}{url}"
        return super().request(method, full_url, *args, **kwargs)


class ShopifyResourceBase:
    def __init__(self, resource: ShopifyResource, resource_name) -> None:
        self.resource = resource
        self.resource_name = resource_name

    def get(self, url):
        return self.resource.get(url)

    def post(self, url, data):
        return self.resource.post(url, json=data)

    def put(self, url, data):
        return self.resource.put(url, json=data, headers={"Content-Type": "application/json"})

    def delete(self, url):
        return self.resource.delete(url)


class Orders(ShopifyResourceBase):
    def __init__(self, resource: ShopifyResource) -> None:
        super().__init__(resource, "orders")

    def get_orders(self):
        return self.get("/orders.json")

    def get_order(self, order_id):
        return self.get(f"/orders/{order_id}.json")

    def create_order(self, data):
        return self.post("/orders.json", data)

    def update_order(self, order_id, data):
        return self.put(f"/orders/{order_id}.json", data)

    def delete_order(self, order_id):
        return self.delete(f"/orders/{order_id}.json")

# TODO: Add Products class
