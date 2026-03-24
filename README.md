# FeastFlow 🍽️

**Django-Based Food Ordering Web Application**  
Browse menu items, manage a cart, place orders, and complete checkout with **Cash on Delivery** or **Razorpay online payments** using **Python, Django, SQLite, HTML, and CSS**.

## 📌 Project Overview

FeastFlow is a full-stack food ordering web application built with Django. It provides a complete ordering workflow for users, starting from menu browsing and authentication to cart management, checkout, payment, and order confirmation.

The project is designed to simulate a restaurant or cafeteria ordering system where users can:

- Explore available food items
- Search and filter menu items
- Add products to a cart
- Place orders with quantity management
- Pay online using Razorpay or choose Cash on Delivery
- View the final placed order summary

## 🎯 Objectives

- Build a complete Django-based food ordering workflow
- Implement user registration, login, and logout
- Allow customers to browse, search, and filter menu items
- Create a cart system with quantity management
- Support both online payment and Cash on Delivery
- Store order, payment, and delivery details in the database
- Organize templates, static files, and media in a reusable structure

## 📁 Repository Structure

```text
FeastFlow-master/
│
├── FeastFlow/                    # Django project settings and root URLs
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── app1/                         # Main Django application
│   ├── migrations/               # Database migrations
│   ├── models.py                 # Fooditem, Cart, Order models
│   ├── views.py                  # Business logic and checkout flow
│   ├── urls.py                   # App routes
│   └── admin.py
│
├── templates/                    # Main HTML templates
├── new_templates/                # Alternate template set
├── static/                       # CSS and static assets
├── media/                        # Uploaded and food item images
├── db.sqlite3                    # SQLite database
├── manage.py                     # Django management entry point
└── README.md                     # Project documentation
```

## ✨ Features

- User registration, login, and logout 👤
- Menu browsing with item detail pages 🍔
- Search and category filtering 🔎
- Cart management with quantity updates 🛒
- Delivery address and phone number capture 📍
- Cash on Delivery option 💵
- Razorpay online payment integration 💳
- Payment signature verification for secure checkout 🔐
- Order summary page after successful purchase ✅
- Admin panel support through Django admin ⚙️

## 🗂️ Database Models

### `Fooditem`

Stores food menu details such as:

- Item image
- Item name
- Price
- Item type/category
- Rating
- Availability

### `Cart`

Stores:

- Logged-in user
- Selected food item
- Quantity of that item

### `Order`

Stores:

- User information
- Ordered item details
- Quantity
- Price at purchase
- Address
- Phone number
- Payment method
- Payment status
- Transaction ID
- Razorpay order and signature details
- Created timestamp

## 🔄 Application Flow

### 1. Home Page

Users can browse all food items, search by item name, or filter by item category.

### 2. Authentication

Users can:

- Register a new account
- Log in with valid credentials
- Log out securely

### 3. Cart

Logged-in users can:

- Add items to the cart
- Increase quantity by adding the same item again
- Remove a single quantity
- Empty the full cart

### 4. Order Placement

Before payment, users enter:

- Delivery address
- Phone number

### 5. Payment

Two payment modes are supported:

- **Cash on Delivery**
- **Razorpay Online Payment**

### 6. Order Confirmation

After successful payment or COD confirmation, the app generates order records and shows a final order summary page.

## 🌐 Available Routes

- `/` - Home page
- `/single/<id>` - Single food item page
- `/cart/<id>` - Add item to cart
- `/showcart` - View cart
- `/emptycart` - Clear cart
- `/removeitem/<id>` - Remove or reduce cart item quantity
- `/order` - Delivery details page
- `/payment` - Payment page
- `/verify-payment` - Razorpay payment verification
- `/ordered` - Final order summary
- `/userreg` - User registration
- `/userlogin` - User login
- `/logout` - Logout user
- `/itemmreg` - Add new menu item
- `/admin/` - Django admin panel

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core programming language |
| Django 5 | Backend framework |
| SQLite | Default database |
| Razorpay Python SDK | Online payment integration |
| HTML / CSS | Frontend templates and styling |
| Django Templates | Server-side rendered UI |

## ▶️ How to Run

### Option 1 - Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/anushadonthi-2820/FeastFlow-master.git
cd FeastFlow-master

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install dependencies
pip install django pillow razorpay

# 5. Apply migrations
python manage.py migrate

# 6. Run the development server
python manage.py runserver
```

Open your browser and visit:

```text
http://127.0.0.1:8000/
```

## 💳 Razorpay Configuration

FeastFlow reads Razorpay credentials from environment variables:

```bash
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
```

If these are not set, the project currently falls back to values present in `FeastFlow/settings.py`.

## 📷 Project Highlights

- Clean Django app structure with models, views, routes, templates, static, and media folders
- End-to-end cart to checkout workflow
- Session-based pending order handling
- Online payment verification with Razorpay
- SQLite-backed persistence for development

## 💡 Key Learnings

- Django makes it efficient to build a full-stack web app with authentication, routing, models, and templates in one framework
- Cart and order workflows require careful session handling and validation
- Payment integration needs both order creation and signature verification for reliability
- Even small projects benefit from clean folder structure and reusable templates

## 🚀 Future Improvements

- Add a proper `requirements.txt`
- Add a `.gitignore` for cache, IDE, and local database files
- Improve UI styling and responsiveness further
- Add product categories and admin-side management improvements
- Add order history for users
- Add automated tests for auth, cart, and payment flows
- Move secret keys and config fully to environment variables
- Deploy with PostgreSQL and a production-ready hosting setup

## ⚠️ Notes

- The repository currently includes `db.sqlite3`, media files, `.idea` files, and Python `__pycache__` files because the project was committed as-is.
- `DEBUG = True` and `ALLOWED_HOSTS = ["*"]` are suitable for development only.
- Secret keys and fallback Razorpay credentials should be secured before production deployment.

## 👤 Author

**Anusha**

Built with ❤️ using **Python, Django, and Razorpay**
