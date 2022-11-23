import { Helmet } from "react-helmet"
import generatePageTitle from "../../utils/generatePageTitle"

const Threads = () => {
  return (
    <>
      <Helmet>
        <title>{generatePageTitle("threads")}</title>
      </Helmet>

      <h1>Threads</h1>
    </>
  )
}

export default Threads
