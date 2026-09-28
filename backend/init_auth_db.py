from app.core.database import Base, engine
from app.models.user import User

Base.metadata.create_all(
    bind=engine
)

print("DeepVerify-X authentication database initialized.")
print("Users table is ready.")