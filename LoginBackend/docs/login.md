```bash
auth_backend/
│
├── login_src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── user.py
│   │   │   └── token.py
│   │   ├── value_objects/
│   │   │   ├── email.py
│   │   │   └── password.py
│   │   └── repositories/
│   │       └── user_repository.py
│   │
│   ├── application/
│   │   ├── use_cases/
│   │   │   ├── login_user.py
│   │   │   ├── register_user.py
│   │   │   ├── login_guest.py
│   │   │   ├── forgot_password.py
│   │   │   └── social_login.py
│   │   └── interfaces/
│   │       ├── auth_service.py
│   │       └── email_service.py
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── models.py
│   │   │   └── session.py
│   │   ├── repositories/
│   │   │   └── user_repository_impl.py
│   │   ├── services/
│   │   │   ├── jwt_service.py
│   │   │   ├── bcrypt_service.py
│   │   │   ├── google_auth_service.py
│   │   │   ├── github_auth_service.py
│   │   │   └── email_service_impl.py
│   │   └── config/
│   │       └── settings.py
│   │
│   └── api/
│       ├── v1/
│       │   ├── routes/
│       │   │   └── auth_routes.py
│       │   ├── schemas/
│       │   │   └── auth_schemas.py
│       │   ├── dependencies/
│       │   │   └── auth_deps.py
│       │   └── controllers/
│       │       └── auth_controller.py
│       ├── middleware/
│       │   ├── auth_middleware.py
│       │   └── cors_middleware.py
│       └── app.py
│
├── tests/
├── requirements.txt
├── .env.example
└── run.py
```