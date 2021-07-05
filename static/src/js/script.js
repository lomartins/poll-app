function copyElementValue(elementId) {
  /* Get the text field */
  const copyText = document.getElementById(elementId);

  /* Select the text field */
  copyText.select();
  copyText.setSelectionRange(0, 99999); /* For mobile devices */

  /* Copy the text inside the text field */
  document.execCommand("copy");
}