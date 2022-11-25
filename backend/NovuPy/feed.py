import httpx

from .settings import Core


class Feed(Core):
    """
    Track feed by passing {'name': name} 

    Example Response:

    {
        _id: "_id",
        name: "name",
        identifier: "identifier",
        _environmentId: "_environmentId",
        _organizationId: "_organizationId"
    }
    """

    async def get_feeds(self):
        """
        Get feed
        """
        url = self.base_url+'/feeds'

        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=self.s_header)

        return response.json()

    async def create_feed(self, data=None):
        """
        Create Feed
        """
        url = self.base_url+'/feeds'

        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=self.header, data=data)

        return response.json()

    async def delete_feed(self, feed_id):
        """
        Create Feed
        """
        url = self.base_url+f'/feeds/{feed_id}'

        async with httpx.AsyncClient() as client:
            response = await client.delete(url=url, headers=self.header)

        return response.json()
