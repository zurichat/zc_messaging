import React from "react"
import { FiX } from "react-icons/fi"
import { useNavigate, useParams } from "react-router"
import { Link } from "react-router-dom"

import { ThreadBar, ThreadBarHeader, ThreadBarContent } from "./ThreadBar.style"

const Thread = () => {
  const navigate = useNavigate()
  const params = useParams()
  return (
    <ThreadBar>
      <ThreadBarHeader>
        <span>
          <h4>Thread</h4>
          {/*
          <h5>Announcement</h5>
  */}
        </span>
        <span>
          <Link to={`/${params.roomId || ""}`}>
            <FiX stroke="white" size={18} />
          </Link>
        </span>
      </ThreadBarHeader>
      <ThreadBarContent>
        {/* <MessageCard /> */} Thread id {params.threadId}{" "}
      </ThreadBarContent>
    </ThreadBar>
  )
}

export default Thread
