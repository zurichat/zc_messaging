import httpx
from fastapi import HTTPException, status

from .settings import Core


class Events(Core):

    async def get_messages(self, **kwargs):
        """
        Returns a list of messages, could paginate using the `page` query parameter

        The query can be passed to the function as a dict---> {page: 3}

        Sample Response:
        {
            totalCount: 0,
            data: ["data"],
            pageSize: 0,
            page: 0
        }
        """
        url = self.base_url + f"/messages"

        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=self.s_header, params=kwargs)

        return response.json()

    async def delete_message(self, message_id):
        """
        Deletes a message entity from the Novu platform
        """
        url = self.base_url + f"/messages/{message_id}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url=url, headers=self.s_header)
        return response.json()

    async def trigger(self, event_name, data=None):
        """
        Trigger event is the main (and the only) way to send notification to subscribers. 
        The trigger identifier is used to match the particular template associated with it. 
        Additional information can be passed according the the body interface below.

        To make a trigger: 

            {
                "name": "Novu",   
                "payload": {                      
                    "test": "test"
                },
                "to": {
                        subscriberId: "<USER_IDENTIFIER>",
                        email: "email@email.com",
                        firstName: "John",
                        lastName: "Doe",
                }, 
                "transactionId": "transactionId"  
            }


        name - #This refers to the name of the notification template you intend to use
        payload - # The payload object is used to pass additional custom information that could be used to render the template, 
                    or perform routing rules based on it. 
                  #This data will also be available when fetching the notifications feed from the API to display certain parts of the UI.


        to - # The recipients list of people who will receive the notification



        transactionId- #A unique identifier for this transaction, a UUID will be generated if not provided.



           Example response:

        {
            acknowledged: true,
            status: "status",
            transactionId: "transactionId"
        }

        """
        url = self.base_url + "/events/trigger"

        if not data:
            data = {}
        try:
            data["name"] = event_name

            async with httpx.AsyncClient() as client:
                response = await client.post(url=url, headers=self.headers, data=data)
            return response.json()

        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Something went wrong")

        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


    async def broadcast(self, event_name, data=None):
        """
        Trigger a broadcast event to all existing subscribers, could be used to send announcements, etc. 
        In the future could be used to trigger events to a subset of subscribers based on defined filters.
        """
        url = self.base_url + "/events/trigger/broadcast"

        if not data:
            data = {}
        try:
            data["name"] = event_name

            async with httpx.AsyncClient() as client:
                response = await client.post(url=url, headers=self.headers, data=data)

        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Something went wrong")

        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        return response.json()

    async def cancel_trigger(self, transaction_id):
        """
        Using a previously generated transactionId during the event trigger, 
        will cancel any active or pending workflows. 
        This is useful to cancel active digests, delays etc...
        """

        url = self.base_url + f"/events/trigger/{transaction_id}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url=url, headers=self.s_headers)

        return response.json()
