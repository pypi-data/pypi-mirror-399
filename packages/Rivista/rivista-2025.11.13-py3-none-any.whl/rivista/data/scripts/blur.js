/*
Blur document upon inactivity. This is helpful to prevent the displaying of
sensitive information when you are away from screen. Inactivity time is set to
90 seconds.
*/

window.onload = function() {
  // 'unset' is probably the most preferable
  const originalFilter = document.body.style.filter;
  window.addEventListener('keydown',event => {
    document.body.style.filter = originalFilter;
  });
  window.addEventListener('mousemove',event => {
    document.body.style.filter = originalFilter;
  });
  onInactive(90000, function () {
    if (document.querySelector('video')) {
      if (document.querySelector('video').paused) {
        document.body.style.filter = 'blur(10px)';
      }
    }
  });
}

function onInactive(ms, cb) {
  var wait = setInterval(cb, ms);
  window.ontouchstart = 
  window.ontouchmove = 
  window.onmousemove = 
  window.onmousedown = 
  window.onmouseup = 
  window.onwheel = 
  window.onscroll = 
  window.onkeydown = 
  window.onkeyup = 
  window.onfocus = 
  function () {
    wait = setInterval(cb, ms);
  };
}
