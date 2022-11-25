from NovuPy.events import Events
from NovuPy.subscribers import Subscribers
from utils.room_utils import get_room_members, get_room
from fastapi import HTTPException

subscriber = Subscribers()
event = Events()

class Notification:
    """
    A class that handles the Novu instance message notification 
    trigger for Channels, DM and when user is tagged.
    This class is called after the message instance or object has been created
    """  

    async def check_message_tag(
        self, message_obj, payload, 
        sender_id
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
        tagged_users = []
        # user_msg_tag = message_obj["richUiData"]['entityMap']
        user_msg_tag = message_obj.get("entityMap", " ")
        if user_msg_tag:
            for i in range(len(user_msg_tag)):
                member_id = user_msg_tag[str(i)]['data']['mention']['member_id']
                if member_id == sender_id:
                    del i[member_id]
                tagged_users.append(member_id)
            dm_trigger_create = await event.trigger(
                'you-have-been-mentioned',
                {
                    "to": tagged_users,
                    "payload": payload
                })
            if dm_trigger_create['statusCode'] !=201:
                raise HTTPException(
                    status_code=422, 
                    detail="Novu couldn't send notifications to tagged users"
                    )
            return dm_trigger_create



    async def dm_subscriber_create(self, room_obj):
        """
        A function that subscribes a DM user to Novu
        Args:
            (i) room_obj -> Dict

        Raise:
            HTTP_422- when novu failed to create DM notification
            HTTP_400- when room object argument passed is invalid
        """
        if not room_obj:
            return ValueError("Room object data is invalid")
        if room_obj['room_type'] != 'DM':
            # i would love to break out of the function if type not a DM
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
            create_subcriber = await subscriber.identify(member_id)
            if create_subcriber['statusCode'] !=201:
                raise HTTPException(
                status_code=422, 
                detail="Novu couldn't create a Novu subscription for Novu"
                )
        return create_subcriber
        
        

    async def channel_subcriber_create(self, member_id):
        """
        A function that create the Novu's subscriber object for a room user
        Args:
            (i) org_id
            (ii) room_id
            (iii) sender_id
            (iv) message
        Raise:
            HTTP_422- when novu failed to create subcription for channel users
        """
        if not member_id:
            raise HTTPException(status_code=400, detail="member ID invalid")
        create_subcriber = await subscriber.identify(member_id)
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
        room = get_room_members(org_id,room_id)
        if not room:
            return ValueError(
                "Room not found"
            )
         #populate the payload dictionary    
        payload['sender'] = sender_id
        payload['message'] = message
        # create novu subscription for room members in the channel 
        # if none exist
        for member_id, values in room.items():
            if member_id == sender_id:
                del room[member_id]
            dm_trigger_create = await event.trigger(
                '<REPLACE_WITH_EVENT_NAME_FROM_ADMIN_PANEL>',
                {
                    "to": {
                    "subscriberId": member_id
                    },
                    "payload": payload
                    })
            if dm_trigger_create['statusCode'] !=201:
                raise HTTPException(
                status_code=422, 
                detail="Novu couldn't create DM notification trigger"
                )
        return dm_trigger_create
        


    async def channel_messages_trigger(self, message_obj):
        """
        A function that triggers a Novu notification instance 
        for every user in a room exclding the sender.
        Args:
            (i) message object->Dict(The message instance in the room)
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
            message = message_obj['data']['blocks'][0]['text']
            sender_id = message_obj.get("sender_id")
        except:
            pass
        room = get_room(org_id, room_id)
        if not room:
            return ValueError("room with ID not found")
        # create a notfication for the DM user 
        if room['roomt_type'] == 'DM':
            dm_create = self.dm_message_trigger(org_id,room_id,sender_id)
            if dm_create['statusCode'] !=201:
                raise HTTPException(
                    status_code=422, 
                    detail="Failed to process Novu instance"
                    )
            if dm_create["acknowledged"] != "true":
                raise HTTPException(
                status_code=422, 
                detail="failed to create a DM Novu instance"
                )
            return "dm notification trigger successful"
        payload['message'] = message
        payload['message'] = sender_id
        # send a message notification to every user in a room by 
        # calling the Novu trigger method
        get_members = get_room_members(org_id, room_id)
        for member_id, value in get_members.items():
            if member_id == sender_id:
                del get_members[member_id]
            room_member_list.append(member_id)
        channel_or_group_msg_trigger_crate = await event.trigger(
            '<REPLACE_WITH_EVENT_NAME_FROM_ADMIN_PANEL>',
            {
                "to": room_member_list,
                "payload": payload
            })
        if channel_or_group_msg_trigger_crate["acknowledged"] != "true":
            raise HTTPException(
                status_code=422, 
                detail="failed to create a DM notification"
                )
        return channel_or_group_msg_trigger_crate
        


