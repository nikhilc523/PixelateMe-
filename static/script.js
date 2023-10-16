const uploadInput = document.getElementById('video-upload');
const uploadFilename = document.querySelector('.upload-filename');
const uploadBtn = document.getElementById('upload-btn');
const videoPreview = document.querySelector('.video-preview');
const body = document.querySelector("body");
const mysidebar = document.getElementById("mysidebar");
uploadInput.addEventListener('change', function () {
  const file = this.files[0];
  uploadFilename.textContent = file.name;
  uploadBtn.style.display = 'inline-block';

  const reader = new FileReader();
  reader.onload = function (e) {
    videoPreview.src = e.target.result;
    videoPreview.style.display = 'block';
  };
  reader.readAsDataURL(file);
});

document.getElementById("user-icon").addEventListener("click", function() {
  var dropdown = document.getElementById("dropdown");
  if (dropdown.style.display === "none") {
    dropdown.style.display = "block";
  } else {
    dropdown.style.display = "none";
  }
});

document.addEventListener("click", function(event) {
  var dropdown = document.getElementById("dropdown");
  if (!event.target.matches("#user-icon") && !event.target.matches("#dropdown")) {
    dropdown.style.display = "none";
  }
});


function toggleDark() {
  if (body.classList.contains("dark")) {
    body.classList.remove("dark");
    localStorage.setItem("theme", "light");
  } else {
    body.classList.add("dark");
    localStorage.setItem("theme", "dark");
  }
}
if (localStorage.getItem("theme") === "dark") {
  body.classList.add("dark");
}

function toggleMneu() {
  mysidebar.classList.toggle("shrink_sidebar");
}


