# 🛒 Microservices E-Commerce Platform

A production-grade e-commerce platform decomposed into six independent microservices — each with its own database, business logic, and API — orchestrated by a FastAPI API Gateway.

---

## Architecture Overview

```
                    ┌──────────────────────────────────────────────────┐
                    │           API Gateway (FastAPI :8000)            │
                    │     JWT Auth · Routing · CORS · Rate Limiting    │
                    └────┬──────┬──────┬──────┬──────┬──────┬─────────┘
                         │      │      │      │      │      │
                    ┌────┘  ┌───┘  ┌───┘  ┌───┘  ┌───┘  ┌──┘
                    ▼       ▼      ▼      ▼      ▼      ▼
              ┌─────────┐ ┌──────┐ ┌─────┐ ┌──────┐ ┌──────────┐
              │  User   │ │Product│ │Order│ │Payment│ │Notification│
              │ Service │ │Service│ │Service│ │Service│ │  Service   │
              │ :8001   │ │:8002  │ │:8003 │ │:8004  │ │  :8005     │
              └──┬──┬───┘ └─┬─┬──┘ └─┬─┬──┘ └──┬─┬──┘ └─────┬─────┘
                 │  │       │ │     │ │       │ │            │
              ┌──┘  │   ┌───┘ │  ┌──┘ │   ┌───┘ │            │
              ▼     │   ▼     │  ▼    │   ▼      │            ▼
        ┌────────┐  │ ┌────────┐│ ┌────────┐│ ┌────────┐  ┌─────┐
        │ user_db│  │ │product_││ │order_db││ │payment_│  │redis│
        │(PG 5432)│ │ │db(PG   ││ │(PG     ││ │db(PG   │  │:6379│
        └────────┘  │ │ 5433)  ││ │ 5434)  ││ │ 5435)  │  └─────┘
                    │ └────────┘│ └────────┘│ └────────┘
Inter-service     HTTP calls with X-Service-Key header
```

### Services

| Service | Tech | Port | Database | Description |
|---------|------|------|----------|-------------|
| **Gateway** | FastAPI | `8000` | — | JWT validation, request routing, CORS |
| **User** | Django + DRF | `8001` | PostgreSQL | Registration, authentication, profiles |
| **Product** | Django + DRF | `8002` | PostgreSQL | Catalog, categories, reviews, inventory |
| **Order** | Django + DRF | `8003` | PostgreSQL | Order lifecycle, state machine |
| **Payment** | Django + DRF | `8004` | PostgreSQL | Payment processing, refunds |
| **Notification** | Django + DRF | `8005` | PostgreSQL | In-app notifications, status alerts |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)

### Clone and Run

```bash
git clone <repo-url>
cd microservices-ecommerce

# Copy environment files
cp .env.example .env
cp gateway/.env.example gateway/.env

# Start all services
docker compose up --build
```

The gateway is available at **http://localhost:8000** with interactive docs at **http://localhost:8000/docs**.

### Service Endpoints

| Service | URL |
|---------|-----|
| API Gateway | http://localhost:8000 |
| User Service | http://localhost:8001/api/v1/ |
| Product Service | http://localhost:8002/api/v1/ |
| Order Service | http://localhost:8003/api/v1/ |
| Payment Service | http://localhost:8004/api/v1/ |
| Notification Service | http://localhost:8005/api/v1/ |

---

## API Reference

All requests flow through the API Gateway at `http://localhost:8000/api/v1/`.

### Authentication

```
POST /api/v1/register     { "username", "email", "password", "password2" }
POST /api/v1/login        { "email", "password" }
POST /api/v1/token/refresh { "refresh" }
```

All authenticated endpoints require a `Bearer` token in the `Authorization` header.

### User Service

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/users/me` | User | Current user profile |
| GET | `/users/{id}` | User | User by ID |
| GET | `/users/by-username/{username}` | User | User by username |
| GET | `/profile` | User | Full profile with address |
| PATCH | `/profile` | User | Update profile |
| POST | `/change-password` | User | Change password |

### Product Service

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/products` | — | List products (paginated, filterable) |
| GET | `/products/featured` | — | Featured products |
| GET | `/products/{slug}` | — | Product detail by slug |
| GET | `/products/id/{id}` | — | Product detail by ID |
| GET | `/categories` | — | Category tree |
| GET | `/reviews/{product_id}` | — | Product reviews |
| POST | `/reviews` | User | Create review |
| POST | `/admin/products` | Admin | Create product |
| PUT | `/admin/products/{id}` | Admin | Update product |

