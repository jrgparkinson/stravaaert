function updateMap() {
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

            document.getElementById('mapContainer').innerHTML = "<div id='map' style='width: 100%; height: 100%;'></div>";

var map = L.map('map');
L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: 'Map data &copy; <a href="http://www.osm.org">OpenStreetMap</a>'}).addTo(map);

            $("#downloadGPX").css("display", "inline");
            $("#positionControls").css("display", "inline");
            var position = $("#topLeft").val();
            var scale = $("#scale").val();

            var gpx = "/retrieve/GPX/" + data["filename"] + "/" + position + "/" + scale + "/downloadName/";
            new L.GPX(gpx, {async: true}).on('loaded', function(e) {
              map.fitBounds(e.target.getBounds());
            }).addTo(map);

                $("#downloadGPX").attr("href", "/retrieve/file" + data["filename"] + "/" + position + "/" + scale + "/" + data["upload_name"]);


        },
    });
}


$(function() {
    $('#upload-file-btn').click(function() {
        updateMap();
    });

    $('#updatePosition').click(function() {
        updateMap();
    });

});