/*
Disable HTTP referer by adding rel="noopener noreferrer".
This prevents the destination site from receiving what URL the user came from.
*/

const
  hueDegreeValue = 0,
  iconPosition = "br",
  svgGraphics = `<?xml version="1.0"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="128px" height="128px" viewBox="0 0 256 256"><defs><linearGradient x1="0.085" y1="0.085" x2="0.915" y2="0.915" id="syndication"><stop  offset="0.0" stop-color="#E3702D"/><stop  offset="0.1071" stop-color="#EA7D31"/><stop  offset="0.3503" stop-color="#F69537"/><stop  offset="0.5" stop-color="#FB9E3A"/><stop  offset="0.7016" stop-color="#EA7C31"/><stop  offset="0.8866" stop-color="#DE642B"/><stop  offset="1.0" stop-color="#D95B29"/></linearGradient></defs><rect width="256" height="256" rx="55" ry="55" x="0"  y="0"  fill="#CC5D15"/><rect width="246" height="246" rx="50" ry="50" x="5"  y="5"  fill="#F49C52"/><rect width="236" height="236" rx="47" ry="47" x="10" y="10" fill="url(#syndication)"/><circle cx="68" cy="189" r="24" fill="#FFF"/><path d="M160 213h-34a82 82 0 0 0 -82 -82v-34a116 116 0 0 1 116 116z" fill="#FFF"/><path d="M184 213A140 140 0 0 0 44 73 V 38a175 175 0 0 1 175 175z" fill="#FFF"/></svg>`;

window.addEventListener("load", function() {
  let links = [],
      mimeTypes = [
        "application/activity+xml",
        "application/activitystream+xml",
        "application/atom+xml",
        "application/feed+json",
        "application/gemini+text",
        "application/pubsub+xml",
        "application/rdf+xml",
        "application/rss+json",
        "application/rss+xml",
        "application/smf+xml",
        "application/stream+xml",
        "application/twtxt+text",
        "text/twtxt+plain",
        "text/gemini"
      ];
  for (mimeType of mimeTypes) {
    results = document.head.querySelectorAll(`link[type="${mimeType}"`);
    /*
    results = document.head.queryPathAll(
      null,
      //`link[@rel="alternate" and contains(@type, "${mimeType}")]`);
      `link[@rel="alternate" and @type="${mimeType}"]`);
    */
    for (result of results) {
      let a = document.createElement("a");
      if (result.href.startsWith("feed:")) {
        result.href = result.href.replace("feed:", "http:");
      } else
      if (result.href.startsWith("itpc:")) {
        result.href = result.href.replace("itpc:", "http:");
      } else {
      }
      a.href = result.href;
      a.title = mimeType;
      a.textContent = result.title;
      a.style.display = "block";
      a.style.color = "#eee";
      for (let i = 0; i < a.style.length; i++) {
        a.style.setProperty(
          a.style[i],
          a.style.getPropertyValue(a.style[i]),
          "important"
        );
      }
      links.push(a);
    }
  }
  if (links.length) {
    generateRssIndicator(links)
  }
});

function generateRssIndicator(links) {
  let iconElement = document.createElement("div");
  //iconElement.id = namespace + "-icon";
  iconElement.innerHTML = svgGraphics;
  if (iconPosition.includes("b")) {iconElement.style.bottom = 0};
  if (iconPosition.includes("l")) {iconElement.style.left = 0};
  if (iconPosition.includes("r")) {iconElement.style.right = 0};
  if (iconPosition.includes("t")) {iconElement.style.top = 0};
  iconElement.style.margin = "1em";
  iconElement.style.display = "block";
  iconElement.style.position = "fixed";
  iconElement.style.zIndex = 2147483646;
  //iconElement.style.height = "32px";
  //iconElement.style.width = "32px";
  svgElement = iconElement.querySelector("svg");
  svgElement.style.height = "32px";
  svgElement.style.width = "32px";
  svgElement.style.filter = `drop-shadow(2px 2px 2px orange) hue-rotate(${hueDegreeValue}deg)`;
  // Set !important
  for (let i = 0; i < iconElement.style.length; i++) {
    iconElement.style.setProperty(
      iconElement.style[i],
      iconElement.style.getPropertyValue(iconElement.style[i]),
      "important"
    );
  }
  //iconElement.append("索 This site offers syndicated contents:") // 📰 ⚛
  //links.forEach(link => iconElement.append(link));
  //iconElement.append(closeButton(iconElement));
  document.body.append(iconElement);
  let dl = document.createElement("dl");
  dl.style.backgroundColor = "rgb(94, 94, 94)"; // rgb(76 176 76)
  dl.style.borderRadius = "7px";
  dl.style.textDecoration = "none";
  dl.style.fontFamily = "system-ui";
  dl.style.fontSize = "80%";
  dl.style.margin = "7px";
  dl.style.padding = "7px";
  dl.style.display = "block";
  //dl.style.textAlign = "center";
  dl.style.direction = "ltr";
  dl.style.userSelect = "none";
  dl.style.position = "fixed";
  dl.style.bottom = 0;
  //dl.style.left = 0;
  dl.style.right = 0;
  //document.body.append(dl);
  let dt = document.createElement("dt");
  dl.append(dt);
  let dtSpan = document.createElement("span");
  dtSpan.style.color = "rgb(230 230 230)";
  dtSpan.style.fontWeight = "bold";
  dtSpan.textContent = "📰 Subscriptions";
  dt.append(dtSpan);
  let dd = document.createElement("dd");
  dl.append(dd);
  let ddP = document.createElement("p");
  ddP.style.color = "#fff";
  ddP.textContent = "RSS news subscriptions for you to choose from.";
  dd.append(ddP);
  let ddDivA = document.createElement("div");
  ddDivA.style.textAlign = "left";
  dd.append(ddDivA);
  for (divA of links) {ddDivA.append(divA);}
  let ddDivB = document.createElement("div");
  ddDivB.style.textAlign = "right";
  dd.append(ddDivB);
  let divButton = document.createElement("button");
  divButton.textContent = "Close";
  divButton.style.margin = "7px";
  divButton.onclick = () => {
    dl.remove();
    document.body.append(iconElement);
  }
  ddDivB.append(divButton);
  // iconElement
  iconElement.onclick = () => {
    document.body.append(dl);
    iconElement.remove();
  }
}

Node.prototype.queryPathAll = function (xmlns, expression) {
  let data = this.ownerDocument || this;
  let nodes = data.evaluate(
    expression,
    this,
    () => xmlns,
    XPathResult.ORDERED_NODE_ITERATOR_TYPE,
    null);
  let results = [];
  let node = nodes.iterateNext();
  while (node) {
    // Add the link to the array
    results.push(node);
    // Get the next node
    node = nodes.iterateNext();
  }
  return results;
};

Node.prototype.queryPath = function (xmlns, expression) {
  let data = this.ownerDocument || this;
  return data.evaluate(
    expression,
    this,
    () => xmlns,
    XPathResult.FIRST_ORDERED_NODE_TYPE,
    null)
    .singleNodeValue;
};
