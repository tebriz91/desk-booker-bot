from sqladmin import ModelView
from wtforms import DateTimeField, IntegerField
from wtforms.validators import DataRequired, Optional
from datetime import datetime
from app.database.models import (
    User,
    UserRoleAssignment,
    Team,
    TeamTree,
    Waitlist,
    Room,
    Desk,
    DeskAssignment,
    Booking,
)


class UserAdmin(ModelView, model=User):
    column_list = [
        User.telegram_id,
        User.telegram_name,
        User.first_name,
        User.last_name,
        User.is_admin,
        User.is_banned,
        User.is_out_of_office,
        User.created_at,
        User.updated_at,
    ]

    form_columns = [
        "telegram_id",
        "telegram_name",
        "first_name",
        "last_name",
        "is_admin",
        "is_banned",
        "is_out_of_office",
    ]

    form_extra_fields = {
        # "telegram_id": IntegerField("Telegram ID", validators=[DataRequired()]),
        "created_at": DateTimeField("Created At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
        "updated_at": DateTimeField("Updated At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
    }


class UserRoleAssignmentAdmin(ModelView, model=UserRoleAssignment):
    column_list = [
        UserRoleAssignment.telegram_id,
        UserRoleAssignment.team_id,
        UserRoleAssignment.role,
    ]


class TeamAdmin(ModelView, model=Team):
    column_list = [
        Team.id,
        Team.name,
        Team.room_id,
        Team.created_at,
        Team.updated_at,
    ]


class TeamTreeAdmin(ModelView, model=TeamTree):
    column_list = [
        TeamTree.parent_team_id,
        TeamTree.child_team_id,
        TeamTree.created_at,
        TeamTree.updated_at,
    ]


class WaitlistAdmin(ModelView, model=Waitlist):
    column_list = [
        Waitlist.telegram_id,
        Waitlist.telegram_name,
        Waitlist.first_name,
        Waitlist.last_name,
        Waitlist.created_at,
        Waitlist.updated_at,
    ]


class RoomAdmin(ModelView, model=Room):
    column_list = [
        Room.id,
        Room.name,
        Room.is_available,
        Room.plan,
        Room.created_at,
        Room.updated_at,
    ]

    form_columns = [
        "name",
        "is_available",
        "plan",
    ]
    
    form_extra_fields = {
        "created_at": DateTimeField("Created At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
        "updated_at": DateTimeField("Updated At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
    }


class DeskAdmin(ModelView, model=Desk):
    column_list = [
        Desk.id,
        Desk.name,
        Desk.room_id,
        Desk.is_available,
        Desk.created_at,
        Desk.updated_at,
    ]


class DeskAssignmentAdmin(ModelView, model=DeskAssignment):
    column_list = [
        DeskAssignment.id,
        DeskAssignment.telegram_id,
        DeskAssignment.desk_id,
        DeskAssignment.weekday,
        DeskAssignment.created_at,
        DeskAssignment.updated_at,
    ]


class BookingAdmin(ModelView, model=Booking):
    column_list = [
        Booking.id,
        Booking.telegram_id,
        Booking.desk_id,
        Booking.date,
        Booking.created_at,
        Booking.updated_at,
    ]