**Query Parameters for `GET /products`:**
- `page`, `page_size` — pagination
- `search` — full-text search on name/description
- `category` — filter by category slug
- `min_price`, `max_price` — price range
- `ordering` — `price`, `-price`, `created_at`, `name`

### Order Service

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/orders` | User | Create order |
| GET | `/orders/list` | User | User's orders (filter by `?status=`) |
| GET | `/orders/{id}` | User | Order detail |
| POST | `/orders/{id}/cancel` | User | Cancel order |
| GET | `/admin/orders` | Admin | All orders |
| PATCH | `/admin/orders/{id}` | Admin | Update order status |

### Payment Service

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/payments` | User | Process payment |
| GET | `/payments/list` | User | User's payments |
| GET | `/payments/{id}` | User | Payment detail |
| GET | `/payments/by-order/{order_id}` | User | Payment by order |
| GET | `/admin/payments` | Admin | All payments |
| PATCH | `/admin/payments/{id}` | Admin | Update payment status |
| GET | `/admin/payments/{id}/refunds` | Admin | Refund history |
| POST | `/admin/payments/{id}/refund` | Admin | Issue refund |

### Notification Service

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/notifications` | User | List notifications (`?unread_only=true`) |
| GET | `/notifications/unread-count` | User | Unread count |
| GET | `/notifications/{id}` | User | Notification detail |
| POST | `/notifications/{id}/read` | User | Mark as read |
| POST | `/notifications/read-all` | User | Mark all as read |
| DELETE | `/notifications/{id}/delete` | User | Delete notification |
| POST | `/admin/notifications` | Admin | Send notification |

---

## Data Model

### User Service

```
User (AbstractUser)
├── id (PK)
├── username, email, password
├── first_name, last_name
├── is_active, date_joined
└── Profile (1:1)
    ├── phone_number, street, city
    ├── state, postal_code, country
    └── created_at, updated_at
```

### Product Service

```
Category (self-referencing)
├── id, name, slug, description
├── parent (FK → Category)
├── is_active, image
└── subcategories (reverse)

Product
├── id, name, slug, sku
├── price, compare_at_price
├── stock_quantity, low_stock_threshold
├── status (draft|active|inactive|discontinued)
├── category (FK → Category)
├── is_featured, main_image
├── meta_title, meta_description
└── ProductImage (FK) · ProductReview (FK)

ProductReview
├── product (FK), user_id
├── rating (1-5), title, comment
└── is_approved
```

### Order Service

```
Order
├── id, user_id
├── status (pending|confirmed|processing|shipped|delivered|cancelled|refunded)
├── total (auto-calculated)
├── shipping_address (JSON), billing_address (JSON)
├── notes
└── OrderItem (FK)
    ├── product_id, product_name, product_slug
    ├── quantity, unit_price, subtotal (auto)
```

### Order State Machine

```
                  ┌─── cancelled
                  │
pending ──► confirmed ──► processing ──► shipped ──► delivered
                                      │
                                      └─── refunded
```

### Payment Service

```
Payment
├── id, order_id, user_id
├── amount
├── status (pending|processing|completed|failed|refunded|partially_refunded)
├── payment_method (credit_card|debit_card|paypal|stripe|bank_transfer|cod)
├── transaction_id (unique)
├── gateway_response (JSON)
└── Refund (FK)
    ├── amount, reason
    └── gateway_refund_id
