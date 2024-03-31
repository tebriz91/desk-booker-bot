from typing import List, Optional, Union
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import (
    orm_select_available_desks_by_room_name,
    orm_select_room_id_by_name,
    orm_select_available_not_assigned_desks_by_room_id,
    orm_select_user_team_id,
    orm_select_team_preffered_room_id,
    orm_select_available_not_booked_desks_by_room_id,
)
from database.enums.weekdays import Weekday

from utils.logger import Logger

logger = Logger()


async def generate_available_desks_list(session: AsyncSession, room_name: str) -> List[str]:
    desks_orm_obj = await orm_select_available_desks_by_room_name(session, room_name)
    return [desk.name for desk in desks_orm_obj]

async def generate_available_not_booked_desks_list(
    session: AsyncSession,
    room_name: str,
    date: str,
    date_format: str,
    advanced_mode: Optional[bool],
    telegram_id: Optional[int],
    standard_access_days: Optional[int] = 1,
    ) -> Union[List[str], str]:
    desks: List[str] = []
    
    # Convert date string to date object
    try:
        booking_date = datetime.strptime(date, date_format).date()
    except ValueError:
        return f"Error: Incorrect date format. Parsing date to datetime.date failed."
    
    today = datetime.now().date()
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Today: {today}")
    weekday = booking_date.weekday()  # This will be an integer from 0 to 6
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Weekday: {weekday}")
    days_difference = (booking_date - today).days
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Days difference: {days_difference}")
    # Fetch the room ID based on room name
    room_id = await orm_select_room_id_by_name(session, room_name)
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Room ID: {room_id}")
    
    # Retrieve desks from the selected room, which are not assigned to any user on the selected weekday
    try:
        not_assigned_desks = await orm_select_available_not_assigned_desks_by_room_id(session, room_id, weekday)
        logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Not assigned desks: {not_assigned_desks}")
    except Exception as e:
        return f"Error retrieving not assigned desks: {e}"
    
    # If advanced mode is enabled, retrieve user's team_id, than check if this team has a preffered room, than check if selected room is the same as preffered room. If yes, return desks from this room. If not, check if standard access days equals or less than number of days between today and booking date. If yes, return desks from selected room. If not, return empty list.
    
    try:
        not_booked_desks_obj = await orm_select_available_not_booked_desks_by_room_id(session, room_id, booking_date)
        not_booked_desks = [desk.name for desk in not_booked_desks_obj]
        logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Not booked desks: {not_booked_desks}")
    except Exception as e:
        return f"Error retrieving not booked desks: {e}"
    
    try:
        
        if not advanced_mode:
            desks = list(set(not_assigned_desks) & set(not_booked_desks))
            logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Desks (in basic mode - service level): {desks}")
            return desks
        
        if advanced_mode and telegram_id:
            # Fetch user's team ID
            team_id = await orm_select_user_team_id(session, telegram_id)
            logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Advanced mode. Team ID: {team_id}")
            
            if not team_id and days_difference > standard_access_days:
                logger.info(f">>>>>>>>>>>>>>>>>>>>>>>No team ID and days difference > standard access days, desks: {desks}")
                return desks
            
            if not team_id and days_difference <= standard_access_days:
                desks = list(set(not_assigned_desks) & set(not_booked_desks))
                logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Desks (not team_id and days_difference <= standard_access_days): {desks}")
                return desks
            
            if team_id:
                # Fetch team's preffered room
                preffered_room_id = await orm_select_team_preffered_room_id(session, team_id)
                logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Preffered room ID: {preffered_room_id}")
                
                if preffered_room_id and preffered_room_id != room_id and days_difference > standard_access_days:
                    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Preffered room ID != room ID and days difference > standard access days")
                    return desks
                
                if preffered_room_id and preffered_room_id != room_id and days_difference <= standard_access_days:
                    desks = list(set(not_assigned_desks) & set(not_booked_desks))
                    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Desks (if preffered_room_id and preffered_room_id != room_id and days_difference <= standard_access_days): {desks}")
                    return desks
                
                if preffered_room_id and preffered_room_id == room_id:
                    desks = list(set(not_assigned_desks) & set(not_booked_desks))
                    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Desks (if preffered_room_id and preffered_room_id == room_id): {desks}")
                    return desks
    
    except Exception as e:
        return f"Error: {e}"
    
    return desks