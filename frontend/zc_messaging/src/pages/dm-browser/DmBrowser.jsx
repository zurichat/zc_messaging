import AllDmsComboBox from "./components/dm_browser_combo_box/DmBrowserComboBox"
import {
  AllDmsContainer,
  AllDmsHeader,
  AllDmsHeaderTextContainer
} from "./DmBrowser.styled"

const AllDms = () => {
  return (
    <AllDmsContainer>
      <AllDmsHeader>
        <AllDmsHeaderTextContainer>
          <p>#</p>
          <p>All direct messages</p>
        </AllDmsHeaderTextContainer>
      </AllDmsHeader>
      <AllDmsComboBox />
    </AllDmsContainer>
  )
}

export default AllDms
