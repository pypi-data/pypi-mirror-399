/*
  This script is required due to some browser vendors which deliberately ignore
  various of XSLT directives, including the directive "disable-output-escaping".

  There is no reason to "report" of this issue to these vendors, because this is
  a deliberate fault which is intended to discourage XSLT.

  Therefore, please do not spend your time on reporting of this issue to any
  vendor.

  Rather, you are encouraged to promote the distribution of HTML, XHTML, and XML
  (e.g. The Atom Syndication Format) contents via PPN/P2P and render these
  documents with software such as DC++, eDonkey2000, eMule, Gnutella, MUTE,
  Shareaza, et cetera.

  The only way to change, is to seek alternatives.
*/

window.addEventListener("load", function() {
  // Scan for elements with indicators of HTML content.
  for (element of document.querySelectorAll("[type*='html']")) {
    // Check whether content has HTML elements.
    if (element.children.length < 1) {
      // Retrieve text content.
      plainContent = element.textContent;
      // Instatiate an HTML/XML object parser.
      domParser = new DOMParser();
      // Generate an HTML document.
      processedContent = domParser.parseFromString(plainContent, "text/html");
      // Replace content by the new HTML document.
      element.innerHTML = processedContent.body.innerHTML;
    }
  }
});
