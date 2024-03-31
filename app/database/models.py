from sqlalchemy import Date, DateTime, Enum, ForeignKey, BigInteger, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from database.enums.user_roles import UserRole
# from database.enums.weekdays import Weekday


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
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    telegram_name: Mapped[str] = mapped_column(unique=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_banned: Mapped[bool] = mapped_column(default=False)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    team_id: Mapped[int | None] = mapped_column(ForeignKey('teams.id', ondelete='SET NULL'))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.TeamMember)
    is_out_of_office: Mapped[bool] = mapped_column(default=False)
    additional_info: Mapped[str | None]

    team: Mapped['Team'] = relationship(backref='users')


class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id', ondelete='SET NULL'))

    room: Mapped['Room'] = relationship(backref='teams')


class Waitlist(Base):
    __tablename__ = 'waitlist'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    telegram_name: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    additional_info: Mapped[str | None]


class Room(Base):
    __tablename__ = 'rooms'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    is_available: Mapped[bool] = mapped_column(default=True)
    plan: Mapped[str | None] # url to the room plan
    additional_info: Mapped[str | None]


class Desk(Base):
    __tablename__ = 'desks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id', ondelete='CASCADE')) # ondelete='CASCADE' means that if the room is deleted, all the desks in it will be deleted as well
    is_available: Mapped[bool] = mapped_column(default=True)
    additional_info: Mapped[str | None]

    room: Mapped['Room'] = relationship(backref='desks') # This relationship is used to access the room of the desk, e.g. desk.room


class DeskAssignment(Base):
    __tablename__ = 'desk_assignments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    desk_id: Mapped[int] = mapped_column(ForeignKey('desks.id', ondelete='CASCADE'))
    
    user: Mapped['User'] = relationship(backref='desk_assignments')
    desk: Mapped['Desk'] = relationship(backref='desk_assignments')

class DeskAssignmentWeekday(Base):
    __tablename__ = 'desk_assignment_weekdays'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    desk_assignment_id: Mapped[int] = mapped_column(ForeignKey('desk_assignments.id', ondelete='CASCADE'), nullable=False)
    weekday: Mapped[int] = mapped_column(nullable=False)
    
    __table_args__ = (
        UniqueConstraint('desk_assignment_id', 'weekday', name='uq_desk_assignment_weekday'),
    )
    
    desk_assignment: Mapped['DeskAssignment'] = relationship(backref='desk_assignment_weekdays')


class Booking(Base):
    __tablename__ = 'bookings'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id', ondelete='CASCADE'), nullable=False)
    desk_id: Mapped[int] = mapped_column(ForeignKey('desks.id', ondelete='CASCADE'), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    date: Mapped[Date]= mapped_column(Date, nullable=False) # format: "YYYY-MM-DD"
    
    user: Mapped['User'] = relationship(backref='bookings')
    room: Mapped['Room'] = relationship(backref='bookings')
    desk: Mapped['Desk'] = relationship(backref='bookings')