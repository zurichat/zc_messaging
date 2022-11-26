import httpx

from .settings import Core


class Activity(Core):

    async def get_activity(self, **kwargs):
        """
        Get activity feed

        A page query parameter can be passed into the function to paginate response e.g page = 2  
        Example response:

        {
            totalCount: 0,
            data: ["data"],
            pageSize: 0,
            page: 0
        }

        """
        url = self.base_url+'/activity'

        async with httpx.AsyncClient() as requests:
            response = await requests.get(url=url, headers=self.s_header, params=kwargs)

        return response.json()

    async def get_activity_stats(self):
        """
        Get activity statistics

        Example response:
        {
            weeklySent: 0,
            monthlySent: 0,
            yearlySent: 0
        }
        """
        url = self.base_url+'/activity/stats'
        async with httpx.AsyncClient() as requests:
            response = await requests.get(url=url, headers=self.s_header)

        return response.json()
