# Bookstore ER Diagram

```mermaid
erDiagram
    CUSTOMER ||--o{ SALES_ORDER : places
    SALES_ORDER ||--|{ ORDER_ITEM : contains
    BOOK ||--o{ ORDER_ITEM : purchased_as
    SALES_ORDER ||--|{ EMAIL_DELIVERY : has
    CUSTOMER {
        bigint id PK
        string name
        string email UK
        datetime created_at
    }
    BOOK {
        bigint id PK
        string title
        string author
        string category
        text description
        decimal price
        string cover_url
        boolean is_active
    }
    SALES_ORDER {
        bigint id PK
        bigint customer_id FK
        uuid order_number UK
        string customer_name
        string customer_email
        decimal total_amount
        string status
        uuid checkout_key UK
        datetime created_at
    }
    ORDER_ITEM {
        bigint id PK
        bigint order_id FK
        bigint book_id FK
        string book_title
        decimal unit_price
    }
    EMAIL_DELIVERY {
        bigint id PK
        bigint order_id FK
        string recipient_email
        string attachment_name
        string status
        int attempt_count
        text last_error
        datetime sent_at
        datetime created_at
    }
```

Author and category are stored directly in the Book table. The shopping bag is stored in a Django session.

The diagram shows the five business tables. Django also creates framework tables for authentication, sessions, and administration logs. Primary keys use Django’s default `id` field. The checkout transaction ensures that every submitted order has order items and an email task. Order items have a unique constraint on `(order_id, book_id)`, allowing one digital copy of each title per order.
