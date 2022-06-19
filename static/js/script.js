function startPrediction(){
  const webCamElement = document.getElementById("webCam");
  const canvasElement = document.getElementById("canvas");
  const webcam = new Webcam(webCamElement, "user",canvasElement);
  webcam.start();
}

let camera_button = document.querySelector("#start-camera");
let video = document.querySelector("#video");
let click_button = document.querySelector("#click-photo");
let canvas = document.querySelector("#canvas");

camera_button.addEventListener('click', async function() {
   	let stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
	video.srcObject = stream;
});


click_button.addEventListener('click', function() {
   	canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
//   	let dataURL = canvas.toDataURL('image/jpg');
//   	var image = canvas.toDataURL("image/jpg").replace("image/jpg", "image/octet-stream");  // here is the most important part because if you dont replace you will get a DOM 18 exception.
//    window.location.href=image; // it will save locally

      image = canvas.toDataURL("image/jpg", 1.0).replace("image/jpg", "image/octet-stream");
      var link = document.createElement('a');
      link.download = "webcam_img.jpg";
      link.href = image;
      link.click();

//   	var dataURL = canvas.toDataURL();
        console.log(image);
        console.log(typeof(image));


//                        $.ajax({
//                                type: "POST",
//                                url: "http://127.0.0.1:5000/predict_capture",
//                                data: {
//                                    file: image
//                    //                access_token: $("#access_token").val()
//                                },
//                                dataType: 'file',
//                                success: function(result) {
//                                    alert('ok');
//                                },
//                                error: function(result) {
//                                    alert('error');
//                            }
//                        });


});

//var blobBin = atob(dataURL.split(',')[1]);
//var array = [];
//for(var i = 0; i < blobBin.length; i++) {
//    array.push(blobBin.charCodeAt(i));
//}
//var file=new Blob([new Uint8Array(array)], {type: 'image/png'});
//
//
//var formdata = new FormData();
//formdata.append("myNewFileName", file);
//$.ajax({
//   url: "uploadFile.php",
//   type: "POST",
//   data: formdata,
//   processData: false,
//   contentType: false,
//}).done(function(respond){
//  alert(respond);
//});




//click_button.addEventListener('click', function() {
//   	canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
//   	let image_data_url = canvas.toDataURL('image/jpg');
//
////           $.ajax({
////              type: "POST",
////              url: "/webcam_upload",
////              data:{
////                imageBase64: dataURL
////              }
////           }).done(function() {
////              console.log('sent');
////           });
//
//
//
//
//
////        canvas.toBlob(function(blob) {
////            saveAs(blob, "img.jpg");
//////            console.log();
////        });
//});

//canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
//let dataURL = canvas.toDataURL('image/jpg');
//
//$(click_button).ajax({
//  type: "POST",
//  url: "/webcam_upload",
//  data:{
//    imageBase64: dataURL
//  }
//}).done(function() {
//  console.log('sent');
//});
//
//$("click-photo").click(function(e) {
//    e.preventDefault();
//    $.ajax({
//        type: "POST",
//        url: "/pages/test/",
//        data: {
//            id: $(this).val(), // < note use of 'this' here
//            access_token: $("#access_token").val()
//        },
//        success: function(result) {
//            alert('ok');
//        },
//        error: function(result) {
//            alert('error');
//        }
//    });
//});