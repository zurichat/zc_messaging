import React from "react"
import ThreadItem from "./ThreadItem"
import { Container } from "./threadList.style"

const ThreadList = ({ threadListData }) => (
  <Container>
    {threadListData.map((message, index) => (
      <ThreadItem key={index} Thread={message} />
    ))}
  </Container>
)

export default ThreadList
