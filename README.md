# Aforro Backend Assignment

A scalable inventory and order management backend built using Django, PostgreSQL, Redis, Celery, and Docker.

---

## Overview

This project implements a backend system for managing products, stores, inventory, and order processing.

The system supports:

* Product catalog management
* Store inventory tracking
* Order creation and fulfillment
* Product search and autocomplete
* Redis caching
* Redis-based rate limiting
* Celery asynchronous task processing
* Dockerized deployment
* Automated test coverage

---

## Tech Stack

### Backend

* Django 5
* Django REST Framework

### Database

* PostgreSQL

### Caching & Messaging

* Redis
* Celery

### Containerization

* Docker
* Docker Compose

### Testing

* Django Test Framework
* DRF APITestCase

---

## Architecture

```text
Client
   |
   v
Django REST APIs
   |
   +--------------------+
   |                    |
   v                    v
PostgreSQL           Redis
(Database)      (Cache + Broker)
                         |
                         v
                    Celery Worker
```

---

## Features

### Product Management

* Product categories
* Product catalog
* Price tracking
* Inventory availability

### Store Management

* Multiple stores
* Store-specific inventory
* Inventory tracking per product

### Order Processing

* Order creation endpoint
* Inventory validation
* Atomic transactions
* Row-level locking using `select_for_update`
* Automatic order confirmation or rejection

### Product Search

Supports:

* Keyword search
* Category search
* Category filtering
* Price filtering
* Store filtering
* In-stock filtering
* Sorting options

### Product Suggestions

Autocomplete endpoint with:

* Prefix prioritization
* Maximum 10 suggestions
* Minimum query length validation

---

## Database Models

### Category

```text
id
name
created_at
```

### Product

```text
id
category
title
description
price
created_at
```

### Store

```text
id
name
location
created_at
```

### Inventory

```text
id
store
product
quantity
updated_at
```

### Order

```text
id
store
status
created_at
```

### OrderItem

```text
id
order
product
quantity_requested
```

---

## Redis Integration

### Product Search Caching

Search results are cached using Redis.

Cache key example:

```text
product_search:/api/search/products/?q=laptop
```

Benefits:

* Reduced database load
* Faster repeated searches
* Improved API performance

Cache TTL:

```text
300 seconds
```

---

### Rate Limiting

Redis is used for IP-based rate limiting on the autocomplete endpoint.

Limit:

```text
20 requests per minute
```

Response:

```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

Status:

```text
429 Too Many Requests
```

---

## Celery Integration

Celery is configured using Redis as the message broker.

### Implemented Task

Low Stock Alert

When inventory falls below:

```text
10 units
```

a Celery task is triggered asynchronously.

Example worker output:

```text
LOW STOCK ALERT

Store: Store 1
Product: Gaming Laptop
Remaining Quantity: 8
```

Benefits:

* Non-blocking order processing
* Background task execution
* Improved scalability

---

## API Endpoints

### Create Order

```http
POST /orders/
```

Request:

```json
{
  "store_id": 1,
  "items": [
    {
      "product_id": 10,
      "quantity_requested": 2
    }
  ]
}
```

Response:

```json
{
  "order_id": 1,
  "status": "CONFIRMED"
}
```

---

### Store Orders

```http
GET /stores/<store_id>/orders/
```

Returns:

* Order history
* Total items
* Order status

---

### Store Inventory

```http
GET /stores/<store_id>/inventory/
```

Returns:

* Product information
* Category
* Available quantity

---

### Product Search

```http
GET /api/search/products/
```

Examples:

```http
/api/search/products/?q=laptop
```

```http
/api/search/products/?category=Electronics
```

```http
/api/search/products/?min_price=100
```

```http
/api/search/products/?max_price=1000
```

```http
/api/search/products/?store_id=1
```

```http
/api/search/products/?in_stock=true
```

```http
/api/search/products/?sort=price
```

---

### Product Suggestions

```http
GET /api/search/suggest/?q=lap
```

Response:

```json
{
  "results": [
    "Gaming Laptop",
    "Laptop Stand"
  ]
}
```

---

## Seed Data

The project includes a management command for generating sample data.

Generated:

```text
12 Categories
1000 Products
20 Stores
6000 Inventory Records
```

Run:

```bash
python manage.py seed_data
```

---

## Running the Project

### Clone Repository

```bash
git clone <repository-url>
cd aforro-backend
```

---

### Create Environment File

```env
POSTGRES_DB=aforro
POSTGRES_USER=aforro
POSTGRES_PASSWORD=aforro
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/2
```

---

### Start Services

```bash
docker compose up --build
```

---

### Run Migrations

```bash
docker compose exec web python manage.py migrate
```

---

### Create Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

---

### Access Application

```text
Django Admin:
http://localhost:8000/admin/
```

```text
Search API:
http://localhost:8000/api/search/products/
```

---

## Running Tests

Run all tests:

```bash
docker compose exec web python manage.py test
```

Current test coverage:

```text
7 Automated Tests
```

Tests include:

* Order confirmation
* Order rejection
* Product search
* Search caching
* In-stock filtering
* Product suggestions
* Rate limiting

---

## Design Decisions

### PostgreSQL

Chosen for:

* Strong relational consistency
* Transaction support
* Indexing capabilities

### Redis

Used for:

* Search result caching
* Rate limiting
* Celery message broker

### Celery

Used for:

* Background processing
* Low stock notifications
* Scalable asynchronous workflows

### Transaction Safety

Order creation uses:

```python
transaction.atomic()
```

and

```python
select_for_update()
```

to prevent inventory race conditions during concurrent order placement.

---

## Future Improvements

* JWT Authentication
* Role-based access control
* Inventory reservation system
* Search ranking and relevance scoring
* Email notifications
* Monitoring and observability
* CI/CD pipeline
* Production deployment on AWS

---

## Author

Kanishq Kumar Dhangar

Backend Assignment Submission
Django • PostgreSQL • Redis • Celery • Docker
