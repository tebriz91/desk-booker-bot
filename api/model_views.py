from sqladmin import ModelView
from wtforms import DateTimeField # type: ignore
from wtforms.validators import Optional # type: ignore
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
    form_include_pk = True
    
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
        "created_at": DateTimeField("Created At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
        "updated_at": DateTimeField("Updated At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
    }

    column_searchable_list = [
        User.telegram_id,
        User.telegram_name,
        User.first_name,
        User.last_name,
    ]
    
    column_sortable_list = [
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

    column_default_sort = "telegram_id"


class UserRoleAssignmentAdmin(ModelView, model=UserRoleAssignment):
    form_include_pk = True
    
    column_list = [
        UserRoleAssignment.telegram_id,
        UserRoleAssignment.team_id,
        UserRoleAssignment.role,
    ]

    form_columns = [
        "telegram_id",
        "team_id",
        "role",
    ]
    
    form_extra_fields = {
        "created_at": DateTimeField("Created At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
        "updated_at": DateTimeField("Updated At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
    }
    
    column_searchable_list = [
        UserRoleAssignment.telegram_id,
        UserRoleAssignment.team_id,
        UserRoleAssignment.role,
    ]

    column_sortable_list = [
        UserRoleAssignment.telegram_id,
        UserRoleAssignment.team_id,
        UserRoleAssignment.role,
    ]

    column_default_sort = "team_id"
    

class TeamAdmin(ModelView, model=Team):
    form_include_pk = True
    
    column_list = [
        Team.id,
        Team.name,
        Team.room_id,
        Team.created_at,
        Team.updated_at,
    ]

    form_columns = [
        "name",
        "room_id",
    ]
    
    form_extra_fields = {
        "created_at": DateTimeField("Created At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
        "updated_at": DateTimeField("Updated At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
    }

    column_searchable_list = [
        Team.id,
        Team.name,
        Team.room_id,
    ]
    
    column_sortable_list = [
        Team.id,
        Team.name,
        Team.room_id,
        Team.created_at,
        Team.updated_at,
    ]
    
    column_default_sort = "name"


class TeamTreeAdmin(ModelView, model=TeamTree):
    form_include_pk = True
    
    column_list = [
        TeamTree.parent_team_id,
        TeamTree.child_team_id,
        TeamTree.created_at,
        TeamTree.updated_at,
    ]

    form_columns = [
        "parent_team_id",
        "child_team_id",
    ]

    form_extra_fields = {
        "created_at": DateTimeField("Created At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
        "updated_at": DateTimeField("Updated At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
    }
    
    column_searchable_list = [
        TeamTree.parent_team_id,
        TeamTree.child_team_id,
    ]
    
    column_sortable_list = [
        TeamTree.parent_team_id,
        TeamTree.child_team_id,
        TeamTree.created_at,
        TeamTree.updated_at,
    ]
    
    column_default_sort = "parent_team_id"
    

class WaitlistAdmin(ModelView, model=Waitlist):
    form_include_pk = True
    
    column_list = [
        Waitlist.telegram_id,
        Waitlist.telegram_name,
        Waitlist.first_name,
        Waitlist.last_name,
        Waitlist.created_at,
        Waitlist.updated_at,
    ]

    form_columns = [
        "telegram_id",
        "telegram_name",
        "first_name",
        "last_name",
    ]
    
    form_extra_fields = {
        "created_at": DateTimeField("Created At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
        "updated_at": DateTimeField("Updated At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
    }
    
    column_searchable_list = [
        Waitlist.telegram_id,
        Waitlist.telegram_name,
        Waitlist.first_name,
        Waitlist.last_name,
    ]
    
    column_sortable_list = [
        Waitlist.telegram_id,
        Waitlist.telegram_name,
        Waitlist.first_name,
        Waitlist.last_name,
        Waitlist.created_at,
        Waitlist.updated_at,
    ]
    
    column_default_sort = "telegram_id"
    

class RoomAdmin(ModelView, model=Room):
    form_include_pk = True
    
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

    column_searchable_list = [
        Room.id,
        Room.name,
        Room.is_available,
        Room.plan,
    ]
    
    column_sortable_list = [
        Room.id,
        Room.name,
        Room.is_available,
        Room.plan,
        Room.created_at,
        Room.updated_at,
    ]
    
    column_default_sort = "id"


class DeskAdmin(ModelView, model=Desk):
    form_include_pk = True
    
    column_list = [
        Desk.id,
        Desk.name,
        Desk.room_id,
        Desk.is_available,
        Desk.created_at,
        Desk.updated_at,
    ]

    form_columns = [
        "name",
        "room_id",
        "is_available",
    ]
    
    form_extra_fields = {
        "created_at": DateTimeField("Created At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
        "updated_at": DateTimeField("Updated At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
    }
    
    column_searchable_list = [
        Desk.id,
        Desk.name,
        Desk.room_id,
        Desk.is_available,
    ]
    
    column_sortable_list = [
        Desk.id,
        Desk.name,
        Desk.room_id,
        Desk.is_available,
        Desk.created_at,
        Desk.updated_at,
    ]
    
    column_default_sort = "room_id"
    

class DeskAssignmentAdmin(ModelView, model=DeskAssignment):
    form_include_pk = True
    
    column_list = [
        DeskAssignment.id,
        DeskAssignment.telegram_id,
        DeskAssignment.desk_id,
        DeskAssignment.weekday,
        DeskAssignment.created_at,
        DeskAssignment.updated_at,
    ]
    
    form_columns = [
        "telegram_id",
        "desk_id",
        "weekday",
    ]
    
    form_extra_fields = {
        "created_at": DateTimeField("Created At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
        "updated_at": DateTimeField("Updated At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
    }
    
    column_searchable_list = [
        DeskAssignment.id,
        DeskAssignment.telegram_id,
        DeskAssignment.desk_id,
        DeskAssignment.weekday,
    ]
    
    column_sortable_list = [
        DeskAssignment.id,
        DeskAssignment.telegram_id,
        DeskAssignment.desk_id,
        DeskAssignment.weekday,
        DeskAssignment.created_at,
        DeskAssignment.updated_at,
    ]
    
    column_default_sort = "telegram_id"


class BookingAdmin(ModelView, model=Booking):
    form_include_pk = True
    
    column_list = [
        Booking.id,
        Booking.telegram_id,
        Booking.desk_id,
        Booking.date,
        Booking.created_at,
        Booking.updated_at,
    ]
    
    form_columns = [
        "telegram_id",
        "desk_id",
        "date",
    ]
    
    form_extra_fields = {
        "created_at": DateTimeField("Created At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
        "updated_at": DateTimeField("Updated At", format='%Y-%m-%d %H:%M:%S', default=datetime.now, validators=[Optional()]),
    }
    
    column_searchable_list = [
        Booking.id,
        Booking.telegram_id,
        Booking.desk_id,
        Booking.date,
    ]
    
    column_sortable_list = [
        Booking.id,
        Booking.telegram_id,
        Booking.desk_id,
        Booking.date,
        Booking.created_at,
        Booking.updated_at,
    ]
    
    column_default_sort = "telegram_id"