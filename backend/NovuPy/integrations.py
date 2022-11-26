import httpx

from .settings import Core


class Integration(Core):

    """
    Create Integrations such as Email, SMS, Push ...etc
    by passing ...

    {
      "providerId": "providerId",
      "channel": "channel",
      "credentials": credentials,
      "active": true
    }

    channel - indicate the channel to integrate(Email, SMS, Push ...etc)
    credentials - necessary parameters to enbale connection should be provided in the credentials e.g API_KEY of the provider

    Example Response:

    {
        _id: "_id",
        _environmentId: "_environmentId",
        _organizationId: "_organizationId",
        providerId: "providerId",
        channel: "channel",
        credentials: credentials,
        active: true,
        deleted: true,
        deletedAt: "deletedAt",
        deletedBy: "deletedBy"
    }
    """

    async def get_integrations(self):
        """
        Get integrations
        """
        url = self.base_url+'/integrations'

        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=self.s_header)

        return response.json()

    async def get_active(self):
        """
        Get active integrations
        """
        url = self.base_url+'/integrations/active'

        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=self.s_header)

        return response.json()

    async def create(self, data=None):
        """
        Create integration
        """
        url = self.base_url+'/integrations'

        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=self.headers, data=data)

        return response.json()

    async def update(self, id, data=None):
        """
        Update integration
        """
        url = self.base_url+f'/integrations/{id}'

        async with httpx.AsyncClient() as client:
            response = await client.put(url=url, headers=self.headers, data=data)

        return response.json()

    async def delete(self, id):
        """
        Delete integration
        """
        url = self.base_url+f'/integrations/{id}'

        async with httpx.AsyncClient() as client:
            response = await client.delete(url=url, headers=self.s_header)

        return response.json()
