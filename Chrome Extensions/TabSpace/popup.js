var background = chrome.extension.getBackgroundPage();

let launchpadButton = document.getElementById('launchpad');
let addButton = document.getElementById('add');
let closeAllButton = document.getElementById('closeAll');
var folderList = document.getElementById('folderList');

$(document).ready(function () {
  folders = Object.keys(background.folderDict);
  for (var f in folders) {
    folderList.options[f] = new Option(folders[f]);
  }
 }) ;

launchpadButton.onclick = function() {
   window.open("launchpad.html");
}

addButton.onclick = function() {
  document.getElementById("temp").classList.toggle("show");
}

window.onclick = function(event) {
  if (!addButton.contains(event.target) && !folderList.contains(event.target)) {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}

closeAllButton.onclick = function() {
  for (var i = 0; i < background.windowlist.length; i++) {
    background.windowlist[i].close();
  }
  background.windowlist.length = 0;
}

// var x = window.open("launchpad.html");
// background.windowlist.push(x);
// if (background.windowlist.length === 0) {
//   window.open("http://youtube.com");
// }
// if (background.windowlist.length > 0) {
//   window.open("http://google.com");
// }
