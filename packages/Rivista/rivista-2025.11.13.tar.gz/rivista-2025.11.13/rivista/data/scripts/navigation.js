/*
Create navigation links from Sitemap (Urlset) documents.
*/

window.addEventListener('load', async function() {
  const locationPathname = location.pathname.split("/");
  const directory = locationPathname[1];
  const filename = locationPathname[2];
  const pathname = `/${directory}/urlset.xml`;
  const response = await retrieveXml(pathname);
  const xmlText = await responseText(response);
  const pathsList = parseXml(xmlText);

  // Set references next and previous.
  let isPageCurrent, pageLast, pageNext, pagePrevious;

  // Set references previous.
  for (let i of pathsList.all) {
    if (i.tagName == "loc") {
      if (pagePrevious) {
        pageNext = i.textContent.trim();
        break;
      } else {
        pageCurrent = i.textContent.trim();
        if (pageLast && pageCurrent == filename) {
          pagePrevious = pageLast;
        }
        pageLast = pageCurrent;
      }
    }
  }

  // Set references next.
  if (!pageNext) {
    for (let i of pathsList.all) {
      if (i.tagName == "loc") {
        if (isPageCurrent) {
          pageNext = i.textContent.trim();
          break;
        } else {
          pageCurrent = i.textContent.trim();
          if (pageCurrent == filename) {
            isPageCurrent = true;
          }
        }
      }
    }
  }

  // Embed XHTML links.
  let s1 = document.querySelector("#xslt-navigation-previous");
  if (s1 && pagePrevious) {
    let p1 = document.createElement("p");
    let a1 = document.createElement("a");
    a1.href = pagePrevious;
    s1.textContent = "";
    a1.textContent = "Previous";
    a1.href = `/${directory}/${pagePrevious}`;
    s1.append(p1);
    p1.append(a1);
  }
  
  let s2 = document.querySelector("#xslt-navigation-proceed");
  if (s2 && pageNext) {
    let p2 = document.createElement("p");
    let a2 = document.createElement("a");
    s2.textContent = "";
    a2.textContent = "Proceed";
    a2.href = `/${directory}/${pageNext}`;
    s2.append(p2);
    p2.append(a2);
  }

});

function parseXml(xmlText) {
  let domParser = new DOMParser();
  let parsedXml = domParser.parseFromString(xmlText, 'text/xml');
  return parsedXml
}

async function responseText(response) {
  return await response.text();
}

async function retrieveXml(pathname) {
  return fetch(pathname)
  .then(response => {
     if (!response.ok) {
       throw new Error(`HTTP error: ${response.status}`);
     }
     return response
  })
  .then(xml => {
    return xml;
  })
  .catch(err => {
    console.warn(err);
  })
}
