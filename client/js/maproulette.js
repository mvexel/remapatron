$.ajax({
	async: false,
	url: 'js/config.js', 
	dataType: 'script'
}); // LOAD CONFIGURATION FILE

var map;
if (config.challenge.hasWay) var geojsonLayer = new L.GeoJSON();
if (config.challenge.hasNode) var geojsonPointLayer = new L.GeoJSON();
var bingLayer, osmLayer;
var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
var osmAttrib='Map data © OpenStreetMap contributors'
var t; 
var currentNodeId = 0;
var currentWayId = 0;

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

// Gets the next error and displays it on the map.
function getItem() {
    msg(config.strings.msgNextChallenge, 0)
    $.getJSON(
        config.geojsonserviceurl,
        function(data) {
			features = data.features;
			var points = [];
			var lines = [];
			if (features == null || features.length == 0 || !features) {return false;}
			for (f in features) {
				feature = features[f];
				if (features[f].geometry.type=="Point") {points.push(features[f])}
				else if (features[f].geometry.type=="LineString") {lines.push(features[f])}
			}
			if (config.challenge.hasWay) currentWayId = lines[0].properties['id'];
			if (config.challenge.hasNode) currentNodeId = points[0].properties['id'];
			// FIXME The popups currently don't work
			var popuphtml = '<big><ul>Tags</ul></big><br />'
            for (tag in data.features[0].properties.tags) {
                popuphtml += tag + ': ' + lines[0].properties.tags[tag] + '<br />';
            };
			if (config.challenge.hasNode) {
				geojsonPointLayer.addData(points[0]);
			};
			if (config.challenge.hasWay) {
				geojsonLayer.addData(lines[0]).bindPopup(popuphtml);//.openPopup();
	            var extent = getExtent(lines[0]);
				map.fitBounds(extent);
			};
			revGeocode();
			updateCounter();
        }
    );
};

function revGeocode() {
	var mqurl = 'http://open.mapquestapi.com/nominatim/v1/reverse?format=json&lat=' + map.getCenter().lat + ' &lon=' + map.getCenter().lng;

	//close any notifications that are still hanging out on the page.
    msgClose()

	// this next bit fires the RGC request and parses the result in a decent way, but it looks really ugly.
	$.getJSON(mqurl, 
		function(data){
			var locstr = 'We\'re ';
			locstr += 
				data.address.county ? 
				'in ' + data.address.county + 
				data.address.county.toLowerCase().indexOf('county') > -1?
				', ' :
				' County, ' :
				data.address.city ? 
				'in ' + data.address.city + ', ' : 
				data.address.town ? 
				data.address.town + ', ' : 
				data.address.hamlet ? 
				data.address.hamlet + ', ' : 
				'somewhere in ';
			locstr += ', ' + data.address.state?data.address.state:data.address.country
			
			// display a message saying where we are in the world
			msg(locstr , 3);
		}
	);
};

function initmap() {
	// initialize Leaflet map and tile layer objects
    map = new L.Map('map');
    osmLayer = new L.TileLayer(osmUrl, {attribution: osmAttrib});
    map.setView(new L.LatLng(40.0, -90.0),17);
    map.addLayer(osmLayer);

	// add the appropriate GeoJSON layers
    if (config.challenge.hasWay) map.addLayer(geojsonLayer);
    if (config.challenge.hasNode) map.addLayer(geojsonPointLayer);

	// get the first error
    getItem();
		
	// add keyboard hooks
    if (config.enablekeyboardhooks) {
        $(document).bind('keydown', function(e){
            switch (e.which) {
                case 81: //q
                    nextUp(config.fixflag.falsepositive);
                    break;
                case 87: //w
                    nextUp(config.fixflag.skip);
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
	
	// update the counters for the first time
	updateCounter();
};

function toggleLayers() {
	if (activeLayer == "osmLayer") {
		map.removeLayer(osmLayer);
		map.addLayer(bingLayer);
	} else {
		map.removeLayer(bingLayer);
		map.addLayer(osmLayer);
	}
}

// This function displays a message that we're moving on to the next error, stores the result of the confirmation dialog in the database, and triggers loading the next challenge.
function nextUp(i) {
	msg(config.strings.msgMovingOnToNextChallenge,1);
	$.ajax(config.storeresulturl + currentWayId + '/' + i, {'type':'PUT'}).done(function(){setTimeout("getItem()", 1000)});
}

// Opens the current highlighted OSM objects in JOSM or Potlatch.
function openIn(editor) {
    if (map.getZoom() < 14){
        msg(config.strings.msgZoomInForEdit, 3);
        return false;
    };
    var bounds = map.getBounds();
    var sw = bounds.getSouthWest();
    var ne = bounds.getNorthEast();
	if (editor == 'j') { // JOSM
		var JOSMurl = "http://127.0.0.1:8111/load_and_zoom?left=" + sw.lng + "&right=" + ne.lng + "&top=" + ne.lat + "&bottom=" + sw.lat + "&new_layer=0&select=node" + currentWayId + ",way" + currentWayId;
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
		setTimeout("confirmRemap('p')", 4000)
	}
}

// This function shows the dialog asking the user for confirmation that he has fixed the bug in the editor.
function confirmRemap(e) {
	dlg("The area is being loaded in " + (e=='j'?'JOSM':'Potlatch') + " now. Come back here after you do your edits.<br /><br />Did you fix it?<p><div class=button onClick=nextUp(" + config.fixflag.fixed + ");$('#dlgBox').fadeOut()>YES</div><div class=button onClick=nextUp(" + config.fixflag.notfixed + ");$('#dlgBox').fadeOut()>NO :(</div><div class=button onClick=nextUp(" + config.fixflag.someonebeatme + ");$('#dlgBox').fadeOut()>SOMEONE BEAT ME TO IT</div><div class=button onClick=nextUp(" + config.fixflag.noerrorafterall + ");$('#dlgBox').fadeOut()>IT WAS NOT AN ERROR AFTER ALL</div>");
}

// This function shows the about window. 
// FIXME the string should be in the config file.
function showAbout() {
	dlg("<strong>Help fix the main OpenStreetMap road network in the US, one way at a time!</strong><p>This website will highlight one unconnected way.<p>You have three options:<p>1. Flag the way as OK (we do make mistakes);<br />2. Skip this one and leave it for someone else to fix;<br />3. Open this area in JOSM or Potlatch to fix it. (You have to have JOSM running and the remote control function enabled in the preferences for the JOSM link to work).<p>When you're done, the next way appears. Repeat ad infinitum.<p><small>A thing by <a href='mailto:m@rtijn.org'>Martijn van Exel</a></small><p><div class='button' onClick=\"dlgClose()\">OK</div>",0);
}

// this function gets the latest counts for total remaining errors, amount fixed in last hr and amount fixed in last day and updates the page with the results.
function updateCounter() {
	$.getJSON(
		config.counturl,
		function(data) {
			$('#counter').text(data[0]);
			$('#hrfix').text(data[1]);
			$('#dayfix').text(data[2]);
		});	
}