# Aforro Backend Assignment

A scalable inventory and order management backend built using Django, PostgreSQL, Redis, Celery, and Docker.

---

# Overview

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

# Tech Stack

## Backend

* Django 5.2
* Django REST Framework

## Database

* PostgreSQL

## Caching & Messaging

* Redis
* Celery

## Containerization

* Docker
* Docker Compose

## Runtime

* Python 3.11

## Testing

* Django Test Framework
* DRF APITestCase

---

# Architecture

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

# Features

## Product Management

* Product categories
* Product catalog
* Price tracking
* Inventory availability

## Store Management

* Multiple stores
* Store-specific inventory
* Inventory tracking per product

## Order Processing

* Order creation endpoint
* Inventory validation
* Atomic transactions
* Row-level locking using `select_for_update`
* Automatic order confirmation or rejection

## Product Search

Supports:

* Keyword search
* Category search
* Category filtering
* Price filtering
* Store filtering
* In-stock filtering
* Sorting options
* Pagination

## Product Suggestions

Autocomplete endpoint with:

* Prefix prioritization
* Maximum 10 suggestions
* Minimum query length validation

---

# Database Models

## Category

```text
id
name
```

## Product

```text
id
category
title
description
price
```

## Store

```text
id
name
location
```

## Inventory

```text
id
store
product
quantity
```

## Order

```text
id
store
status
created_at
```

## OrderItem

```text
id
order
product
quantity_requested
```

---

# Redis Integration

## Product Search Caching

Search responses are cached in Redis for 300 seconds.

Cache key example:

```text
product_search:/api/search/products/?q=laptop
```

Benefits:

* Reduced database load
* Faster repeated searches
* Improved API response times

### Cache Strategy

To keep the implementation simple, cache freshness is maintained through TTL expiration.

In a production environment, cache invalidation would be triggered through Django signals whenever product, category, or inventory data changes.

Cache TTL:

```text
300 seconds
```

---

## Rate Limiting

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

# Celery Integration

Celery is configured using Redis as the message broker.

## Asynchronous Processing Design

The assignment suggested asynchronous workflows such as order confirmations, inventory summaries, or search preprocessing.

A Low Stock Alert workflow was implemented because it represents a realistic inventory-management use case.

Whenever inventory for a product falls below 10 units after order processing, a Celery task is dispatched asynchronously through Redis and executed by a background worker.

This keeps order processing fast while allowing inventory monitoring to scale independently.

## Implemented Task

### Low Stock Alert

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
* Separation of concerns

---

# API Endpoints

## API Documentation

Interactive Swagger UI:
http://localhost:8000/api/docs/

OpenAPI Schema:
http://localhost:8000/api/schema/

## Create Order

### Endpoint

```http
POST /orders/
```

### Request

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

### Successful Response

```json
{
  "order_id": 1,
  "status": "CONFIRMED"
}
```

### Rejected Response

If inventory is insufficient:

```json
{
  "order_id": 25,
  "status": "REJECTED"
}
```

---

## Store Orders

### Endpoint

```http
GET /stores/<store_id>/orders/
```

Returns:

* Order history
* Total items
* Order status

---

## Store Inventory

### Endpoint

```http
GET /stores/<store_id>/inventory/
```

Returns:

* Product information
* Category
* Available quantity

---

## Product Search

### Endpoint

```http
GET /api/search/products/
```

### Examples

Search by keyword:

```http
GET /api/search/products/?q=laptop
```

Filter by category:

```http
GET /api/search/products/?category=Electronics
```

Filter by minimum price:

```http
GET /api/search/products/?min_price=100
```

Filter by maximum price:

```http
GET /api/search/products/?max_price=1000
```

Filter by store:

```http
GET /api/search/products/?store_id=1
```

Filter by stock availability:

```http
GET /api/search/products/?in_stock=true
```

Sort by price:

```http
GET /api/search/products/?sort=price
```

Sort by newest:

```http
GET /api/search/products/?sort=newest
```

---

## Pagination

Product search results are paginated using Django REST Framework.

Default page size:

```text
20 items
```

Example:

```http
GET /api/search/products/?page=2
```

Response:

```json
{
  "count": 1000,
  "next": "http://localhost:8000/api/search/products/?page=3",
  "previous": "http://localhost:8000/api/search/products/",
  "results": [
    {
      "id": 21,
      "title": "Gaming Laptop"
    }
  ]
}
```

---

## Product Suggestions

### Endpoint

```http
GET /api/search/suggest/?q=lap
```

### Response

```json
{
  "results": [
    "Gaming Laptop",
    "Laptop Stand"
  ]
}
```

---

# Seed Data

The project includes a management command for generating sample data.

Generated:

```text
12 Categories
1000 Products
20 Stores
6000 Inventory Records
```

This exceeds the assignment requirement of at least 300 products per store.

Run:

```bash
python manage.py seed_data
```

---

# Running the Project

## Clone Repository

```bash
git clone <repository-url>
cd aforro-backend
```

---

## Environment Configuration

A `.env.example` file is included in the repository.

Create a `.env` file using the provided example before starting the application.

Example:

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

## Start Services

```bash
docker compose up --build
```

---

## Run Migrations

```bash
docker compose exec web python manage.py migrate
```

---

## Create Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

---

## Access Application

Django Admin:

```text
http://localhost:8000/admin/
```

Product Search API:

```text
http://localhost:8000/api/search/products/
```

---

# Running Tests

Run all tests:

```bash
docker compose exec web python manage.py test
```

Current test coverage:

```text
7 Automated Tests
```

Covered scenarios:

* Successful order creation
* Rejected order creation
* Product search
* Search cache creation
* In-stock filtering
* Product suggestions
* Rate limiting

Example result:

```text
Found 7 test(s)
.......
OK
```

---

# Scalability Considerations

* Redis caching reduces repeated database queries for popular searches.
* Redis-based rate limiting protects autocomplete endpoints from abuse.
* Celery workers process background jobs independently from API requests.
* PostgreSQL row-level locking prevents overselling during concurrent order creation.
* Search queries use `select_related()` and aggregation to reduce query count.
* Multiple Django API instances and Celery workers can be deployed horizontally behind a load balancer.
* Redis provides a centralized cache and message broker across all application instances.

---

# Design Decisions

## PostgreSQL

Chosen for:

* Strong relational consistency
* Transaction support
* Indexing capabilities

## Redis

Used for:

* Search result caching
* Rate limiting
* Celery message broker

## Celery

Used for:

* Background processing
* Low stock notifications
* Scalable asynchronous workflows

## Transaction Safety

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

# Future Improvements

* JWT Authentication
* Role-based access control
* Search relevance ranking
* Email notifications
* Inventory reservation system
* Monitoring and observability
* CI/CD pipeline
* Production deployment on AWS

---

# Author

Kanishq Dhangar

Backend Assignment Submission

Django • PostgreSQL • Redis • Celery • Docker
