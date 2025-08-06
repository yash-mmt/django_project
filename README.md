# 🛒 Small E-commerce System

This is a simple e-commerce backend built with **Django REST Framework** that supports **Superadmin** and **Normal Users** roles with functionalities like product listings, cart management, order placement, invoicing, and stock management.

---

## 🚀 Features

### User Roles:

#### Superadmin
- Full access to **all users’ data**.
- Can **Add, Update, Delete** any **Items, Categories, Carts, Addresses, Orders**.

#### Normal Users
- Can **Add, Update, Delete** their own **Items, Categories**.
- Can only manage their own **Cart, Addresses, Orders**.

---

### Modules & Functionalities:

#### 🗂️ Categories & Items
- All users can add **Categories** and **Items**.
- Normal Users can **edit or delete only their own items/categories**.
- Admin can manage (CRUD) **all items and categories**.

#### 🛒 Cart Management
- Normal Users can **add, update, and delete** their **own cart**.
- Admin can access and manage **any user’s cart**.

#### 🔐 Authentication
- JWT-based Authentication with **Access Token** and **Refresh Token**.
- Login API returns tokens to authenticate further requests.

#### 🏠 Addresses
- Users can add **multiple addresses**.
- At any time, **one address is marked as Default**.
- If no address is selected during ordering, the system uses the **Default Address**.
- Normal Users can manage **only their own addresses**.
- Admin can access and manage **all users' addresses**.

#### 📦 Orders
**Normal Users can:**
- Place Orders.
- View their **Order History and Details**.
- Download **Invoice PDF** after placing an order.

**Admin can:**
- View and manage **all orders**.
- Check **Order Billing Details**.

- After an order is placed, **Item Stock is automatically adjusted**.

---

## 🔑 API Authentication Flow
1. User logs in → Receives **Access Token** & **Refresh Token**.
2. Use **Access Token** for authenticated API requests.
3. **Refresh Token** is used to obtain a new Access Token after expiry.

---

## 🏗️ Tech Stack

### Backend
- **Django** — Python-based web framework.
- **Django REST Framework (DRF)** — For building RESTful APIs.
- **SimpleJWT** — JWT-based authentication (Access & Refresh Tokens).
- **ReportLab** — PDF generation library (for Invoices).

### Database
- **PostgreSQL**

### API Documentation
- **DRF Browsable API** — Built-in interactive API.
- **Postman** 

### Environment & Dependency Management
- **Python Virtual Environment (venv)** — Isolated environment.
- **pip** — Python package installer.
