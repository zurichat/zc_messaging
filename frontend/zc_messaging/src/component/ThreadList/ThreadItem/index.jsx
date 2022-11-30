import React from "react"
import "./threadItem.module.css"
import moment from "moment"

const ThreadItem = ({
  Thread: { created_at, richUiData, emojis, sender_id }
}) => {
  return (
    <div className="thread_container_443f">
      <div className="sender_cont_34f4">
        <p className="sender_id_3g5x">{sender_id}</p>
        <p className="date_sent_34f4">
          {moment(created_at).startOf("hour").fromNow()}
        </p>
      </div>
      <div className="thread_text_cont_45gm6">
        <p>{richUiData.blocks[0].text}</p>
      </div>
      <div className="emoji_cont_54x4">
        <p>{emojis}</p>
      </div>
    </div>
  )
}

export default ThreadItem
