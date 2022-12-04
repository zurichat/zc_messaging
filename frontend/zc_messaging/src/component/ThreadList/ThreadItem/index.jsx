import React from "react"
import styles from "./threadItem.module.css"
import moment from "moment"

const ThreadItem = ({
  Thread: { created_at, richUiData, emojis, sender_id }
}) => {
  return (
    <div className={styles.thread_container_443f}>
      <div className={styles.sender_cont_34f4}>
        <p className={styles.sender_id_3g5x}>{sender_id}</p>
        <p className={styles.date_sent_34f4}>
          {moment(created_at).startOf("hour").fromNow()}
        </p>
      </div>
      <div className={styles.thread_text_cont_45gm6}>
        <p>{richUiData.blocks[0].text}</p>
      </div>
      <div className={styles.emoji_cont_54x4}>
        <p>{emojis}</p>
      </div>
    </div>
  )
}

export default ThreadItem
