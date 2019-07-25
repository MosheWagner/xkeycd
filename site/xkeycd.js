var availableTags = [];
var comic_scores = {};

var comic_titles = {};
var comic_links = {};
var comic_tooltips = {};

var TRANSCRIPT_FACTOR = 4;
var EXPLANATION_FACTOR = 1;
var MAX_RES = 10;

$.getJSON("scores.json", function(json) {
    $.each( json, function( key, val ) {
        availableTags.push(key);
        comic_scores[key] = val;
    });
    
    availableTags.sort();
});

$.getJSON("comics_meta.json", function(json) {
    $.each( json, function( key, val ) {
        comic_titles[key] = val.title_text;
        comic_links[key] = val.image_link;
        comic_tooltips[key] = val.tooltip;
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
            var str_id = String(comic_id)
             $('#images').append('<li>' + '<a href="https://xkcd.com/' + str_id + '">' +  'XKCD ' + str_id + ': ' + comic_titles[str_id] + '</a> <br><img src=' + comic_links[str_id] + '><br><small>' + comic_tooltips[str_id] + '</small><br><br><br><br>');
        } );
      }
    });
} );