(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-81694900-1', 'auto');
ga('send', 'pageview');

var search_timer = 0;

function search() {
	var q = $("#search").val();
	if (q.length == 0) {
		$(".container *").show();
	} else {
		q = q.toLowerCase().split(" ");
		$(".container *").each(function() {
			var show = true;
			var text = $(this).text().toLowerCase();
			for (var i = 0;i < q.length;i++) {
				if (text.indexOf(q[i]) == -1) {
					show = false;
					break;
				}
			}
			if (show) {
				$(this).show();
			} else {
				$(this).hide();
			}
		});
	}
}

$(document).ready(function() {
	$(".button-collapse").sideNav();
	$('select').material_select();
	$('ul.tabs').tabs();
	$("#search").keyup(function(e) {
		clearTimeout(search_timer);
		search_timer = setTimeout(search, 80);
	});

	$(".close").click(function(e) {
		$("#search").val("");
		$("#search").keyup();
	});
});