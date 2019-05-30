let page = document.getElementById('buttonDiv');
function constructOptions(numButtons) {
  while (numButtons > 0) {
    let button = document.createElement('button');
    button.innerHTML = 'Subsection Name Placeholder';
    button.style.backgroundColor = 'black';
    button.style.color = 'white'; 
    button.addEventListener('click', function() {
      window.open();
    });
    page.appendChild(button);
    numButtons--;
  }
}
constructOptions(5);
