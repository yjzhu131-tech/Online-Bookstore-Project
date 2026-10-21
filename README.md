# Online Bookstore

A simple website for browsing books and placing orders. Customers do not need to create an account or log in.

## Features

- Browse books and view their details.
- Search by title or author and filter by category.
- Add books to the cart or remove them.
- Place an order using a name and email address.
- Generate a confirmation email with a `.txt` eBook placeholder attached.

This is a demonstration project. It does not collect payments or include actual eBook content.

## Requirements

- Python 3.12 or later
- A terminal and a web browser

The project uses Django and SQLite. You do not need to install a separate database server.

## Run the program for the first time

Open a terminal in the `Online-Bookstore-Project` folder. Run these commands one at a time:

### 1. Create and activate a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install the required package

```bash
python -m pip install -r requirements.txt
```

### 3. Set up the database and add sample books

```bash
python manage.py migrate
python manage.py seed_books
```

The catalog includes eight well-known books with USD eBook demo prices based on online listings. See [book prices and sources](docs/book-prices.md). Running `seed_books` again will not duplicate books or overwrite your edits. It also hides the original fictional samples while preserving existing orders.

### 4. Start the website

```bash
python manage.py runserver
```

Keep this terminal open, then visit **http://127.0.0.1:8000/** in your browser.

## Run the program again

You only need to activate the virtual environment and start the server.

On macOS or Linux:

```bash
source .venv/bin/activate
python manage.py runserver
```

On Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
python manage.py runserver
```

To stop the server, press **Control + C** in the terminal where it is running.

## How to use the website

1. Open the website and browse or search for a book.
2. Click **Add to cart**.
3. Open **Cart** and click **Checkout**.
4. Enter your name and email address.
5. Click **Place order** to see your order confirmation.

## Where is the email?

By default, emails are saved as files in the **`var/emails/`** folder inside the project. They are **not sent to your inbox**. Each saved email includes a `.txt` placeholder attachment listing the books you ordered.

To send real emails, configure your SMTP service using the settings in [.env.example](.env.example). Export those settings in your terminal before starting the server. The program does not load `.env` files automatically.

If an email fails, check your SMTP settings and retry with:

```bash
python manage.py retry_emails
```

## Manage books (optional)

You do not need an administrator account to browse or place an order.

To manage books through the admin dashboard, create an administrator account:

```bash
python manage.py createsuperuser
```

With the server running, visit **http://127.0.0.1:8000/admin/** and log in with that account. You can manage books, view orders, and retry failed emails.

## Database diagram

See the [ER diagram](docs/ER-Diagram.md) or the [Mermaid source](docs/er-diagram.mmd).

The five main tables are:

- **Book**: title, author, category, description, and price.
- **Customer**: customer name and email address.
- **SalesOrder**: order information and total price.
- **OrderItem**: books purchased in each order.
- **EmailDelivery**: email delivery status and retry information.

Author and category are fields in Book, not separate tables.

## Run tests

```bash
python manage.py test
```
