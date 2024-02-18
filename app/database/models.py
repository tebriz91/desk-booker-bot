from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    repr_cols_num = 3 # Number of columns to include in the __repr__ method
    repr_cols = tuple()
    
    # This method is used to represent the object as a string
    def __repr__(self):
        """Relationships are not included in the __repr__ method, because they can cause infinite recursion."""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    telegram_name: Mapped[str] = mapped_column(unique=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_banned: Mapped[bool] = mapped_column(default=False)
    additional_info: Mapped[str | None]

class Room(Base):
    __tablename__ = 'rooms'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    availability: Mapped[bool] = mapped_column(default=True)
    plan: Mapped[str | None] # url to the room plan
    additional_info: Mapped[str | None]

class Desk(Base):
    __tablename__ = 'desks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id'))
    availability: Mapped[bool] = mapped_column(default=True)
    additional_info: Mapped[str | None]

class Booking(Base):
    __tablename__ = 'bookings'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    desk_id: Mapped[int] = mapped_column(ForeignKey('desks.id'))
    date: Mapped[DateTime]= mapped_column(DateTime)