import {
  AllDmsComboBoxContainer,
  AllDmsComboBoxContent
} from "./DmBrowserComboBox.styled.js"
const AllDmsComboBox = () => {
  return (
    <AllDmsComboBoxContainer>
      <p>To:</p>
      <AllDmsComboBoxContent>
        <input type="text" placeholder="@somebody or somebody@example.com" />
        <div className="all_dms_combo_box_search_modal_container"></div>
      </AllDmsComboBoxContent>
    </AllDmsComboBoxContainer>
  )
}

export default AllDmsComboBox
