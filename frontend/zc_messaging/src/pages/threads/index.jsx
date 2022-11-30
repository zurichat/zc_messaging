import { useEffect, useState } from "react"
import { Helmet } from "react-helmet"
import { ThreadList } from "../../component"
import generatePageTitle from "../../utils/generatePageTitle"
import { getThreadHandler } from "./threads.utils"
import "./threads.css"
import { Toast } from "react-bootstrap"

const Threads = () => {
  const [threadsData, setThreadsData] = useState([])
  const [statusMsgA, setStatusMsgA] = useState(false)
  const [errMsgB, setErrMsgB] = useState(false)

  const toggleTstShowA = () => setStatusMsgA(!statusMsgA)
  const toggleTstShowB = () => setErrMsgB(!errMsgB)

  const jsonDataParse = data => {
    return JSON.parse(data)
  }

  useEffect(() => {
    const userInfo = localStorage.getItem("userData")
    const new_data = jsonDataParse(userInfo)
    const org_ud = new_data.currentWorkspace
    const sender_ud = new_data.user._id

    const threads_data = getThreadHandler(org_ud, sender_ud)
    if (threads_data != []) {
      threads_data
        .then(response => {
          let threads_array = response.data
          let dumpy_threads_Arr = []
          for (let i = 0; i < threads_array.length; i++) {
            for (let j = 0; j < threads_array[i].threadsData.length; j++) {
              dumpy_threads_Arr.push(threads_array[i].threadsData[j])
            }
          }
          setThreadsData(dumpy_threads_Arr)
        })
        .catch(err => {
          console.error(err)
          toggleTstShowB()
        })
    } else {
      toggleTstShowA()
    }
  }, [])

  return (
    <>
      <Helmet>
        <title>{generatePageTitle("threads")}</title>
      </Helmet>
      <div>
        <div>
          <div>
            <Toast show={statusMsgA} onClose={toggleTstShowA} bg="primary">
              <Toast.Header>
                <h3 className="me-auto"></h3>
              </Toast.Header>
              <Toast.Body>
                <p>Nothing was returned. You are up to date</p>
              </Toast.Body>
            </Toast>
          </div>
          <div>
            <Toast show={errMsgB} onClose={toggleTstShowB} bg="danger">
              <Toast.Header>
                <h3 className="me-auto"></h3>
              </Toast.Header>
              <Toast.Body>
                <p>Error fetching Threads. Invalid Arguments!</p>
              </Toast.Body>
            </Toast>
          </div>
        </div>
        <div className="Threads_main_wrapper_45x2c">
          {threadsData ? (
            <ThreadList threadListData={threadsData} />
          ) : (
            <p>Loading...</p>
          )}
        </div>
      </div>
    </>
  )
}

export default Threads
