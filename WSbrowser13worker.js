var ws2 = new WebSocket("ws://127.0.0.1:5677/");
placeholder2 = $("#placeholder2");
var plot2 = $.plot(placeholder2, [data2], options2);


console.time("onmessage ws2");
ws2.onmessage = function (event) {
  decode(event.data, def2, updateOption);
  // console.timeLog("onmessage ws2");
  
  function updateOption(ds){
    data2 = [[],[],[]];
    var j=0;
    var tmpdata = [];
    // var x=[], y=[];
    while (!ds.isEof()) {
      var obj = ds.readStruct(def2);
      tmpdata.push([[j*df,obj["X"]*XGAIN],[j*df,obj["Y"]*YGAIN],[j*df,obj["Z"]*ZGAIN]]);//for some reason obj.x didn't work here...
      // y.push(obj.x*XGAIN);
      // x.push(j*df);
      j++;
    }
    // data2 = data2.concat(tmpdata);
    // for (i = 0; i < tmpdata.length; i++){
      // Array.prototype.push.apply(data2[i], tmpdata[i])
    // }
    plot2.setData(tmpdata);
    // plot2.setData(data2);
    plot2.setupGrid();
    plot2.draw();
    zoomSelect(placeholder2,plot2,'x',data2);
    spectrums.push(data2);
  }
}

//convert binary data to datastream
function decode(dataB, def, cb){
  new Response(dataB).arrayBuffer().then(runOnDs);//event.data is blob
    function runOnDs(a){
      f = new Uint8Array(a);  
      cb(new DataStream(f.buffer));
    }
}