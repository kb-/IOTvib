//var c = $("#placeholder2 .flot-base")[0]

export function plotmarkers(c,m){//canvas, markers[{left: 113, top: 43, color:#003300, radius:2}]
  var ctx = c.getContext("2d");
  for(let i=0; i<m.length; i++) {
    ctx.beginPath();
    ctx.arc(m[i].left, m[i].top, m[i].radius, 0, 2 * Math.PI, false);
    ctx.fillStyle = m[i].color;
    ctx.fill();
    ctx.lineWidth = 1;
    ctx.strokeStyle = m[i].color;
    ctx.stroke();
  }
}