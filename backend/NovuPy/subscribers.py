import httpx
from fastapi import HTTPException, status

from .settings import Core


class Subscribers(Core):

    async def list(self, page=None):
        """
        Returns a list of subscribers, could be paginated using the `page` query parameter
        """
        url = self.base_url + \
            f'/subscribers?page={page}' if page else self.base_url + \
            f'/subscribers'

        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=self.s_header)

        return response.json()

    async def identify(self, user_id, data=None):
        """
        Creates a subscriber entity, in the Novu platform. 
        The subscriber will be later used to receive notifications, and access notification feeds.

        A user_id must be passed, so that a correlating subscriberId will be created in Novu

        This function will only create a Subscriber if it does not exist already

        Sample data:


        {
            subscriberId: user.id
            email: user.email,
            firstName: user.firstName,
            lastName: user.lastName,
            phone: user.phone,
            avatar: user.profile_avatar
        }

        Response:

        {
            _id: "_id",
            firstName: "firstName",
            lastName: "lastName",
            email: "email",
            phone: "phone",
            avatar: "avatar",
            subscriberId: "subscriberId",
            channels: ["channels"],
            _organizationId: "_organizationId",
            _environmentId: "_environmentId",
            deleted: true,
            createdAt: "createdAt",
            updatedAt: "updatedAt",
            __v: 0
        }

        """

        url = self.base_url + '/subscribers'

        if not data:
            data = {}

        try:
            data['subscriberId'] = str(user_id)

        except KeyError:
            pass

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url=url, headers=self.headers, data=data)
            return response.json()

        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Could not subscribe user")

    async def get_subscriber(self, subscriber_id):
        """
        Get subscriber by your internal id used to identify the subscriber
        """

        url = self.base_url + f'/subscribers/{subscriber_id}'

        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=self.s_header)

        return response.json()

    async def update_subscriber(self, subscriber_id, data=None):
        """
        Used to update the subscriber entity with new information
        """

        url = self.base_url + f'/subscribers/{subscriber_id}'

        async with httpx.AsyncClient() as client:
            response = await client.put(url=url, headers=self.headers, data=data)

        return response.json()

    async def delete_subscriber(self, subscriber_id):
        """
        Deletes a subscriber entity from the Novu platform
        """

        url = self.base_url + f'/subscribers/{subscriber_id}'

        async with httpx.AsyncClient() as client:
            response = await client.delete(url=url, headers=self.headers)

        return response.json()

    async def update_subscriber_credentials(self, subscriber_id, data=None):
        """
        Subscriber credentials associated to the delivery methods such as slack and push tokens.
        """
        url = self.base_url + f'/subscribers/{subscriber_id}/credentials'

        async with httpx.AsyncClient() as client:
            response = await client.put(url=url, headers=self.headers, data=data)

        return response.json()

    async def get_subscriber_preferences(self, subscriber_id):
        """
        Get subscriber preferences
        """
        url = self.base_url + f'/subscribers/{subscriber_id}/preferences'

        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=self.s_header)

        return response.json()

    async def update_subscriber_preferences(self, subscriber_id, template_id, data=None):
        """
        Update subscriber preference
        """

        url = self.base_url + \
            f'/subscribers/{subscriber_id}/preferences/{template_id}'

        async with httpx.AsyncClient() as client:
            response = await client.patch(url=url, headers=self.headers, data=data)

        return response.json()

    async def get_notifications_feed(self, subscriber_id, **kwargs):
        """
        Get a notification feed for a particular subscriber
        """
        url = self.base_url + \
            f'/subscribers/{subscriber_id}/notifications/feed'

        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=self.s_header)

        return response.json()

    async def get_unseen_notifications_count(self, subscriber_id, **kwargs):
        """
        Get the unseen notification count for subscribers feed
        """

        url = self.base_url + \
            f'/subscribers/{subscriber_id}/notifications/unseen'

        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=self.s_header)

        return response.json()

    async def mark_message_seen(self, subscriber_id, message_id):

        """
        Mark a subscriber feed message as seen
        """
        url = self.base_url + \
            f'subscribers/{subscriber_id}/messages/{message_id}/seen'

        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=self.s_header)

        return response.json()

    async def mark_action_seen(self, subscriber_id, message_id, type):
        """
        Mark message action as seen
        """
        url = self.base_url + \
            f'subscribers/{subscriber_id}/messages/{message_id}/actions/{type}'

        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=self.s_header)

        return response.json()
