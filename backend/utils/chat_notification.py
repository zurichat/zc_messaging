from NovuPy.events import Events
from NovuPy.subscribers import Subscribers
from room_utils import get_room_members, get_room
from fastapi import HTTPException
from db import DataStorage

subscriber = Subscribers()
event = Events()

class Notification:
    """
    A class that handles the Novu instance message notification 
    trigger for Channels, DM and when user is tagged.
    This class is called after the message instance or object has been created
    """  


    async def tagged_user_trigger_create(
        self, message_obj
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
        get_tagged_users = message_obj.get("richUiData", " ")
        if get_tagged_users: 
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
                    DB =  DataStorage(organization_id=get_tagged_users['org_id'])
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
                sender_id = message_obj["sender_id"]
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
                payload['messageBody'] = new_message
                tagged_users = await event.trigger({
                    "name":"channel-message",
                    "payload": payload,
                    "to": tagged_users_list
                })
                if tagged_users['statusCode'] !=201:
                    raise HTTPException(
                        status_code=422, 
                        detail="Novu couldn't send notifications to tagged users"
                        )
                return tagged_users



    async def dm_subscriber_create(self, room_obj):
        """
        A function that subscribes a DM user to Novu
        Args:
            (i) room_obj -> Dict

        Raise:
            HTTP_422- when novu failed to create DM notification
            HTTP_400- when room object argument passed is invalid
        """
        org_id = room_obj.get("org_id", " ")
        if not room_obj or org_id:
            raise HTTPException(
                status_code=400, 
                detail="Room object data is invalid"
                )
        if room_obj['room_type'] != 'DM':
            raise HTTPException(
                status_code=400, 
                detail="This function is only for DM"
                )
        try:
            room_members = room_obj['room_members']
        except:
            raise HTTPException(
                status_code=400, 
                detail="room members can't be empty"
            )
        for member_id, value in room_members:
            # fetch user data from DB
            DB = DataStorage(organization_id=org_id)
            get_user_details = await DB.get_all_members()
            if not get_user_details:
                raise HTTPException(
                    status_code=404, 
                    detail="Organization has no member"
                )
            user_info = [
                user for user in get_user_details  if user['_id'] == member_id
                ]
            if not user_info:
                raise HTTPException(
                    status_code=404, 
                    detail="User data in this organization not found"
                )
            user_first_name = user_info[0]['first_name']
            user_last_name = user_info[0]['last_name']
            user_email = user_info[0]['email']
            # subscribe user to Novu for message notification
            create_subcriber = await subscriber.identify(
                member_id, {
                "email": user_email,
                "firstName": user_first_name,
                "lastName": user_last_name
                })
            if create_subcriber['statusCode'] !=201:
                raise HTTPException(
                status_code=422, 
                detail="User's Novu subscription failed"
                )
        return create_subcriber
        
        

    async def channel_subcriber_create(self, org_id, member_id):
        """
        A function that create the Novu's subscriber object for a room user
        Args:
            (i) org_id
            (ii) member_id
        Raise:
            HTTP_422- when novu failed to create subcription for channel users
        """
        if not member_id or org_id:
            raise HTTPException(
                status_code=400, 
                detail="ID argument required"
                )
        # fetch user data from DB
        DB = DataStorage(organization_id=org_id)
        get_user_details = await DB.get_all_members()
        if not get_user_details:
            raise HTTPException(
                status_code=404,
                detail="Organization doesn't have a member"
            )
        user_info = [
            user for user in get_user_details  if user['_id'] == member_id
            ]
        if not user_info:
            raise HTTPException(
                status_code=404, 
                detail="User data in this organization not found"
            )
        user_first_name = user_info[0]['first_name']
        user_last_name = user_info[0]['last_name']
        user_email = user_info[0]['email']
        # subscribe user to Novu for message notification
        create_subcriber = await subscriber.identify(member_id,{
            "email": user_email,
            "firstName": user_first_name,
            "lastName": user_last_name
            })
        if create_subcriber.status_code != 201:
            raise HTTPException(
                status_code=422, 
                detail="User Novu subscription failed"
                )
        return create_subcriber
        


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
            dm_trigger_create = await event.trigger({
                "name": 'direct-message',
                "payload": payload,
                "to": [member_id]
            })
            if dm_trigger_create['statusCode'] !=201:
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
        org_id = message_obj.get("org_id", '')
        room_id = message_obj.get("room_id", '')
        if not org_id or room_id or message_obj:
            raise HTTPException(
                status_code=400, 
                detail="Invalid data input"
                )
        try:
            message = message_obj['richUiData']['blocks'][0]['text']
            sender_id = message_obj["sender_id"]
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
            if dm_notification['statusCode'] !=201:
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
        DB = DataStorage(organization_id=org_id)
        
        room_members = await DB.get_all_members()
        if not room_members:
            raise HTTPException(
                status_code=404, 
                detail="Organization doesn't have a member"
            )

        get_sender_details = [
            user for user in room_members  if user['_id'] == member_id
            ]
        sender_firstname = get_sender_details[0]['first_name']
        sender_lastname = get_sender_details[0]['last_name']
        payload['senderName'] = sender_firstname + ' ' + sender_lastname
        payload['messageBody'] = message
        get_members = await get_room_members(org_id, room_id)
        for member_id, value in get_members.items():
            if member_id == sender_id:
                del get_members[member_id]
            room_member_list.append(member_id)
         # send a message notification to every user in either in the channel
         #  or Group DM by calling the Novu trigger method
        channel_or_group_msg_notification = await event.trigger({
            "name":'channel-message',
            "payload": payload,
            "to": room_member_list
            })
        # raise an http exception if novu fails to send message notification
        # to group DM or channel room members
        if channel_or_group_msg_notification["acknowledged"] != "true":
            raise HTTPException(
                status_code=422, 
                detail="Message notification failed"
                )
        # send notification to tagged users if there's any
        tagged_message = message_obj.get("richUiData", '')
        if tagged_message:
            get_tagged_users = tagged_message['entityMap']
            if get_tagged_users !=[]:
                notify_tagged_users = await self.tagged_user_trigger_create(
                    message_obj
                    )
            # raise an http exception if novu fails to send message notification
            # to tagged users
            if notify_tagged_users["acknowledged"] != "true":
                raise HTTPException(
                    status_code=422, 
                    detail="failed to create a DM notification"
                    )
        return channel_or_group_msg_notification
        


