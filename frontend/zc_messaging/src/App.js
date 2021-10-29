import React from "react"
import Hello from "./component/Hello"

export default function App() {
  return (
    <div>
      <Hello text="Zuri people" />
      <h2>App is not running on grace!!😊 let's keep it that way</h2>
      <p>
        <strong>Few guide lines</strong>
      </p>
      <ul>
        <li>Make sure to remove console.logs after debugging </li>
        <li>Don't repeat codes, create a reusable component</li>
        <li>Avoid re-rendering!!!</li>
        <li>Don't style elements globally please 😢</li>
        <li>Use comments where needed so we can understand what is written</li>
      </ul>
    </div>
  )
}
