const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))


function copy(text) {
    navigator.clipboard.writeText(window.location.href + text)
}


document.addEventListener("DOMContentLoaded", function() {
  setTimeout(function() {
    document.getElementById("overlay").style.display = "none";
  }, 300); // Adjust the delay (in milliseconds) as desired
});