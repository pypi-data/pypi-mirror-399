/*
Disable HTTP referer by adding rel="noopener noreferrer".
This prevents the destination site from receiving what URL the user came from.
*/

window.addEventListener('load', function() {
  let elements = ['area', 'form'];
  for (let i = 0; i < elements.length; i++) {
    for (const element of document.querySelectorAll(elements[i])) {
      element.rel = 'noopener noreferrer';
    }
  }
  for (const element of document.querySelectorAll('link')) {
    element.referrerPolicy = 'no-referrer';
  }
  // TODO
  // Do we need array "elements"?
  // Probably not, because we handle 'a[href]' which isn't related to array "elements".
  // I think this for loop should not be here
  for (let i = 0; i < elements.length; i++) {
    for (const element of document.querySelectorAll('a[href]')) {
      // TODO CSS Selector to select a[href] which does
      // not start with hash, instead of "if" statement
      if (!element.href.startsWith(element.baseURI + '#')) {
        element.rel = 'noopener noreferrer';
      }
    }
  }
  // Event delegation works and requires JS enabled
  document.body.addEventListener ("click", function(e) {
    if (e.target && e.target.nodeName == "A" && e.target.href) {
      if (!e.target.href.startsWith(e.baseURI + '#') ||
          !document.querySelector(namespace)) { // TODO Test
        e.target.rel = 'noopener noreferrer';
      }
    }
  });
});
