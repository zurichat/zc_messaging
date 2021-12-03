import React from "react"
import "./hello.module.css"

export default function Hello(props) {
  return <h1 className="heading">Hello {props.text}</h1>
}
