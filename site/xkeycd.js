const availableTags = [];
const comic_scores = {};

const comic_titles = {};
const comic_links = {};
const comic_tooltips = {};

const TRANSCRIPT_FACTOR = 4;
const EXPLANATION_FACTOR = 1;
const MAX_RES = 10;

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

function showComics(keywords) {
	const scores = {};
	for (const keyword of keywords) {
		$.each(comic_scores[keyword], function(comic_id, kw_score) {
			prev_score = scores[comic_id] || 0;
            scores[comic_id] = prev_score + (TRANSCRIPT_FACTOR * kw_score.transcript_score || 0 + EXPLANATION_FACTOR * kw_score.explanation_score || 0);
        });
	}
	
	 scoresSorted = Object.keys(scores).sort(function(a,b){return scores[a]-scores[b]}).reverse().slice(0, MAX_RES);
	// console.log(scoresSorted);   
        
	$('#images').empty();
	scoresSorted.forEach(function(comic_id) {
		const str_id = String(comic_id)
		 $('#images').append('<li>' + '<a href="https://xkcd.com/' + str_id + '">' +  'XKCD ' + str_id + ': ' + comic_titles[str_id] + '</a> <br><img src=' + comic_links[str_id] + '><br><small>' + comic_tooltips[str_id] + '</small><br><br><br><br>');
	} );
}

function addKeyword(keyword) {
	$('#tags-input').tagsinput('add', keyword);
}

$( function() {
	$('#tags-input').tagsinput();
	
    $("#kws" ).autocomplete({
      minLength: 3,
      delay: 200,
      source: availableTags,
      select: function( event, ui) {
		  addKeyword($(this).val());
		  $(this).val(''); return false;
	  }
    });
	
	$('#kws').keypress(function(event) {
        if (event.keyCode == 13) {
		  addKeyword($(this).val());
		  $(this).val('');
		  $(this).blur(); 
        }
    });
	
	$('#tags-input').on('itemAdded', function(event) {
	  showComics($('#tags-input').tagsinput('items'));
	});
	
	$('#tags-input').on('itemRemoved', function(event) {
	  showComics($('#tags-input').tagsinput('items'));
	});
} );