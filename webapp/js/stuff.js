var map;
var ajaxRequest;
var plotlist;
var plotlayers=[];
var geojsonLayer = new L.GeoJSON();
var get_url = "/mrsvc/get/";
var store_url = "/mrsvc/store/";
var count_url = "/mrsvc/count/";
var clickcnt;
var m1, m2;
var currentWayId;
var bingLayer, osmLayer;
var attrControl;
var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
var osmAttrib='Map data © OpenStreetMap contributors'
var t; 
var currentWayId = 0;

var DISABLEKEYBOARDHOOKS = false;

var geojsonMarkerOptions = {
    radius: 14,
    fillColor: "#ff7800",
    color: "#F00",
    weight: 4,
    opacity: 1,
    fillOpacity: 0.0
};

function getExtent(geojson) {
	var lats = [], lngs = [];
	if (!(geojson.geometry.coordinates && geojson.geometry.coordinates.length > 0)) {
		return false;
	}
	for (i in geojson.geometry.coordinates) {
		lats.push(geojson.geometry.coordinates[i][1]);
		lngs.push(geojson.geometry.coordinates[i][0]);
	}
	var minlat = Math.min.apply(Math, lats);
	var sw = new L.LatLng(Math.min.apply(Math, lats), Math.min.apply(Math, lngs));
	var ne = new L.LatLng(Math.max.apply(Math, lats), Math.max.apply(Math, lngs));
	return new L.LatLngBounds(sw, ne);
}

function msg(h, t) {
    // displays an info message. if the time is 0, you will have to provide a close button that calls msgClose() yourself.
    clearTimeout(t);
    $('#msgBox').html(h).fadeIn();
    $('#msgBox').css("display", "block");
    if(t!=0) t = setTimeout("msgClose()", t * 1000);
}

function dlg(h) {
    // displays a dialog. you are responsible for closing with $('#dlgBox').fadeOut()
    $('#dlgBox').html(h).fadeIn();
    $('#dlgBox').css("display", "block");
}

function msgClose() {
    $('#msgBox').fadeOut();
}

function dlgClose() {
    $('#dlgBox').fadeOut();
}


function getItem() {
    msg('Faites vos jeux...', 0);
    map.removeLayer(geojsonLayer);
    geojsonLayer = new L.GeoJSON();
    map.addLayer(geojsonLayer);
    $.getJSON(
        get_url,
        function(data) {
			currentWayId = data.features[0].properties['id'];
            var extent = getExtent(data.features[0]);
            geojsonLayer.addData(data.features[0]);$                                                                                      
            map.fitBounds(extent);
			var mqurl = 'http://open.mapquestapi.com/nominatim/v1/reverse?format=json&lat=' + map.getCenter().lat + ' &lon=' + map.getCenter().lng;
			//msg(mqurl, 3);
            msgClose()
			$.getJSON(mqurl, 
				function(data){
					var locstr = 'We\'re in ';
					locstr += data.address.county;
					locstr += data.address.county.toLowerCase().indexOf('county') > -1?'':' County';
					locstr += ', ' + data.address.state
					msg(locstr , 3);
				}
			);
			updateCounter();
        }
    );
};

function initmap() {
    map = new L.Map('map');
    osmLayer = new L.TileLayer(osmUrl, {attribution: osmAttrib});
    map.setView(new L.LatLng(40.0, -90.0),17);
    map.addLayer(osmLayer);
    map.addLayer(geojsonLayer);
    getItem();
    $.cookie('activelayer', 'osmLayer');
	
	// add keyboard hooks
    if (!DISABLEKEYBOARDHOOKS) {
        $(document).bind('keydown', function(e){
            switch (e.which) {
                case 81: //q
                    nextUp(1);
                    break;
                case 87: //w
                    nextUp(0);
                    break;
                case 69: //e
                    openIn('j');
                    break;
                case 82: //r
                    openIn('p');
                    break;
            }
        })
	};
	updateCounter();
};

function toggleLayers() {
	activeLayer = $.cookie('activelayer');
	if (activeLayer == "osmLayer") {
		map.removeLayer(osmLayer);
		map.addLayer(bingLayer);
		$.cookie('activelayer', 'bingLayer');	
	} else {
		map.removeLayer(bingLayer);
		map.addLayer(osmLayer);
		$.cookie('activelayer', 'osmLayer');
	}
}

function nextUp(i) {
	msg("OK, moving along...",1);
	$.ajax(store_url + currentWayId + '/' + i, {'type':'PUT'}).done(function(){setTimeout("getItem()", 1000)});
}

function openIn(editor) {
    //if (map.getZoom() < 14){
    //    msg("zoom in a little so we don't have to load a huge area from the API.", 3);
    //    return false;
    //};
    var bounds = map.getBounds();
    var sw = bounds.getSouthWest();
    var ne = bounds.getNorthEast();
	if (editor == 'j') { // JOSM
		//var JOSMurl = "http://127.0.0.1:8111/load_and_zoom?left=" + sw.lng + "&right=" + ne.lng + "&top=" + ne.lat + "&bottom=" + sw.lat + "&new_layer=0&select=node" + currentNodeId + ",way" + currentWayId;
		var JOSMurl = "http://127.0.0.1:8111/load_object?new_layer=true&objects=w" + currentWayId;
		// Use the .ajax JQ method to load the JOSM link unobtrusively and alert when the JOSM plugin is not running.
		$.ajax({
			url: JOSMurl,
			complete: function(t) {
				if (t.status!=200) {
					msg("JOSM remote control did not respond ("+t.status+"). Do you have JOSM running?", 2);
				} else {
					setTimeout("confirmRemap('j')", 4000);
				}
			}
		});
	} else if (editor == 'p') { // potlatch
		var PotlatchURL = 'http://www.openstreetmap.org/edit?editor=potlatch2&bbox=' + map.getBounds().toBBoxString();
		window.open(PotlatchURL);
        //msg("Potlatch does not support loading a single object so it is not well suited for this challenge, which sometimes involves editing very long way segments.",5)
		setTimeout("confirmRemap('p')", 4000)
	}
}

function confirmRemap(e) {
	dlg("The area is being loaded in " + (e=='j'?'JOSM':'Potlatch') + " now. Come back here after you do your edits.<br /><br />Did you fix it?<p><div class=button onClick=nextUp(1);$('#dlgBox').fadeOut()>YES</div><div class=button onClick=nextUp(0);$('#dlgBox').fadeOut()>NO , I FORGOT / GOT LAZY</div><div class=button onClick=nextUp(2);$('#dlgBox').fadeOut()>NO, UNFIXABLE (CONFUSING, COULDN'T SEE, TUNNEL)</div>");
}

function showAbout() {
	dlg("<strong>Help fix the main OpenStreetMap road network in the US, one way at a time!</strong><p>This website will highlight one way with no lanes=*.<p>You have three options:<p>1. Flag the way as OK (we do make mistakes);<br />2. Skip this one and leave it for someone else to fix;<br />3. Open this way in JOSM or Potlatch to fix it. (You have to have JOSM running and the remote control function enabled in the preferences for the JOSM link to work).<p>When you're done, the next way appears. Repeat ad infinitum.<p><small>A thing by <a href='mailto:m@rtijn.org'>Martijn van Exel</a></small><p><div class='button' onClick=\"dlgClose()\">OK</div>",0);
}

function updateCounter() {
	$.getJSON(
		count_url,
		function(data) {
			$('#counter').text(data[0]);
			$('#hrfix').text(data[1]);
			$('#dayfix').text(data[2]);
            $('#hrtouch').text(data[3]);
            $('#daytouch').text(data[4]);
		});	
}
