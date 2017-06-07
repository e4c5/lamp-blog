$(document).ready(function(){

    /**
     * Times are saved in the database in milli seconds
     * 
     * We need to show them as days, hours and minutes etc. However for
     * speed calculations we will need a consistent unit so we will
     * work in seconds. As such the return value will be the 
     * duration of the trip in seconds.
     * 
     * @param secs
     * @returns {String}
     */
    function show_timing(startObj, endObj, compact)
    {
        var day = 1000 * 60 * 60 * 24;
        var year = day * 365;
        var days = ["Jan","Feb","March","April","May","June","July","Aug","Sept","Oct","Nov","Dec"];
        var duration = 0;
    
        var current =  new Date();                        
        var start = new Date(parseInt( ( startObj.text() <12300000000 )
                                        ? startObj.text() * 1000  :  startObj.text()  ));
         
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
    

    if($(".timestamp").length) {
        $(".timestamp").each(function(){
            show_timing($(this), false, $(this).hasClass('compact'));
            $(this).show()
        });
    }
});