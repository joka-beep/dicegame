function updateTime(time, divName)
{
    var datetime = new Date(time + "Z").getTime();
    document.getElementById(divName).innerHTML = time + "<br/>" + new Date(datetime)

    update(datetime, divName)
    setInterval(function(){ update(datetime, divName) }, 1000);
}

function update(datetime, divName)
{
    var now = new Date().getTime();
    var millisec_diff = datetime - now;
    var days = Math.floor(millisec_diff / (1000 * 60 * 60 * 24));
    var date_diff = new Date( millisec_diff );
    var output = "You are restricted for another <br />";

    if (days > 0){
        output += (days == 1 ? "day" : days + " days") + ", ";
    }
    if (date_diff.getHours() > 0) {
        output += date_diff.getHours() + (date_diff.getHours() == 1 ? " hour" : " hours") + " and ";
    }
    output += date_diff.getMinutes() + " minute" + (date_diff.getMinutes() == 1 ? "" : "s") + ".";

    document.getElementById(divName).innerHTML = (output);
}