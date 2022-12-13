import React from "react"
import moment from "moment"
import { ThreadItemWrapper } from "./threadItem.style"

const ThreadItem = ({
  Thread: { created_at, richUiData, emojis, sender_id, threads }
}) => {
  return (
    <ThreadItemWrapper>
      <div className="sender_cont_34f4">
        <p>{sender_id}</p>
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
      {threads.map((thread, index) => (
        <div
          key={index.toString()}
          className="threadCom"
          style={{ border: "1px solid black", margin: "8px 25px" }}
        >
          <p>{thread.sender_id}</p>
          <h3>{thread.richUiData.blocks[0].text}</h3>
          <strong>{thread.created_at}</strong>
        </div>
      ))}
    </ThreadItemWrapper>
  )
}

export default ThreadItem
