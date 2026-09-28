import bcrypt

from sqlalchemy.orm import Session

from app.models.user import User


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()

    hashed = bcrypt.hashpw(
        password_bytes,
        salt,
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def get_user_by_email(
    db: Session,
    email: str,
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def create_user(
    db: Session,
    email: str,
    password: str,
):
    password_hash = hash_password(password)

    user = User(
        email=email.lower().strip(),
        password_hash=password_hash,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user