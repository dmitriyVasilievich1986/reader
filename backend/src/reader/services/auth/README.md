# Auth

Authentication primitives used by the backend: bcrypt-based password hashing and signed JWT access tokens carrying a user identity and expiry.

The module exposes two stateless services — `PasswordService` for hashing/verifying user passwords at registration and login, and `JWTTokenService` for issuing and decoding the short-lived JWTs returned by the `/login` endpoint and validated by the `user_authorized` FastAPI dependency.

## Components

| Component          | Responsibility                                                                                                                                           |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PasswordService`  | Static helpers that hash a plaintext password with `bcrypt` (random per-password salt) and verify a candidate password against a stored hash.            |
| `JWTTokenService`  | Instance-scoped service configured with a signing secret and algorithm. Generates 1-day JWTs for a given `user_id` and decodes/verifies incoming tokens. |
| `AccessToken`      | Pydantic model returned by `generate_token`: the signed JWT string and its absolute expiry.                                                              |
| `JWTTokenMetadata` | Pydantic model returned by `decode_token`: the subject `user_id` and `exp` claim parsed from the token.                                                  |

## Requirements

Pulled in by the backend's `uv` workflow:

- `bcrypt` — password hashing.
- `PyJWT` — JWT encoding/decoding.
- `pydantic` — token models.

Install through the backend's standard setup:

```bash
cd backend
uv sync
```

## Usage

### Hashing and verifying passwords

`PasswordService` is intended to be called as a static utility — no instantiation needed. `hash_password` generates a fresh salt on every call, so the same plaintext produces different digests; always use `check_password` for comparison rather than re-hashing and comparing strings.

```python
from reader.services.auth import PasswordService

hashed = PasswordService.hash_password("correct horse battery staple")

PasswordService.check_password("correct horse battery staple", hashed)  # True
PasswordService.check_password("wrong password", hashed)                # False
```

### Issuing a JWT for a logged-in user

`JWTTokenService` is constructed with the symmetric signing key and (optionally) the JWA algorithm. `generate_token` embeds the supplied `user_id` and an expiry one day in the future, and returns an `AccessToken`.

```python
from reader.services.auth import JWTTokenService

jwt_service = JWTTokenService(secret_key="replace-with-app-secret", algorithm="HS256")

access_token = jwt_service.generate_token(user_id=42)

print(access_token.token)       # signed JWT string
print(access_token.expires_at)  # tz-aware datetime, 24h from issue time
```

### Decoding and verifying an incoming token

`decode_token` verifies the signature and expiry by default and returns `JWTTokenMetadata`. Expired tokens raise `jwt.ExpiredSignatureError`; otherwise invalid tokens raise other `PyJWTError` subclasses.

```python
from jwt.exceptions import ExpiredSignatureError, PyJWTError

from reader.services.auth import JWTTokenService

jwt_service = JWTTokenService(secret_key="replace-with-app-secret")

try:
    metadata = jwt_service.decode_token(incoming_token)
except ExpiredSignatureError:
    ...  # 401 — token expired
except PyJWTError:
    ...  # 401 — malformed or bad signature
else:
    user_id = metadata.user_id
    expires_at = metadata.exp
```

Pass `verify_signature=False` to inspect a token's claims without validating the signature (useful for debugging — never trust the result in a security-sensitive code path):

```python
metadata = jwt_service.decode_token(incoming_token, verify_signature=False)
```

### End-to-end: login flow

A typical login endpoint loads the user, verifies the password against the stored hash, and issues a JWT:

```python
from reader.services.auth import JWTTokenService, PasswordService

user = await user_dao.get_by_username(username)

if not PasswordService.check_password(plaintext_password, user.password):
    raise HTTPException(status_code=401, detail="Invalid username or password")

jwt_service = JWTTokenService(
    secret_key=config.services.auth.jwt_secret_key.get_secret_value(),
    algorithm=config.services.auth.jwt_algorithm,
)
access_token = jwt_service.generate_token(user.id)

return {"access_token": access_token.token, "expires_at": access_token.expires_at}
```

The corresponding `Authorization: Bearer <token>` header is consumed by the `user_authorized` FastAPI dependency in `modules/middlewares/dependencies/user_authorized.py`, which calls `decode_token` and loads the matching `User` row.

## Notes

- The signing secret and algorithm are read from `AppConfig.services.auth` (`jwt_secret_key`, `jwt_algorithm`) — instantiate `JWTTokenService` from config rather than hard-coding a key.
- Token lifetime is fixed at one day inside `generate_token`; change it there if a different expiry policy is required.
- `PasswordService.hash_password` uses `bcrypt.gensalt()` with library defaults — the cost factor is not configurable from outside the service.
- `decode_token` always enforces `verify_exp=True`, so callers do not need to re-check the expiry against the current time.
