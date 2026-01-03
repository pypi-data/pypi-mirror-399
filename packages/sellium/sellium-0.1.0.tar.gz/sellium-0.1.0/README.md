# sellium (Sellium Python SDK)

Official, production-ready Python SDK for the **Sellium API (v1)**.

This SDK provides a single `SelliumClient` with service groups for:
- Store
- Products
- Orders
- Coupons
- Customers
- Tickets
- Feedback
- Groups
- Blacklist

> Works great for building dashboards, automations, and integrations on top of Sellium.

---

## Requirements

- Python **3.9+**

---

## Install

### From PyPI (recommended)
```bash
pip install sellium
```

### From GitHub
```bash
pip install git+https://github.com/Sellium-site/sellium-python.git
```

### Local development (editable)
From the repo root:
```bash
pip install -e .
```

---

## Quick Start

```python
from sellium import SelliumClient, APIError

BASE_URL = "https://yourdomain.com/api/v1"

client = SelliumClient(
    api_key="YOUR_API_KEY",
    store_id="YOUR_STORE_ID",
    base_url=BASE_URL,
)

try:
    data, meta = client.products.list(page=1, limit=20)
    print("Products:", len(data["data"]["products"]))

    if meta.rate_limit:
        print("Rate remaining:", meta.rate_limit.remaining)

except APIError as e:
    print("API Error:", e)

finally:
    client.close()
```

---

## Client Options

```python
from sellium import SelliumClient

client = SelliumClient(
    api_key="API_KEY",
    store_id="STORE_ID",
    base_url="https://yourdomain.com/api/v1",
    user_agent="my-app/1.0",
    timeout=30.0,
)
```

---

## Services & Endpoints

### Store
- `GET /store`
```python
data, meta = client.store.get()
```

### Products
- `GET /products`
- `POST /products`
- `GET /products/{productId}`
- `PATCH /products/{productId}`
- `DELETE /products/{productId}`

```python
data, meta = client.products.list(page=1, limit=25, active=True, group_id="group_id")
data, meta = client.products.create({"name": "Item", "price_in_cents": 999, "delivery_type": "file"})
data, meta = client.products.get("product_id")
data, meta = client.products.update("product_id", {"price_in_cents": 1299})
data, meta = client.products.delete("product_id")
```

### Orders
- `GET /orders`
- `POST /orders`
- `GET /orders/{orderId}`
- `PATCH /orders/{orderId}`

```python
data, meta = client.orders.list(page=1, limit=25, status="pending")
data, meta = client.orders.create({"product_id": "pid", "customer_email": "a@b.com", "quantity": 1})
data, meta = client.orders.get("order_id")
data, meta = client.orders.update("order_id", {"status": "completed"})
```

### Coupons
- `GET /coupons`
- `POST /coupons`
- `GET /coupons/{couponId}`
- `PATCH /coupons/{couponId}`
- `DELETE /coupons/{couponId}`

```python
data, meta = client.coupons.list(page=1, limit=25, active=True)
data, meta = client.coupons.create({"code": "NEW10", "type": "percentage", "value": 10})
data, meta = client.coupons.get("coupon_id")
data, meta = client.coupons.update("coupon_id", {"is_active": False})
data, meta = client.coupons.delete("coupon_id")
```

### Customers
- `GET /customers`
- `GET /customers/{email}`

```python
data, meta = client.customers.list(page=1, limit=25, email="gmail.com")
data, meta = client.customers.get("customer@example.com")
```

### Tickets
- `GET /tickets`
- `GET /tickets/{ticketId}`
- `POST /tickets/{ticketId}/reply`
- `PATCH /tickets/{ticketId}`

```python
data, meta = client.tickets.list(page=1, limit=25, status="open", priority="high")
data, meta = client.tickets.get("ticket_id")
data, meta = client.tickets.reply("ticket_id", {"message": "Thanks! We'll help you shortly."})
data, meta = client.tickets.update("ticket_id", {"status": "closed"})
```

### Feedback
- `GET /feedback`
- `GET /feedback/{feedbackId}`
- `PATCH /feedback/{feedbackId}`

```python
data, meta = client.feedback.list(page=1, limit=25, rating=5, has_response=False)
data, meta = client.feedback.get("feedback_id")
data, meta = client.feedback.update("feedback_id", {"response": "Appreciate it!", "is_visible": True})
```

### Groups
- `GET /groups`
- `POST /groups`
- `GET /groups/{groupId}`
- `PATCH /groups/{groupId}`
- `DELETE /groups/{groupId}`

```python
data, meta = client.groups.list(page=1, limit=25, active=True)
data, meta = client.groups.create({"name": "Boosts", "is_active": True})
data, meta = client.groups.get("group_id")
data, meta = client.groups.update("group_id", {"name": "Boosts (Updated)"})
data, meta = client.groups.delete("group_id")
```

### Blacklist
- `GET /blacklist`
- `GET /blacklist/{entryId}`
- `POST /blacklist`
- `DELETE /blacklist/{entryId}`

```python
data, meta = client.blacklist.list(page=1, limit=25, type="email", search="@gmail.com")
data, meta = client.blacklist.get("entry_id")
data, meta = client.blacklist.create({"type": "email", "value": "blocked@example.com", "reason": "Chargebacks"})
data, meta = client.blacklist.delete("entry_id")
```

---

## Response Meta (Rate Limits)

Most methods return `(data, meta)`.

```python
data, meta = client.products.list(page=1, limit=10)

if meta.rate_limit:
    print(meta.rate_limit.limit, meta.rate_limit.remaining, meta.rate_limit.reset_sec)
```

---

## Errors

Errors raise `APIError`:

```python
from sellium import APIError

try:
    client.products.get("bad_id")
except APIError as e:
    print(e.status, e.code, e.message)
```

---

## Project Structure

```text
sellium-python/
├── sellium/
│   ├── __init__.py
│   ├── client.py
│   ├── errors.py
│   ├── types.py
│   ├── _http.py
│   └── services/
│       ├── __init__.py
│       ├── store.py
│       ├── products.py
│       ├── orders.py
│       ├── coupons.py
│       ├── customers.py
│       ├── tickets.py
│       ├── feedback.py
│       ├── blacklist.py
│       └── groups.py
└── examples/
    └── basic.py
```

---

## Development

Optional lint:
```bash
python -m pip install ruff
ruff check .
```

Quick import sanity check:
```bash
python -c "from sellium import SelliumClient; print('ok')"
```

---

## License

MIT License

---
## Contributing

Pull requests are welcome.  
Please ensure all code is formatted with `gofmt` and passes `go test ./...` before submitting.

---

## Support

For questions or issues related to the Sellium API, please refer to the official Sellium documentation or open an issue in this repository.
