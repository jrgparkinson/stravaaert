$(function() {
    $('#upload-file-btn').click(function() {
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



                var gpx = "/gpx/" + data["filename"]; // URL to your GPX file or the GPX itself
                new L.GPX(gpx, {async: true}).on('loaded', function(e) {
                  map.fitBounds(e.target.getBounds());
                }).addTo(map);

                    $("#downloadGPX").attr("href", "/download/" + data["filename"] + "/" + data["upload_name"]);
                    $("#downloadGPX").css("display", "inline");

            },
        });
    });
});