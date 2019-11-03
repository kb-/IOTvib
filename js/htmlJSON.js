//form to json
//inspired by: https://jsfiddle.net/gabrieleromanato/bynaK/
/* (function ($) {
    $.fn.formtoJSON = function () {

        var o = {};
        var a = this.serializeArray();
        $.each(a, function () {
            if (o[this.name]) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        
        //convert str to number if possible
        for(let d in o){
          o[d] = isNaN(o[d])?o[d]:o[d]/1;
        }
        return o;
    };
})(jQuery); */
(function ($) {
    $.fn.formtoJSON = function (prefix) {
        
        if (typeof(prefix) != "undefined") {
          var expr = new RegExp('^'+prefix);
          name = name.replace(expr,"");
        }

        var o = {};
        var a = this.serializeArray();
        $.each(a, function () {
          var name = this.name;
          
          if (typeof(prefix) != "undefined") {
            name = name.replace(expr,"");
          }
          
          if(this.value!==""){//discard empty field
            if (o[name]) {
                if (!o[name].push) {
                    o[name] = [o[name]];
                }
                o[name].push(this.value || '');
            } else {
                o[name] = this.value || '';
            }
          }
        });
        
        //convert str to number and str to bool if possible
        for(let d in o){
          o[d] = isNaN(o[d])?o[d]:o[d]/1;
          o[d] = ["true","false"].includes(o[d])?JSON.parse(o[d]):o[d];
        }
        return o;
    };
})(jQuery);

//inspired by: https://stackoverflow.com/a/14447147
//[{value:"",label:""},...]
(function ($) {
    $.fn.JSONtoSelect = function (data) {
        var html = '';

        for (var i = 0, len = data.length; i < len; ++i) {
            html = html.concat('<option value="' + data[i]['value'] + '">' + data[i]['label'] + '</option>');
        }           
        $(this).append(html);
    }
})(jQuery);


(function ($) {
    $.fn.JSONtoInput = function (data,type,class_,container) {
        var html = '';
//<label for="fftdf">Δf (Hz)</label><input type="text" name="fftdf" id="fftdf" value="1" class="rgtSettingsInput"/>
        for (var i = 0, len = data.length; i < len; ++i) {
            html = '<div><label for="' + data[i]['id'] + '">' + data[i]['label'] + '</label><input type="'+ type +'" name="' + data[i]['name'] + '" id="' + data[i]['id'] + '" class="' +class_+ '"/></div>';
            var h = $(html).wrap(container);
            $(this).append(h);
        }           
        // $(this).append(html);
        // $(this).find('div').addClass(containerClass);
    }
})(jQuery);