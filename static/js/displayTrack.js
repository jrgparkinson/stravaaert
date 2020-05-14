var overlay;
var map;

function updateMap(do_fit) {
    var form_data = new FormData($('#upload-file')[0]);
    $.ajax({
        type: 'POST',
        url: '/uploadajax',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            console.log('Success!');
            console.log(data);

           

            if (!map) {
                document.getElementById('mapContainer').innerHTML = "<div id='map' style='width: 100%; height: 100%;'></div>";
                console.log("Map is undefined, creating");
                map = L.map('map');
                        
                L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: 'Map data &copy; <a href="http://www.osm.org">OpenStreetMap</a>'}).addTo(map);
            } else {
                console.log("Map already exists")
            }

            if (overlay) {
                map.removeLayer(overlay);
                overlay = undefined;
            }

            $("#downloadGPX").css("display", "inline");
            $("#positionControls").css("display", "inline");
            var position = $("#position").val();
            var scale = $("#scale").val();

            var gpx = "/retrieve/GPX/" + data["filename"] + "/" + position + "/" + scale + "/downloadName/";
            overlay = new L.GPX(gpx, {async: true}).on('loaded', function(e) {
                if (do_fit){
                    map.fitBounds(e.target.getBounds());
                }
            }).addTo(map);

            // Here the events for zooming and dragging
            map.on('zoomend', function() {
                // stuff here when user zooms the map...
                map.removeLayer(overlay);
                var position = map.getCenter();
                var posString = position.lat + "," + position.lng;
                addToMap(map, data["filename"], posString, scale);
            });
            map.on('dragend', function() {
                // stuff here when user drags the map...  
                map.removeLayer(overlay);  
                var position = map.getCenter();
                var posString = position.lat + "," + position.lng;
                addToMap(map, data["filename"], posString, scale);
            });

            $("#downloadGPX").attr("href", "/retrieve/file/" + data["filename"] + "/" + position + "/" + scale + "/" + data["upload_name"] + "/");


        },
    });
}

function addToMap(map, filename, position, scale) {
    var gpx = "/retrieve/GPX/" + filename + "/" + position + "/" + scale + "/downloadName/";
    console.log(gpx);
    if (overlay != undefined) { map.removeLayer(overlay); }
    overlay = new L.GPX(gpx, {async: true}).addTo(map);

    $("#position").val(position);
    $("#scale").val(scale);

    return overlay
}


$(function() {
    $('#upload-file-btn').click(function() {
        updateMap(true);
        console.log("overlay: ");
        console.log(overlay);
        // map.fitBounds(overlay.getBounds());
    });

    $('#updatePosition').click(function() {
        updateMap(false);
    });

});