var overlay;
var map;

function makeMap() {
    if (!map) {
        document.getElementById('mapContainer').innerHTML = "<div id='map' style='width: 100%;'></div>";
        console.log("Map is undefined, creating");
        var placeholder_lat_ln = getPlaceHolderLatLng();
        map = L.map('map').setView([placeholder_lat_ln.lat, placeholder_lat_ln.lng], 16);

        L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="http://www.osm.org">OpenStreetMap</a>'
        }).addTo(map);

        
    } else {
        console.log("Map already exists")
    }
   
}

function updateMap(do_fit) {
    var form_data = new FormData($('#upload-file')[0]);
    console.log(form_data);
    $.ajax({
        type: 'POST',
        url: '/uploadajax',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        success: function (data) {
            console.log('Success!');
            console.log(data);

            makeMap();

            if (overlay) {
                map.removeLayer(overlay);
                overlay = undefined;
            }

            $("#downloadGPX").css("display", "inline");
            
            mapChanged(data["filename"], do_fit);


            // Here the events for zooming and dragging
            map.on('zoomend', function () {

            });
            map.on('dragend', function () {

                mapChanged(data["filename"]);
            });

            
            // $("#downloadGPX").attr("onclick", "location.href='/retrieve/file/" + data["filename"] + "/" + position + "/" + scale + "/" + data["upload_name"] + "/'");
            $("#downloadGPX").attr("onclick", "location.href='" + 
            makeLink(data["filename"], data["upload_name"]) + "'");
        },
    });
}

function getPlaceHolderLatLng() {
    var posPlaceholder = $("#position").attr('placeholder');
       var parts = posPlaceholder.split(',');
       return {"lat": parts[0], "lng": parts[1]};
}

function makeLink(filename, download_name) {
    var scale = $("#scale").val() ? $("#scale").val() : $("#scale").attr('placeholder');

    var position;
    if (map && overlay) {
        position = map.getCenter()
    } else {
       position = getPlaceHolderLatLng();
    }
    var posString = position.lat + "," + position.lng;

    var algorithm = $("#algorithm option:selected").val();

    $("#position").val(posString);
    $("#scale").val(scale);

    return "/retrieve/file/" + filename + "/" + posString + "/" + scale + "/" + algorithm + "/" + download_name + "/";

}

function mapChanged(filename, do_fit) {

    var gpx = makeLink(filename, "DUMMY");

//     addToMap(map, url, do_fit);

// }

// // function addToMap(map, filename, position, scale, do_fit) {
//     // var gpx = "/retrieve/GPX/" + filename + "/" + position + "/" + scale + "/downloadName/";
// function addToMap(map, gpx, do_fit) {
    console.log(gpx);
    if (overlay != undefined) { map.removeLayer(overlay); }
    overlay = new L.GPX(gpx, { async: true }).on('loaded', function (e) {
        if (do_fit) {
            map.fitBounds(e.target.getBounds());
        }
    }).addTo(map);

   

    return overlay
}


$(function () {
    $('#convert').click(function () {
        console.log("Convert clicked!");
        var mapExists = map != undefined;
        updateMap(!mapExists);
    });


    $(document).ready(function() {
        makeMap();
       
    });

});

