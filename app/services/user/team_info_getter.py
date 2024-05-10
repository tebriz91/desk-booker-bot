from typing import TYPE_CHECKING, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.orm_queries import (
    orm_select_team_id_by_telegram_id,
    orm_select_team_info_by_team_id,
)

if TYPE_CHECKING:
    from app.locales.stub import TranslatorRunner # type: ignore


async def get_team_info_service(i18n, session: AsyncSession, telegram_id: int) -> Tuple[str, str] | Tuple[str, str, int]:
    """
    Get team information from the database.

    Returns:
        Tuple[str, str]: A tuple containing the status and response message
        or
        Tuple[str, str, int]: A tuple containing the status, response message and team_id
    """
    i18n: TranslatorRunner = i18n
    team_id = await orm_select_team_id_by_telegram_id(session, telegram_id)
    if not team_id:
        #! team-empty
        return "empty", i18n.team.empty()
    
    team_info = await orm_select_team_info_by_team_id(session, team_id)
    if not team_info:
        #! team-no-info
        return "no-info", i18n.team.no.info()

    team_name = team_info[0].team_name
    room_name = team_info[0].room_name
    
    # Iterate over the team_info to get the user_name and role of each user in the team and add it to the response message
    #! team-name & team-room-name
    response_message: str = i18n.team.name(team_name=team_name) + '\n\n' + i18n.team.room.name(room_name=room_name) + '\n\n'
    for item in team_info:
        #! team-member-info
        response_message += i18n.team.member.info(telegram_name=f'@{item.user_name}', role=item.role) + '\n'
    return "team-info", response_message, team_id