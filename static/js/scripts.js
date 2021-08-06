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
