window.addEventListener("load", function() {
  if (sessionStorage.getItem("dismissWarning") == "1") { return; }
  // Properties of ECMAScript client.
  //const isMobile = navigator.userAgentData.mobile
  //const operatingSystem = navigator.userAgentData.platform;
  const platform = navigator.platform;
  const userAgent = navigator.userAgent;

  const isUserAgentIncluded = isKeywordIncluded(
      ["Chrome", "Edg", "EdgA", "EdgiOS", "Firefox", "FxiOS", "OPR",
        "Safari", "Trident", "YaBrowser", "Yowser", "Vivaldi"],
      userAgent);

  const isSystemIncluded = isKeywordIncluded(
      ["CrOS", "Fedora", "iPad", "iPhone", "iPod", "Mac OS", "Macintosh",
       "Ubuntu", "Windows"],
      userAgent);

  // Embed XHTML links.
  if (isUserAgentIncluded || isSystemIncluded) {
    let link, components;
    if (isUserAgentIncluded && isSystemIncluded) {
      components = "browser and system";
      link = "/help/";
    } else
    if (isUserAgentIncluded) {
      components = "browser";
      link = "/help/html/";
    } else
    if (isSystemIncluded) {
      components = "system";
      link = "/help/os/";
    }
    let dl = document.createElement("dl");
    dl.style.backgroundColor = "rgb(176 76 76)";
    dl.style.borderRadius = "7px";
    dl.style.textDecoration = "none";
    dl.style.fontFamily = "system-ui";
    dl.style.fontSize = "80%";
    dl.style.maxWidth = "500px";
    dl.style.margin = "1em auto";
    dl.style.padding = "7px";
    dl.style.display = "block";
    //dl.style.textAlign = "center";
    dl.style.direction = "ltr";
    dl.style.userSelect = "none";
    //dl.style.position = "fixed";
    //dl.style.bottom = 0;
    //dl.style.left = 0;
    //dl.style.right = 0;
    document.body.prepend(dl);
    let dt = document.createElement("dt");
    dl.append(dt);
    let dtSpan = document.createElement("span");
    dtSpan.style.color = "rgb(207 207 207)";
    dtSpan.style.fontWeight = "bold";
    dtSpan.textContent = "⚠️ Warning!";
    dt.append(dtSpan);
    let dd = document.createElement("dd");
    dl.append(dd);
    let ddP = document.createElement("p");
    ddP.style.color = "#fff";
    ddP.textContent = `Insecure ${components} detected. Please proceed to instructions.`;
    dd.append(ddP);
    let ddDiv = document.createElement("div");
    ddDiv.style.textAlign = "right";
    dd.append(ddDiv);
    let divButtonA = document.createElement("button");
    divButtonA.textContent = "Proceed";
    divButtonA.style.margin = "7px";
    divButtonA.onclick = () => { location = link }
    ddDiv.append(divButtonA);
    let divButtonB = document.createElement("button");
    divButtonB.textContent = "Dismiss";
    divButtonB.style.margin = "7px";
    divButtonB.onclick = () => {
      dl.remove();
      sessionStorage.setItem("dismissWarning", 1);
    }
    ddDiv.append(divButtonB);
  }

});

function isKeywordIncluded(keywords, userAgent) {
  for (keyword of keywords) {
    if (userAgent.includes(keyword)) {
      return true
    }
  }
}
