/**
 * @param {string} title title for the page
 * @returns {string}
 * @description
 * returns the page title
 */

const generatePageTitle = title => {
  const workspaceName = localStorage.getItem("orgName")
  const pageTitle = `Zuri Chat ${title ? "| " + title : ""} ${
    workspaceName ? "| " + workspaceName : ""
  }`
  return pageTitle
}

export default generatePageTitle
