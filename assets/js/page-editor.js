/**
 * Copied from road.lk common.js
 */
function show_timing(startObj, endObj, compact)
{
    var day = 1000 * 60 * 60 * 24;
    var year = day * 365;
    var days = ["Jan","Feb","March","April","May","June","July","Aug","Sept","Oct","Nov","Dec"];
    var duration = 0;

    
     var current =  new Date();
     var start = parseInt(startObj.text()) ;
     if(! start || start < 10000) {
         return ;
     }
     if (start < 10000000000) {
    	 start = start *1000;
     }
     start = new Date(start);
     
     var delta = current.getTime() - start.getTime();
       
     if(endObj && endObj.text().trim() != '') {
         var end = new Date(parseInt(endObj.text()));
         if(end) {
             duration = end.getTime() - start.getTime();
             endObj.text(secondsToTime((duration)/1000));
         }
     }
     
     var hours = (start.getHours() < 10 ) ? "0" + start.getHours() : start.getHours();
     var minutes = (start.getMinutes() < 10) ? "0" + start.getMinutes() : start.getMinutes();
     
     if(compact) {
         if(delta < day || start.getDate() == current.getDate()) {
             startObj.text(hours +":" + minutes);
         }
         else if (delta < year) {
             startObj.text(days[start.getMonth()] + " " + start.getDate());
         }
         else {
    		 startObj.text(start.getFullYear() + " " + days[start.getMonth()] + " " + start.getDate() +" at "+ hours +":" + minutes);
    	 }
     }
     else {
    	 if (delta < year) {
    		 startObj.text(days[start.getMonth()] + " " + start.getDate() +" at "+ hours +":" + minutes);
    	 }
    	 else {
    		 startObj.text(start.getFullYear() + " " + days[start.getMonth()] + " " + start.getDate() +" at "+ hours +":" + minutes);
    	 }
     }
     
     return duration;
}

$(document).ready(function() {

    if($("#id_timestamp").length) {

        var scheduled = new Date(parseInt($('#id_timestamp').val()));
        var hours = (scheduled.getHours() < 10) ? '0' + scheduled.getHours() : scheduled.getHours();
        var minutes = (scheduled.getMinutes() < 10) ? '0' + scheduled.getMinutes() : scheduled.getMinutes();
        var month = scheduled.getMonth() + 1;
        if (month < 10) {
            month = '0' + month;
        }

        $('#id_published_at').val(scheduled.getFullYear() + '-'+ month + '-'+
            scheduled.getDate() + ' '+ hours + ':'+ minutes + ':00');

        $('#id_published_at').datetimepicker({lang: 'en',
            'format': 'Y-m-d H:i', 'step': 15,
            onClose: function(current_time, inp) {
                try {
                    /*
                     * Date.parse() doesn't work so well cross browser. Using date.js seems overkill.
                     * so this solution from so http://stackoverflow.com/a/4680129/267540
                     */
                    var v = /(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})/.exec($("#id_published_at").val().trim())

                    if (v.length == 6) {
                        var dt = new Date();
                        dt.setYear(v[1]);
                        dt.setMonth(v[2]-1);
                        dt.setDate(v[3]);

                        dt.setHours(v[4]);
                        dt.setMinutes(v[5]);

                        if (dt) {
                            console.log(dt.valueOf());
                            $('#id_timestamp').val(dt.valueOf());
                        }
                        else {
                            console.log('trouble parsing date}');

                       }
                  }
                }catch (ex) 
                {
                }
            }
        });

    /**/
        try {
            CKEDITOR.replace('id_content', { 'allowedContent': true, 'height': '400px',
                             'contentsCss' : ['/assets/css/bootstrap.min.css', '/assets/css/main.css']});
        } catch (e) {
            $('#id_contents').css('height', '350px');
        }
    }
    else {
       $("#load-more").on('click',function(){
         $.get('/list/?page=' + $("#load-more").data('page') + '&type=' + $("#load-more").data("what"),
             function(resp) {
                 $("#load-more").data('page', parseInt( $("#load-more").data('page')) + 1);
                 $("#list-items").append(resp);
                 
                 $(".timestamp").each(function(){
                     show_timing($(this), false, $(this).hasClass('compact'));
                 });

             }
         );
       });
       if($(".timestamp").length) {
           $(".timestamp").each(function(){
               show_timing($(this), false, $(this).hasClass('compact'));
           });
           $(".timestamp").removeClass('hide');
       }
    }
});
