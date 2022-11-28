from utils.db import DataStorage
from config.settings import settings

async def off_set(page: int, limit: int):
    return (page-1)*limit


async def page_urls(page: int, size: int, org_id : int, room_id: int, endpoint: str):

    DB = DataStorage(org_id)
    total_count = len(await DB.read(settings.MESSAGE_COLLECTION, query={"room_id": room_id}))

    paging = {}

    if (size + await off_set(page, size)) >= total_count:
        paging['next'] = None
    else:
        paging['next'] = f"{endpoint}?page={page+1}&size={size}"


    if page > 1:
        paging['previous'] = f"{endpoint}?page={page-1}&size={size}"
    else:
        paging['previous'] = None

    return paging, total_count