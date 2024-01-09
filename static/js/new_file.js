const customFileInput = document.getElementById("custom-file-input");
const fileNameDisplay = document.getElementById("file-name");

customFileInput.addEventListener("change", (e) => {
    const files = e.target.files;
    if (files.length > 0) {
        fileNameDisplay.textContent = files[0].name;
    } else {
        fileNameDisplay.textContent = "فایلی انتخاب نشده";
    }
});