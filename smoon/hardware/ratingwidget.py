from turbogears.widgets import Widget, mochikit

class RatingWidget(Widget):
    """
    this widget has no call back.
    """
    name = "RatingWidget"
    javascript = [mochikit]
    template = """
        <script type="text/javascript"><![CDATA[
var NUMBER_OF_STARS = ${num};

function displayHover(ratingId, star)
{
    for (var i = 0; i <= star; i++)
    {
        var starI = document.getElementById('star_'+ratingId+'_'+i)
        starI.setAttribute('src', '/static/images/stars/rating_over.gif');
    }
}

function displayNormal(ratingId, star)
{
    for (var i = 0; i <= star; i++)
    {
        var status = document.getElementById('star_'+ratingId+'_'+i).className;
        var starI = document.getElementById('star_'+ratingId+'_'+i);
        starI.setAttribute('src', '/static/images/stars/rating_'+status+'.gif');
    }
}

function submitRating(widgetId, starNbr)
{
    doSimpleXMLHttpRequest("${href}",
       { 'ratingID': widgetId, 'value': parseInt(starNbr)+1});
     for (var i = 0; i <= NUMBER_OF_STARS; i++)
     {
       var star = document.getElementById('star_'+widgetId+'_'+i)
       if (i <= starNbr) {
         star.setAttribute('src', '/static/images/stars/rating_on.gif');
         star.className = 'on';
       } else {
         star.setAttribute('src', '/static/images/stars/rating_off.gif');
         star.className = 'off';
       }
     }
     displayHover(widgetId, starNbr);
}

connect(window, "onload", function() {
    var ratings = document.getElementsByTagName('div');
    for (var i = 0; i < ratings.length; i++)
    {
        if (ratings[i].className != '${update}')
            continue;
            
        var rating = ratings[i].firstChild.nodeValue;
        ratings[i].removeChild(ratings[i].firstChild);
        if (rating > NUMBER_OF_STARS)
            rating = NUMBER_OF_STARS;
        if (rating < 0)
            rating = 0;
        for (var j = 0; j < NUMBER_OF_STARS; j++)
        {
            var star = document.createElement('img');
            if (rating >= 1)
            {
                star.setAttribute('src', '/static/images/stars/rating_on.gif');
                star.className = 'on';
                rating-=1;
            }
            else
            {
                star.setAttribute('src', '/static/images/stars/rating_off.gif');
                star.className = 'off';
            }
            var widgetId = ratings[i].getAttribute('id');
            star.setAttribute('id', 'star_'+widgetId+'_'+j);
            star.onmouseover = new Function("env", "displayHover('"+widgetId+"', '"+j+"');");
            star.onmouseout = new Function("env", "displayNormal('"+widgetId+"', '"+j+"');");
            star.onclick = new Function("env", "submitRating('"+widgetId+"', '"+j+"');");
            ratings[i].appendChild(star);
        } 
    }
});

//]]>
        </script>
    """
    params = ["update", "href", "num"]
    params_doc = {
        "update":"div class name to be replaced",
        "href":"remote method href",
        "num" : "number of rating levels",
        }