```

### Notification Service

```
Notification
├── id, user_id
├── type (order_confirmed|order_shipped|order_delivered|order_cancelled|
│         payment_received|payment_failed|welcome|promotional)
├── title, message, link
├── is_read, read_at
└── created_at
```

---

## Inter-Service Communication

Services communicate synchronously via HTTP using the shared `ServiceClient` from `shared/common/client.py`. Internal requests include an `X-Service-Key` header for authentication.

```
Order Service ──HTTP──► User Service      (validate user exists)
Order Service ──HTTP──► Product Service    (fetch prices, reserve stock)
Payment Service ──HTTP──► Order Service    (get order total)
```

The API Gateway validates JWT tokens and forwards the authenticated user's ID via the `X-User-Id` header to all backend services.

---

## Project Structure

```
microservices-ecommerce/
├── gateway/                    # FastAPI API Gateway
│   ├── main.py                 # App entry point
│   ├── config.py               # Environment configuration
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── middlewares/
│   │   └── auth.py             # JWT validation
│   ├── routes/                 # Route definitions per service
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   └── notifications.py
│   └── services/
│       └── client.py           # Async HTTP proxy client
├── services/
│   ├── user_service/           # Django app
│   │   ├── accounts/
│   │   │   ├── api/            # views, serializers, urls
│   │   │   ├── services/       # Business logic
│   │   │   └── selectors/      # Query logic
│   │   └── config/
│   ├── product_service/        # Django app
│   │   ├── products/
│   │   │   ├── api/            # views, serializers, urls, filters
│   │   │   ├── services/
│   │   │   └── selectors/
│   │   └── config/
│   ├── order_service/          # Django app
│   │   ├── orders/
│   │   │   ├── api/
│   │   │   ├── services/
│   │   │   └── selectors/
│   │   └── config/
│   ├── payment_service/        # Django app
│   │   ├── payments/
│   │   │   ├── api/
│   │   │   ├── services/
│   │   │   └── selectors/
│   │   └── config/
│   └── notification_service/   # Django app
│       ├── notifications/
│       │   ├── api/
│       │   ├── services/
│       │   └── selectors/
│       └── config/
├── shared/                     # Shared library
│   └── common/
│       ├── client.py           # Inter-service HTTP client
│       ├── exceptions.py       # Custom exception hierarchy
│       ├── responses.py        # Standard JSON response format
│       ├── pagination.py       # Paginated response helper
│       └── permissions.py      # Common permission classes
├── docker-compose.yml
└── requirements.txt
```

---

## Development

### Local Setup (without Docker)

Each service can be run independently. From the project root:

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Navigate to a service and run
cd services/user_service
cp .env.example .env   # configure your database
python manage.py migrate
python manage.py runserver 0.0.0.0:8001

# Run the gateway (separate venv)
cd gateway
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Running Tests

```bash
# All services
docker compose run --rm user_service pytest
docker compose run --rm product_service pytest
docker compose run --rm order_service pytest
docker compose run --rm payment_service pytest
docker compose run --rm notification_service pytest
```

---

## Shared Response Format

All services return a consistent JSON envelope:

```json
{
  "success": true,
  "data": { ... },
  "message": "optional message",
  "errors": null
}
```

Paginated responses:

```json
{
  "success": true,
  "data": {
    "items": [ ... ],
    "pagination": {
      "count": 100,
      "page": 1,
      "page_size": 20,
      "total_pages": 5,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

---

## Technology Stack

| Category | Technology |
|----------|-----------|
| **Languages** | Python 3.12 |
| **Frameworks** | Django 6.0, DRF 3.17, FastAPI 0.139 |
| **Auth** | JWT (SimpleJWT / python-jose) |
| **Databases** | PostgreSQL 15, Redis 7 |
| **Async Tasks** | Celery 5.6 |
| **API Docs** | OpenAPI (drf-spectacular + Swagger/ReDoc) |
| **Containerization** | Docker, Docker Compose |
| **Inter-service** | HTTP (httpx) |
| **Testing** | pytest, pytest-django |

---

## Environment Variables

Each service has its own `.env` file:

| Variable | Service | Description |
|----------|---------|-------------|
| `SECRET_KEY` | All Django | Django secret key |
| `POSTGRES_*` | All Django | Database connection |
| `REDIS_URL` | All | Redis connection string |
| `SERVICE_KEY` | All | Internal service auth key |
| `GATEWAY_*` | Gateway | Gateway configuration |

See `.env.example` files in each service directory.

---

## License

MIT
