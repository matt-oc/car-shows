// https://www.webtrickshome.com/forum/how-to-display-uploaded-image-in-html-using-javascript for preview of uploaded image
// https://stackoverflow.com/questions/5697605/limit-the-size-of-a-file-upload-html-input-element file size limit
  var loadFile = function(event) {
  	var image = document.getElementById('output');
    var eventImage = document.getElementById('eventImage');
    //ensuring the filesize doesnt exceed 16MB
    image.src = URL.createObjectURL(event.target.files[0]);
    if(event.target.files[0].size > 15999024){
       alert("Image must be below 16MB!");
        image.src = "";
       eventImage.value="";
    }
};


// adapted from https://codepen.io/astrit/pen/OJPyqyx
// Hiding the flash messages after a small pause
window.setTimeout(function() {
    $(".alert").slideUp(400);
}, 4000);




var getWindowOptions = function() {
  var width = 500;
  var height = 350;
  var left = (window.innerWidth / 2) - (width / 2);
  var top = (window.innerHeight / 2) - (height / 2);

  return [
    'resizable,scrollbars,status',
    'height=' + height,
    'width=' + width,
    'left=' + left,
    'top=' + top,
  ].join();
};

function twShare(id){
  const url = window.location.href;
  const lastSegment = url.split("/").pop();
var shareUrl = 'https://twitter.com/intent/tweet?url=' + window.location.href + lastSegment;
  var win = window.open(shareUrl, 'ShareOnTwitter', getWindowOptions());
  win.opener = null;
};

function fbShare(){
  const url = window.location.href
  const lastSegment = url.split("/").pop();
var shareUrl = 'https://www.facebook.com/sharer/sharer.php?u=' + window.location.href + lastSegment;
  var win = window.open(shareUrl, 'facebook-share-dialog', getWindowOptions());
  win.opener = null;
};

// Contact us form
var contactModal = document.getElementById('contactModal')

contactModal.addEventListener('shown.bs.modal', function() {
  myInput.focus()
})


var form = document.getElementById("contact");

// Success and Error functions for after the form is submitted

function success() {
  form.reset();
  alert("Success! we will be in touch shortly.");
  document.getElementById("closeContactModal").click(); // Close the modal on success

}

function error() {
  alert("Oops! There was a problem.");
}

// handle the form submission event from formspree.io

form.addEventListener("submit", function(ev) {
  ev.preventDefault(); // stop the standard form POST submit so we can stay on our page and display a response to the user.
  var data = new FormData(form);
  ajax(form.method, form.action, data, success, error);
});


// helper function for sending an AJAX request from formspree.io

function ajax(method, url, data, success, error) {
  var xhr = new XMLHttpRequest();
  xhr.open(method, url);
  xhr.setRequestHeader("Accept", "application/json");
  xhr.onreadystatechange = function() {
    if (xhr.readyState !== XMLHttpRequest.DONE) return;
    if (xhr.status === 200) {
      success(xhr.response, xhr.responseType);
    } else {
      error(xhr.status, xhr.response, xhr.responseType);
    }
  };
  xhr.send(data);
}
