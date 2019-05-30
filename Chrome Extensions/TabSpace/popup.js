var background = chrome.extension.getBackgroundPage();

let launchpadButton = document.getElementById('launchpad');
let addButton = document.getElementById('add');
let closeAllButton = document.getElementById('closeAll');

launchpadButton.onclick = function() {
   window.open("launchpad.html");
}

addButton.onclick = function() {
  var x = window.open("launchpad.html");
  background.windowlist.push(x);
  if (background.windowlist.length === 0) {
    window.open("http://youtube.com");
  }
  if (background.windowlist.length > 0) {
    window.open("http://google.com");
  }
}

closeAllButton.onclick = function() {
  for (var i = 0; i < background.windowlist.length; i++) {
    background.windowlist[i].close();
  }
  background.windowlist.length = 0;
}
