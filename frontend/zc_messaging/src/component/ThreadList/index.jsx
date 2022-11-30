import React from "react"
import ThreadItem from "./ThreadItem"
import styles from "./threadList.module.css"

const ThreadList = ({ threadListData }) => (
  <div className={styles.threadListWrap}>
    {threadListData.map(thread => (
      <ThreadItem key={thread.message_id} Thread={thread} />
    ))}
  </div>
)

export default ThreadList
