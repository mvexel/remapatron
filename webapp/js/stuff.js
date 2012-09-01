var map;
var ajaxRequest;
var plotlist;
var plotlayers=[];
var geojsonLayer = new L.GeoJSON();
var url = "http://lima.schaaltreinen.nl/remappingservice/"; 
var clickcnt;
var m1, m2;
var way_id;
var bingLayer, osmLayer;
var attrControl;
var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
var osmAttrib='Map data © OpenStreetMap contributors'
var t; 

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
    $.getJSON(
        url,
        function(data) {
			way_id = data.properties['id'];
			geojsonLayer.addGeoJSON(data);
			var extent = getExtent(data);
			map.fitBounds(extent);
			var mqurl = 'http://open.mapquestapi.com/nominatim/v1/reverse?format=json&lat=' + map.getCenter().lat + ' &lon=' + map.getCenter().lng;
			//msg(mqurl, 3);
			$.getJSON(mqurl, 
				function(data){
					var locstr = 'We\'re in ';
					locstr += data.address.county;
					locstr += data.address.county.toLowerCase().indexOf('county') > -1?'':' County';
					locstr += ', ' + data.address.state
					msg(locstr , 3);
				}
			);
        }
    );
};

function initmap() {
    map = new L.Map('map');
    bingLayer = new L.TileLayer.Bing(
		"AncYMYJDvHMmYPXT7mJcpCeYxGEVcJFj_StK8PO3ih8WgjvfHzuvnyjc_iRFXqN2",
		"Aerial"
    );
    osmLayer = new L.TileLayer(osmUrl, {attribution: osmAttrib});
    map.setView(new L.LatLng(40.0, -90.0),17);
    map.addLayer(osmLayer);
    
//	var baseLayers = {
//		"Bing Aerial": bingLayer,
//		"OpenStreetMap": osmLayer/
//	};

//    layersControl = new L.Control.Layers(baseLayers);
//    map.addControl(layersControl);
    
    map.addLayer(geojsonLayer);
    getItem();
    $.cookie('activelayer', 'osmLayer');
	
	// add keyboard hooks
	$(document).bind('keydown', function(e){
		switch (e.which) {
			case 81: //q
				nextUp(1);
				break;
			case 87: //w
				nextUp(-1);
				break;
			case 69: //e
				openIn('j');
				break;
			case 82: //r
				openIn('p');
				break;
			case 83: //s
				toggleLayers();
				break;
			//default:
			//	msg(e.which);
		}
	});
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
//		map.attributionControl.addAttribution(osmAttrib);
	}
}

function startSelect() {
    $("#map").addClass("xhair");
    msg("Click on the map to set the start of the bridge", 3);
    map.on('click', function(e) {
		msg("Now click on the map to set the end of the bridge", 3);
		m1 = new L.CircleMarker(e.latlng);
		map.addLayer(m1)
		map.on('click', function(e) {
			m2 = new L.CircleMarker(e.latlng);
			map.addLayer(m2)
			stopSelect()
        });
    });
}

function stopSelect() {
    $("#map").removeClass("xhair");
    savedMsg();
    clickcnt=0;
	t = setTimeout("getItem()", 1000);
}

function nextUp(i) {
	msg("OK, moving along...",1);
	$.ajax(url + way_id + '/' + i, {'type':'PUT'}).done(function(){setTimeout("getItem()", 1000)});
}

function savedMsg() {
//    msg('Saved! thx', 0.8);
    msg('This is alpha and nothing is saved yet!', 1);
}

function openIn(editor) {
    if (map.getZoom() < 14){
        msg("zoom in a little so we don't have to load a huge area from the API.", 3);
        return false;
    };
    var bounds = map.getBounds();
    var sw = bounds.getSouthWest();
    var ne = bounds.getNorthEast();
	if (editor == 'j') { // JOSM
		var JOSMurl = "http://127.0.0.1:8111/load_and_zoom?left=" + sw.lng + "&right=" + ne.lng + "&top=" + ne.lat + "&bottom=" + sw.lat + "&new_layer=0"
		// Use the .ajax JQ method to load the JOSM link unobtrusively and alert when the JOSM plugin is not running.
		$.ajax({
			url: JOSMurl,
			complete: function(t) {
				if (t.status!=200) {
					msg("JOSM remote control did not respond ("+t.status+"). Do you have JOSM running?", 2);
				} else {
					setTimeout(confirmRemap(editor), 4000);
				}
			}
		});
	} else if (editor == 'p') { // potlatch
		var PotlatchURL = 'http://www.openstreetmap.org/edit?editor=potlatch2&bbox=' + map.getBounds().toBBoxString();
		window.open(PotlatchURL);
		setTimeout(confirmRemap(editor), 4000)
	}
}

function confirmRemap(e) {
	dlg("The area is being loaded in " + (e=='j'?'JOSM':'Potlatch') + " now. Come back here after you do your edits.<br /><br />Did you remap the way?<p><div class=button onClick=nextUp(3);$('#dlgBox').fadeOut()>YES</div><div class=button onClick=nextUp(0);$('#dlgBox').fadeOut()>NO :(</div>");
}

function showAbout() {
	dlg("<strong>Help remap the main OpenStreetMap road network in the US, one way at a time!</strong><p>This website will show you one single deleted way that is likely not remapped yet.<p>You have three options:<p>1. Flag the way as already remapped;<br />2. Skip this one and leave it for someone else to remap;<br />3. Open this area in JOSM or Potlatch to remap it. (You have to have JOSM running and the remote control function enabled in the preferences for the JOSM link to work).<p>When you're done, the next way appears. Repeat ad infinitum.<p><small>A thing by <a href='mailto:m@rtijn.org'>Martijn van Exel</a></small><p><div class='button' onClick=\"dlgClose()\">OK</div>",0);
}
