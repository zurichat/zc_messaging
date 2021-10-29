import React from "react"
import style from "./hello.module.css"

export default function Hello(props) {
  return <h1 className={style.heading}>Hello {props.text}</h1>
}
