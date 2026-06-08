# PrintForge Fullstack Ecommerce

PrintForge is now structured as a fullstack ecommerce app:

- `frontend/` - React + Vite storefront
- `backend/` - Django API with MySQL database configuration
- `productsimg/` and `assets/` - existing product images and video assets reused by the new app

## Features

- Product catalog with categories, search, featured/custom product flags
- Cart, quantity controls, buy-now checkout drawer
- Customer address and required 6 digit delivery pincode
- Shipping calculation from the Coimbatore hub pincode `641001`
- Razorpay order creation and checkout handoff
- Razorpay payment verification endpoint
- Shiprocket shipment creation after successful payment verification
- WhatsApp contact buttons for customization, support, and delivery questions
- Django admin for products and orders
- Password-protected React admin panel for order stats and product price/name editing

## Backend Setup

```bash
cd backend
cp .env.example .env
python3 -m pip install -r requirements.txt
```

Start MySQL/XAMPP, then create the database:

```bash
/Applications/XAMPP/xamppfiles/bin/mysql -u root --execute="CREATE DATABASE IF NOT EXISTS printforge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
```

Run migrations and seed products:

```bash
python3 manage.py migrate
python3 manage.py seed_products
python3 manage.py runserver 8000
```

Run `python3 manage.py seed_products` again any time you add images under `productsimg/`; it imports every product image into the correct category folder.

Add live keys in `backend/.env`:

```bash
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
SHIPROCKET_EMAIL=
SHIPROCKET_PASSWORD=
WHATSAPP_NUMBER=919944823602
ADMIN_PANEL_PASSWORD=admin123
```

Without Razorpay or Shiprocket credentials, the backend returns development IDs so the order flow can still be tested.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

Set a different API base if needed:

```bash
VITE_API_BASE=http://localhost:8000/api npm run dev
```
