# PrintForge Fullstack Ecommerce

PrintForge is now structured as a fullstack ecommerce app:

- `frontend/` - React + Vite storefront
- `backend/` - Django API with MySQL database configuration
- `productsimg/` and `assets/` - existing product images and video assets reused by the new app
- `frontend/public/productsimg/` - permanent frontend copy of product images for fallback/local display
- `frontend/src/localProducts.js` - permanent local catalog generated from `productsimg/`

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

If you add new product images, also copy them into the React public folder so the fallback catalog remains permanent:

```bash
rsync -av productsimg/ frontend/public/productsimg/
```

Add live keys in `backend/.env`:

```bash
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
SHIPROCKET_EMAIL=
SHIPROCKET_PASSWORD=
WHATSAPP_NUMBER=919944823602
ADMIN_PANEL_PASSWORD=admin123
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://fullstack-zt6v.onrender.com
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

## Render Connection

The deployed backend URL is:

```text
https://fullstack-zt6v.onrender.com
```

The frontend must use the API base with `/api`:

```text
https://fullstack-zt6v.onrender.com/api
```

For Render backend, set these environment variables:

```bash
DJANGO_SECRET_KEY=your-secret
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=fullstack-zt6v.onrender.com
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://your-frontend-domain.com
MYSQL_DATABASE=...
MYSQL_USER=...
MYSQL_PASSWORD=...
MYSQL_HOST=...
MYSQL_PORT=3306
WHATSAPP_NUMBER=919944823602
ADMIN_PANEL_PASSWORD=admin123
```

After deploying backend, run migrations and seed products on Render:

```bash
python backend/manage.py migrate
python backend/manage.py seed_products
```

If your Render product API returns `{"products": [], "categories": []}`, the backend database has not been seeded yet.
