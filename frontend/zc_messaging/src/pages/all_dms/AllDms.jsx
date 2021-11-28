import "./AllDms.module.css"
import AllDmsComboBox from "./components/all_dms_combo_box/AllDmsComboBox"
const AllDms = () => {
  return (
    <div className="all_dms_container">
      <header className="all_dms_header d-flex align-items-center">
        <div className="all_dms_header_text_container d-flex align-items-center">
          <p>#</p>
          <p>All direct messages</p>
        </div>
      </header>
      <AllDmsComboBox />
    </div>
  )
}

export default AllDms
