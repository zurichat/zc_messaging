from NovuPy.events import Events
from NovuPy.subscribers import Subscribers
from utils.room_utils import get_room_members, get_room
from fastapi import HTTPException
from utils.db import DataStorage
from config.settings import settings

subscriber = Subscribers()
event = Events()

class Notification:
    """
    A class that handles the Novu instance message notification 
    trigger for Channels, DM and when user is tagged.
    This class is called after the message instance or object has been created
    """  


    async def tagged_user_trigger_create(
        self, message_obj, room_name
        ):
        """
        A method that creates a notification trigger for tagged users
        Args:
            message_object-> Dict
            payload-> Dict: message data that should be passed to novu
            sender_id -> str
        Raise:
            HTTP_422- when Novu couldn't send notification to tagged users
        """
        tagged_users_list = []
        payload = {}
        message_data = dict(message_obj)
        get_tagged_users = message_data.get("richUiData", " ")
        org_id = message_data.get("org_id", '')
        if get_tagged_users: 
            DB =  DataStorage(organization_id=org_id)
            # get the text from the message object
            text_message = get_tagged_users['blocks'][0]['text']
            # from the text in the message text, get the characters without '@'
            get_text_msg = text_message.split(' ')
            message_text = [text for text in get_text_msg if text.isalnum()]
            new_message = " ".join(message_text)
            # check the message object to get the names of the tagged users
            user_msg_tag = get_tagged_users['entityMap']
            if user_msg_tag !=[]:
                for message in range(len(user_msg_tag)):
                    tagged_user_email = user_msg_tag[str(message)]['data']['mention']['link']
                    # get user details from DB
                    get_room_users = await DB.get_all_members()
                    if not get_room_users:
                        raise HTTPException(
                            status_code=404, 
                            detail="Organization doesn't have a member"
                        )
                    tagged_user = [
                        user for user in get_room_users if user['email'] == tagged_user_email
                        ]
                    tagged_users_list.append(tagged_user[0]['_id'])
                # use sender ID to fetch sender's data from the DB
                sender_id = message_data["sender_id"]
                get_sender_details = await DB.get_all_members()
                if not get_sender_details:
                        raise HTTPException(
                            status_code=404, 
                            detail="Sender ID doesn't exist"
                        )
                sender_info = [user for user in get_sender_details if user['_id'] == sender_id]
                sender_firstname = sender_info[0]['first_name']
                sender_lastname = sender_info[0]['last_name']
                sender_name = sender_firstname + ' ' + sender_lastname
                payload['senderName'] = sender_name
                payload['channelName'] = room_name
                payload['messageBody'] = new_message
                tagged_users = await event.trigger("channel-message",{
                    "payload": payload,
                    "to": tagged_users_list
                })
                tagged_user_notification_status = tagged_users.get("status", " ")
                if not tagged_user_notification_status:
                    raise HTTPException(
                        status_code=422, 
                        detail="Novu couldn't send notifications to tagged users"
                        )
                return tagged_users

        


    async def dm_message_trigger(self, org_id, room_id, sender_id, message):
        """
        A function that triggers a Novu notification instance 
        for DM room.
        Args:
            (i) org_id
            (ii) room_id
            (iii) sender_id
            (iv) message
        Raise:
            HTTP_422- when novu failed to create DM notification
        """
        payload = {}
        room = await get_room_members(org_id,room_id)
        if not room:
            return HTTPException(
                status_code=404,
                detail="Room with supplied ID not found"
            )
        DB = DataStorage(organization_id=org_id)
        get_all_members = await DB.get_all_members()
        if not get_all_members:
            raise HTTPException(
                status_code=404, 
                detail="Organization doesn't have a member"
            )
        sender_info = [
            user for user in get_all_members  if user['_id'] == sender_id
            ]
        if not sender_info:
            raise HTTPException(
                status_code=404, 
                detail="User with sender ID not found"
            )
        sender_firstname = sender_info[0]['first_name']
        sender_lastname = sender_info[0]['last_name']
        if not sender_lastname or sender_lastname:
            raise HTTPException(
                status_code=404,
                detail="Sender name field is empty"
            )
        #populate the payload dictionary    
        payload['senderName'] = sender_firstname + ' ' + sender_lastname
        payload['messageBody'] = message
        # create novu subscription for room members in the channel 
        # if none exist
        for member_id, values in room.items():
            if member_id == sender_id:
                del room[member_id]
            dm_trigger_create = await event.trigger('direct-message',{
                "payload": payload,
                "to": [member_id]
            })
            dm_trigger_create_statuscode = dm_trigger_create.get("status", " ")
            # if the novu response doesn't contain a status as a key, 
            # it means the novu instance failed 
            if not dm_trigger_create_statuscode:
                raise HTTPException(
                status_code=422, 
                detail="Novu couldn't create DM notification trigger"
                )
        return dm_trigger_create
        


    async def messages_trigger(self, message_obj):
        """
        A function that triggers a Novu notification instance for 
        users either in DM, channels, or Group DM excluding the sender.
        Args:
            (i) message object->Dict
        Raise:
            HTTP_422- when novu failed to create DM notification
        """
        payload = {}
        room_member_list = []
        message_data = dict(message_obj)
        org_id = message_data.get("org_id", '')
        room_id = message_data.get("room_id", '')
        DB = DataStorage(organization_id=org_id)
        query = {"_id": room_id}
        # get room data
        get_room_data = await DB.read(settings.ROOM_COLLECTION, query=query)
        if not get_room_data:
            raise HTTPException(
                status_code=404,
                detail="Room with supplied ID not found"
            )
        room_name = get_room_data["room_name"]
        try:
            message = message_data['richUiData']['blocks'][0]['text']
            sender_id = message_data["sender_id"]
        except:
            raise HTTPException(
                status_code=400, 
                detail="Invalid message input"
                )
        try:
            room = await get_room(org_id, room_id)
        except:
            raise HTTPException(
                status_code=404, 
                detail="room with ID not found"
                )
        # create a notfication for the DM user 
        if room['room_type'] == 'DM':
            dm_notification = await self.dm_message_trigger(
                org_id,room_id,sender_id, message
                )
            dm_notification_status_code = dm_notification.get("status", " ")
            # check the novu instance response to get the status code
            # this logic was used becuase if the novu operation fails,
            # it will return a statusCode as a key and if the operation 
            # is successful it returns status as a key.
            if not dm_notification_status_code:
                raise HTTPException(
                    status_code=422, 
                    detail="Failed to process Novu instance"
                    )
            if dm_notification["acknowledged"] != "true":
                raise HTTPException(
                status_code=422, 
                detail="failed to create a DM Novu instance"
                )
            return "dm notification trigger successful"
        # fetch sender data from DB 
        room_members = await DB.get_all_members()
        if not room_members:
            raise HTTPException(
                status_code=404, 
                detail="Organization doesn't have a member"
            )

        get_sender_details = [
            user for user in room_members  if user['_id'] == sender_id
            ]
        sender_firstname = get_sender_details[0]['first_name']
        sender_lastname = get_sender_details[0]['last_name']
        payload['senderName'] = sender_firstname + ' ' + sender_lastname
        payload['channelName'] = room_name
        payload['messageBody'] = message
        get_members = await get_room_members(org_id, room_id)
        for member_id in get_members.keys():
            if member_id != sender_id:
                room_member_list.append(member_id)
         # send a message notification to every user in either in the channel
         #  or Group DM by calling the Novu trigger method
        channel_or_group_msg_notification = await event.trigger('channel-message',{
            "payload": payload,
            "to": room_member_list
            })
        # raise an http exception if novu fails to send message notification
        # to group DM or channel room members
        channel_notification_status = channel_or_group_msg_notification.get("status", " ")
        if not channel_notification_status:
            raise HTTPException(
                status_code=422, 
                detail="Message notification failed"
                )
        # send notification to tagged users if there's any
        tagged_message = message_data.get("richUiData", '')
        if tagged_message:
            get_tagged_users = tagged_message['entityMap']
            if get_tagged_users !=[]:
                notify_tagged_users = await self.tagged_user_trigger_create(
                    message_obj, room_name
                    )
            # raise an http exception if novu fails to send message notification
            # to tagged users
            novu_status = notify_tagged_users.get("status", " ")
            if not novu_status :
                raise HTTPException(
                    status_code=422, 
                    detail="failed to create a DM notification"
                    )
        return channel_or_group_msg_notification
        


