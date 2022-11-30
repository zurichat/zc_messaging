import React from "react"
import ThreadItem from "./ThreadItem"
import "./threadList.module.css"

const ThreadList = ({ threadListData }) => (
  <div className="threadList-Wrap">
    {threadListData.map(thread => (
      <ThreadItem key={thread.message_id} Thread={thread} />
    ))}
  </div>
)

export default ThreadList
