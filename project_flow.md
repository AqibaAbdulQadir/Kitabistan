# What We've Built & Why

## User Service

### 1. The User Model (`models.py`)

**What we did:** Created a custom User model that extends Django's `AbstractUser`.

**Why we did it this way:**

| Decision | Reason |
|:---|:---|
| Removed `username` field | Modern apps use email for login, not usernames. Cleaner UX. |
| Made `email` the `USERNAME_FIELD` | Users log in with email + password |
| Custom `UserManager` | Django's default manager expects a username. Ours expects email instead. |
| Added `role` field | Distinguishes customers from admins. Useful later for permissions. |
| Added `name` field | Stores the user's display name separately from email. |

**The `create_user` method** uses `set_password()` — this **hashes** the password. We never store raw passwords in the database. If the database is breached, passwords are unreadable.

---

### 2. The Serializers (`serializers.py`)

**What serializers do:** Convert JSON ↔ Python objects. When a request comes in with JSON data, serializers validate it and turn it into model instances.

**Three serializers and their jobs:**

| Serializer | Purpose |
|:---|:---|
| `RegisterSerializer` | Takes email, name, password → validates → creates User with hashed password |
| `LoginSerializer` | Only validates email + password format. Actual authentication happens in the view. |
| `ProfileSerializer` | Returns user profile data. Fields are read-only so users can't hack their email or join date. |

**Key details:**
- `password = serializers.CharField(write_only=True)` — password is accepted on input but **never returned** in API responses
- `min_length=6` — basic security validation

---

### 3. The Settings (`settings.py`)

**`AUTH_USER_MODEL = 'accounts.User'`** tells Django: "Use our custom User model, not the default one." This must be done **before** running migrations, or you'll have to reset the database.

---

Now the views — where the actual API logic lives.

---

### 4. The Views

#### The `AuthViewSet`

| Concept | What it means |
|:---|:---|
| `GenericViewSet` | A viewset without default CRUD. We define custom `@action` methods instead. |
| `get_serializer_class()` | Returns different serializers depending on which action is called. Keeps code clean. |
| `@action(detail=False)` | Creates a URL endpoint on the viewset. `detail=False` means it's on the collection, not a single item. |

#### Registration Flow

```text
Client sends: POST /api/auth/register/
Body: { "email": "...", "name": "...", "password": "..." }
       │
       ▼
RegisterSerializer validates the data
       │
       ▼
serializer.save() → creates User (password gets hashed)
       │
       ▼
RefreshToken.for_user(user) → generates JWT access + refresh tokens
       │
       ▼
Response: user info + tokens (user is instantly logged in after registration)
```

#### Login Flow

```text
Client sends: POST /api/auth/login/
Body: { "email": "...", "password": "..." }
       │
       ▼
authenticate() → Django checks email + password against database
       │
       ▼
Success? → Generate JWT tokens
Failure? → 401 Unauthorized
```

#### JWT Tokens

| Token | Purpose | Lifetime |
|:---|:---|:---|
| **Access Token** | Attached to every API request to prove identity | Short (5-15 min) |
| **Refresh Token** | Used to get a new access token when it expires | Long (24h+) |

This way, if an access token is stolen, it only works briefly.

---

#### Profile Endpoint

- `GET` returns the logged-in user's data
- `PUT` updates name/role (partial update via `partial=True`)
- `permission_classes=[IsAuthenticated]` — must include `Authorization: Bearer <access_token>` in request header

Now URLs and JWT configuration.

---

### 5. URLs and JWT Settings

#### URLs Structure

```text
Router generates these endpoints automatically:

GET/POST    /api/auth/              → list all users / register
GET/PUT     /api/auth/{id}/         → get/update specific user
POST        /api/auth/register/     → register (our custom action)
POST        /api/auth/login/        → login (our custom action)
GET/PUT     /api/auth/profile/      → profile (our custom action)
```

#### JWT Settings

| Setting | Meaning |
|:---|:---|
| `ACCESS_TOKEN_LIFETIME` | Access token expires in 15 minutes |
| `REFRESH_TOKEN_LIFETIME` | Refresh token lasts 1 day |
| `DEFAULT_AUTHENTICATION_CLASSES` | All views use JWT by default |
| `AUTH_HEADER_TYPES` | Clients send: `Authorization: Bearer <token>` |

---

### 7. Run Migrations & Test
 
#### Test Structure

| Section | What it verifies |
|:---|:---|
| **Registration** | Valid creation, duplicate rejection, short password, missing fields |
| **Login** | Correct credentials succeed, wrong password fails, ghost users fail |
| **Profile** | Auth required for reading, updating name works, email is immutable |
| **Security** | Password stored as hash (`pbkdf2_sha256$...`), never plaintext |

##### `APIClient`

Django REST Framework's test client. Sends real HTTP requests to your API without needing a running server.

##### `force_authenticate()`

Simulates a logged-in user by attaching them to the request. No JWT token needed in tests.

---

#### Run the Tests

```bash
cd user-service
python manage.py test accounts --verbosity=2
```

    user-service/
    ├── accounts/
    │   ├── models.py       ✅ Custom User with email login
    │   ├── serializers.py  ✅ Register, Login, Profile
    │   ├── views.py        ✅ AuthViewSet with JWT
    │   ├── urls.py         ✅ Router endpoints
    │   └── tests.py        ✅ 11 tests passing
    ├── user_service/
    │   ├── settings.py     ✅ JWT configured
    │   └── urls.py         ✅ /api/ prefix
    └── manage.py

## Cart Service

### 1. Cart Model

| Field | Why |
|:---|:---|
| `user_id` (Integer) | References User Service. Not a foreign key — services don't share databases. |
| `product_id` (Integer) | References Product Service. Same reason. |
| `product_name`, `product_price` | Stored locally so cart works even if Product Service is down. |
| `unique_together` | One cart item per product. Quantity updates instead of duplicates. |
| `subtotal` property | Calculated field = `price × quantity`. Not stored, computed live. |

Now serializers and views together — they're tightly connected for Cart.

---

### 2. Cart Serializers and Views 

| Endpoint | What it does |
|:---|:---|
| `GET /api/cart/my_cart/?user_id=1` | Returns the user's full cart with items, totals |
| `POST /api/cart/add/` | Adds item. If it exists, increases quantity |
| `PUT /api/cart/update/` | Updates quantity. Setting to 0 removes the item |
| `DELETE /api/cart/remove/` | Removes a specific item |
| `DELETE /api/cart/clear/` | Empties the entire cart |

**Key design decisions:**
- `user_id` is passed in the request, not from JWT. Later we'll add auth verification via the User Service.
- `get_or_create` ensures every user automatically has one cart.
- No product validation yet — that comes when we connect to Product Service.


Now the Order models.

---

## Order Service


| Field | Purpose |
|:---|:---|
| `user_id` (Integer) | References User Service — no foreign key across services |
| `product_id` (Integer) | References Product Service |
| `order_status` | Tracks fulfillment: pending → confirmed → shipped → delivered |
| `payment_status` | Tracks payment: pending → paid (updated by Payment Service) |
| `shipping_address` | Stored at order time so it's preserved even if user updates profile |
| `product_name`, `product_price` | Snapshot at order time — price may change later |
| `created_at` / `updated_at` | Timestamps for auditing |
| `ordering = ['-created_at']` | Newest orders first |

