//webkitURL is deprecated but nevertheless 
URL = window.URL || window.webkitURL;
var gumStream;
//stream from getUserMedia() 
var rec;
//Recorder.js object 
var input;
//MediaStreamAudioSourceNode we'll be recording 
// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext = new AudioContext;
//new audio context to help us record 
var recordButton = document.getElementById("recordButton");
var realRecordButton = document.getElementById("realRecordButton");
var link;
var basePath="";
var count= 1;
//add events to those 3 buttons 
if(!!recordButton){
	recordButton.onclick = startRecording;
}
if(!!realRecordButton){
	realRecordButton.onclick = startRealRecording;
}


function startRecording() {
	console.log("recordButton clicked");
	
    var constraints = { audio: true, video:false }
	var x = document.getElementById("recordButton").value;
	console.log(x);
	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
		console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

		audioContext = new AudioContext();
		document.getElementById("recordButton").innerHTML  = "Finish"
		document.getElementById("recordButton").onclick = function(){

					console.log("stopButton2 clicked ABC");
					document.getElementById("recordButton").setAttribute("disabled", "disabled");
					document.getElementById("recordButton").style.background=	'#808080';
					//tell the recorder to stop the recording
					rec.stop();
					//stop microphone access
					gumStream.getAudioTracks()[0].stop();
					//create the wav blob and pass it on to createDownloadLink
					
					  rec.exportWAV(sendtoServerAjax);
			}

		gumStream = stream;
		
		input = audioContext.createMediaStreamSource(stream);

		rec = new Recorder(input,{numChannels:1})
		//start the recording process
		rec.record()
		console.log("Recording started");
	}).catch(function(err) {	  	
    	realRecordButton.disabled = false;
	});
}
function startRealRecording() {
	console.log("RealRecordButton clicked");

    var constraints = { audio: true, video:false }

	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
		console.log("getUserMedia() success, stream created, initializing Recorder.js ...");
		console.log("TST"+Flask.url_for("static", {"filename": "images/microphone.gif"}));
		audioContext = new AudioContext();
		document.getElementById("realRecordButton").innerHTML  = "Finish"
			document.getElementById("realRecordButton").onclick = function(){
					console.log("stopButton2 clicked ABC");
					document.getElementById("realRecordButton").setAttribute("disabled", "disabled");
					document.getElementById("realRecordButton").style.background=	'#808080';
					//tell the recorder to stop the recording
					rec.stop();
					//stop microphone access
					gumStream.getAudioTracks()[0].stop();
					//create the wav blob and pass it on to createDownloadLink
					
					  rec.exportWAV(sendtoServerAjax2);
			}

		// document.getElementById("realRecordButton").src = " /Users/CK/downloads/microphone.gif"
		document.getElementById("microphone").src = Flask.url_for("static", {"filename": "images/microphone.gif"});
		gumStream = stream;
		
		input = audioContext.createMediaStreamSource(stream);

		rec = new Recorder(input,{numChannels:1})
		//start the recording process
		rec.record()
		console.log("Recording started");
	}).catch(function(err) {	  	
    	//recordButton.disabled = false;
	});
}
function stopRecording() {
	console.log("stopButton clicked");
	//tell the recorder to stop the recording
	rec.stop();
	//stop microphone access
	gumStream.getAudioTracks()[0].stop();
	//create the wav blob and pass it on to createDownloadLink
	 rec.exportWAV(sendtoServerAjax);
}
function stopRecording2() {
	count++;
	console.log("stopButton2 clicked");
	document.getElementById("realRecordButton").disabled = "true";
	//tell the recorder to stop the recording
	rec.stop();
	//stop microphone access
	gumStream.getAudioTracks()[0].stop();
	//create the wav blob and pass it on to createDownloadLink
	
	 rec.exportWAV(sendtoServerAjax2);
}
function sendtoServerAjax2(blob){

	realRecordButton.disabled= true;
    var filename = new Date().toISOString();
    link = URL.createObjectURL(blob);
    console.log("TEST2"+basePath)
    var fd = new FormData();
    fd.append("audio_data", blob, filename);
    fd.append("baseA",basePath);
    // fd.append("num",2);
	$.ajax({
	    type: 'POST',
	    url: '/saveAudio',
	    data: fd,
	    processData: false,
	    contentType: false,
	    success : function(completeHtmlPage,data1, data2,data3) {
	    	alert("Successfully got your voice2");

	    	document.write(completeHtmlPage);
		},
		error : function() {
		    alert("error in loading");
		}
	});
}

function sendtoServerAjax(blob){
    var filename = new Date().toISOString();
    var fd = new FormData();
    fd.append("audio_data", blob, filename);

    // fd.append("num",1);    
	$.ajax({
	    type: 'POST',
	    url: '/saveBase',
	    data: fd,
	    processData: false,
	    contentType: false,
	    success : function(completeHtmlPage) {
	    	 window.location.href='/realRecord';
		},
		error : function() {
		    alert("error in loading");
		}
	});
}

