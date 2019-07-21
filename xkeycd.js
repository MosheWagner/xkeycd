var availableTags = [];
var comic_scores = {};
var comic_links = {};

var TRANSCRIPT_FACTOR = 4;
var EXPLANATION_FACTOR = 1;
var MAX_RES = 5;

$.getJSON("scores.json", function(json) {
    $.each( json, function( key, val ) {
        availableTags.push(key);
        comic_scores[key] = val;
    });
    
    availableTags.sort();
});

$.getJSON("comic_images.json", function(json) {
    $.each( json, function( key, val ) {
        comic_links[key] = val;
    });
});

$( function() {
    $( "#kws" ).autocomplete({
      minLength: 3,
      delay: 200,
      source: availableTags,
      select: function( event, ui ) {
        scores = {};
          
        var keyword = ui.item.value;
        $.each(comic_scores[keyword], function( comic_id, kw_score ) {
            scores[comic_id] = TRANSCRIPT_FACTOR * kw_score.transcript_score || 0 + EXPLANATION_FACTOR * kw_score.explanation_score || 0;
        });
        
        scoresSorted = Object.keys(scores).sort(function(a,b){return scores[a]-scores[b]}).reverse().slice(0, MAX_RES);
        // console.log(scoresSorted);   
        
        $('#images').empty();
        scoresSorted.forEach(function(comic_id) {
             console.log(comic_id);
             console.log(String(comic_id));
             
             //$('#images').append('<iframe frameborder="0" scrolling="no" width="100%" height="100%" src=' + "http://xkcd.com/" + String(comic_id) + ' name="imgbox" id="imgbox"></iframe><br />'); 
             
             $('#images').append('<li>' + 'XKCD ' + String(comic_id) + ': <br><img src=' + comic_links[String(comic_id)] + '><br><br><br>');
        } );
      }
    });
} );