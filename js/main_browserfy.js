let colorize = require("apply-colormap")
let fill = require("ndarray-fill")
let zeros = require("zeros")
let colormap = require('colormap')
 
/* var x = zeros([512, 512])
fill(x, function(a,b) {
  return a*a + b*b
})
 
imshow(colorize(x)) */

window.zeros = zeros;
window.fill = fill;
window.colorize = colorize;
window.colormap = colormap;