//https://github.com/scijs
//http://scijs.net/packages/
let colorize = require("apply-colormap")//https://www.npmjs.com/package/apply-colormap
let fill = require("ndarray-fill")//https://www.npmjs.com/package/ndarray-fill
let zeros = require("zeros")//https://www.npmjs.com/package/zeros
let colormap = require('colormap')//https://www.npmjs.com/package/colormap
let ndarray = require('ndarray')//https://github.com/scijs/ndarray
let pack = require('ndarray-pack')//http://scijs.net/packages/#scijs/ndarray-pack
let unpack = require('ndarray-unpack')//http://scijs.net/packages/#scijs/ndarray-unpack
let ops = require('ndarray-ops')//http://scijs.net/packages/#scijs/ndarray-ops
let cwise = require("cwise")//http://scijs.net/packages/#scijs/cwise
 
/* var x = zeros([512, 512])
fill(x, function(a,b) {
  return a*a + b*b
})
 
imshow(colorize(x)) */

window.zeros = zeros;
window.fill = fill;
window.colorize = colorize;
window.colormap = colormap;
window.ndarray = ndarray;
window.pack = pack;
window.unpack = unpack;
window.ops = ops;
window.cwise = cwise;