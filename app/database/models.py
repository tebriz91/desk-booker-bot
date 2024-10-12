import enum
from sqlalchemy import Date, DateTime, Enum, ForeignKey, BigInteger, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.database.enums.user_roles import UserRole
from app.database.enums.weekdays import Weekday


class Base(DeclarativeBase):
    # type_annotation_map = {
    #     enum.Enum: Enum(enum.Enum, inherit_schema=True),
    # }
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    repr_cols_num = 3 # Number of columns to include in the __repr__ method
    repr_cols: tuple = tuple()
    
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
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_name: Mapped[str] = mapped_column(String(32), unique=True)
    first_name: Mapped[str | None] = mapped_column(String(32))
    last_name: Mapped[str | None] = mapped_column(String(32))
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_banned: Mapped[bool] = mapped_column(default=False)
    is_out_of_office: Mapped[bool] = mapped_column(default=False)


class UserRoleAssignment(Base):
    __tablename__ = 'user_role_assignments'

    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id', ondelete='CASCADE'), primary_key=True, autoincrement=False)
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id', ondelete='CASCADE'))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name='userrole'), default=UserRole.Member)

    user: Mapped['User'] = relationship(backref='user_role_assignments')
    team: Mapped['Team'] = relationship(backref='user_role_assignments')


class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), unique=True)
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id', ondelete='SET NULL'))

    room: Mapped['Room'] = relationship(backref='teams')


class TeamTree(Base):
    __tablename__ = 'team_tree'

    parent_team_id: Mapped[int] = mapped_column(ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True)
    child_team_id: Mapped[int] = mapped_column(ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True)

    parent_team: Mapped['Team'] = relationship(
        foreign_keys=[parent_team_id],
        backref='child_teams',
    )
    child_team: Mapped['Team'] = relationship(
        foreign_keys=[child_team_id],
        backref='parent_teams',
    )
    
    __table_args__ = (
        UniqueConstraint('parent_team_id', 'child_team_id', name='uq_team_tree'),
    )


class Waitlist(Base):
    __tablename__ = 'waitlist'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    telegram_name: Mapped[str] = mapped_column(String(32), unique=True)
    first_name: Mapped[str | None] = mapped_column(String(32))
    last_name: Mapped[str | None] = mapped_column(String(32))


class Room(Base):
    __tablename__ = 'rooms'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), unique=True)
    is_available: Mapped[bool] = mapped_column(default=True)
    plan: Mapped[str | None] = mapped_column(String(255)) # url to the room plan


class Desk(Base):
    __tablename__ = 'desks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), unique=True)
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id', ondelete='CASCADE')) # ondelete='CASCADE' means that if the room is deleted, all the desks in it will be deleted as well
    is_available: Mapped[bool] = mapped_column(default=True)

    room: Mapped['Room'] = relationship(backref='desks') # This relationship is used to access the room of the desk, e.g. desk.room


class DeskAssignment(Base):
    __tablename__ = 'desk_assignments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id', ondelete='CASCADE'))
    desk_id: Mapped[int] = mapped_column(ForeignKey('desks.id', ondelete='CASCADE'))
    weekday: Mapped[Weekday] = mapped_column(Enum(Weekday, name='weekday'))
    
    user: Mapped['User'] = relationship(backref='desk_assignments')
    desk: Mapped['Desk'] = relationship(backref='desk_assignments')

    __table_args__ = (
        # A desk cannot be assigned to more than one user on the same weekday.
        UniqueConstraint('desk_id', 'weekday', name='uq_desk_weekday'),
        # A user cannot be assigned more than one desk on the same weekday.
        UniqueConstraint('telegram_id', 'weekday', name='uq_telegram_id_weekday'),
    )


class Booking(Base):
    __tablename__ = 'bookings'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id', ondelete='CASCADE'))
    desk_id: Mapped[int] = mapped_column(ForeignKey('desks.id', ondelete='CASCADE'))
    date: Mapped[Date]= mapped_column(Date) # format: "YYYY-MM-DD"
    
    user: Mapped['User'] = relationship(backref='bookings')
    desk: Mapped['Desk'] = relationship(backref='bookings')
    
    __table_args__ = (
        # A desk cannot be booked by more than one user on the same date.
        UniqueConstraint('desk_id', 'date', name='uq_desk_id_date'),
        # A user cannot book more than one desk on the same date.
        UniqueConstraint('telegram_id', 'date', name='uq_telegram_id_date'),
    )
