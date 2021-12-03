import "./AllDmsComboBox.module.css"
const AllDmsComboBox = () => {
  return (
    <div className="all_dms_combo_box_container">
      <p>To:</p>
      <div className="all_dms_combo_box_content">
        <input type="text" placeholder="@somebody or somebody@example.com" />
        <div className="all_dms_combo_box_search_modal_container"></div>
      </div>
    </div>
  )
}

export default AllDmsComboBox
