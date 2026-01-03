window.addEventListener("load", function() {
  if (sessionStorage.getItem("dismissSecurity") == "1") { return; }
  // Disable JavaScript.
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
  ddP.textContent = "JavaScript is insecure by design, and endangers your privacy. Please proceed to instructions.";
  dd.append(ddP);
  let ddDiv = document.createElement("div");
  ddDiv.style.textAlign = "right";
  dd.append(ddDiv);
  let divButtonA = document.createElement("button");
  divButtonA.textContent = "Proceed";
  divButtonA.style.margin = "7px";
  divButtonA.onclick = () => { location = "/help/ecma" }
  ddDiv.append(divButtonA);
  let divButtonB = document.createElement("button");
  divButtonB.textContent = "Dismiss";
  divButtonB.style.margin = "7px";
  divButtonB.onclick = () => {
    dl.remove();
    sessionStorage.setItem("dismissSecurity", 1);
  }
  ddDiv.append(divButtonB);
});
