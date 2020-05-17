var overlay;
var map;
var xml;
var prev_center;
var prev_scale;
var current_file;
var current_algorithm;

function makeMap() {
    if (!map) {
        document.getElementById('mapContainer').innerHTML = "<div id='map' style='width: 100%;'></div>";
        console.log("Map is undefined, creating");
        var location = getEnteredLocation();
        map = L.map('map').setView([location.lat, location.lng], 16);

        L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="http://www.osm.org">OpenStreetMap</a>'
        }).addTo(map);


    } else {
        console.log("Map already exists")
    }

}

function convertImage(do_fit) {
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

            if (data["error"]) {
                alert(data["error"]);
            } else {

                $("#file").attr("data-filename", data["filename"]);
                $("#file").attr("data-downloadname", data["upload_name"]);

                current_file = $("#file").val();
                current_algorithm = $("#algorithm option:selected").val();
                // alert(current_file);



                makeMap();

                if (overlay) {
                    map.removeLayer(overlay);
                    overlay = undefined;
                }

                $("#downloadGPX").css("display", "inline");

                mapChanged(do_fit);

                // Here the events for zooming and dragging
                map.on('zoomend', function () {

                });
                map.on('dragend', function () {
                    // Update position textbox with new map location
                    var position = map.getCenter()
                    var posString = position.lat + "," + position.lng;
                    $("#position").val(posString);

                    // Update overlay
                    mapChanged();
                });

                

            }
        },
    });
}

function downloadGPX() {
    var filename = $("#file").attr("data-downloadname") + ".gpx";
    var text = $("#gpxData").html()

    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}

function getEnteredLocation() {
    var location = $("#position").val();
    console.log("Location:" + String(location));
    if (!location) {
        location = $("#position").attr('placeholder');
        console.log("Using placeholder location:" + String(location));
    }
    var parts = location.split(',');
    return { "lat": parts[0], "lng": parts[1] };
}

function getPlaceHolderLatLng() {
    var posPlaceholder = $("#position").attr('placeholder');
    var parts = posPlaceholder.split(',');
    return { "lat": parts[0], "lng": parts[1] };
}

function makeLink(filename, download_name) {
    var scale = $("#scale").val() ? $("#scale").val() : $("#scale").attr('placeholder');
    var position = getEnteredLocation();
    var posString = position.lat + "," + position.lng;
    var algorithm = $("#algorithm option:selected").val();

    $("#position").val(posString);
    $("#scale").val(scale);

    return "/retrieve/file/" + filename + "/" + posString + "/" + scale + "/" + algorithm + "/" + download_name + "/";

}

function mapChanged(do_fit) {
    var filename = $("#file").attr("data-filename");

    var gpx = makeLink(filename, "DUMMY");


    if (overlay == undefined) {
        console.log("Loading: " + gpx);

        // Get GPX
        $.ajax({
            type: 'GET',
            url: gpx,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                // console.log(data);

                $("#gpxData").html(data);

                xml = $.parseXML(data),
                    // $xml = $( xmlDoc ),
                    // $title = $xml.find( "title" );

                    overlay = new L.GPX($("#gpxData").html(),
                        {
                            async: true,
                            marker_options: {
                                startIconUrl: undefined, // 'static/pin-icon-start.png',
                                endIconUrl: undefined, //'static/pin-icon-end.png',
                                shadowUrl: 'static/pin-shadow.png'
                            },
                            display_wpt: false
                        } // turn off icons
                    ).on('loaded', function (e) {
                        if (do_fit) {
                            map.fitBounds(e.target.getBounds());
                        }
                        $("#loading").css("display", "none");
                    }).addTo(map);

                    $("#loading").css("display", "none");

            }
        });

      


    } else {
        // Move overlay with JS
        // map.removeLayer(overlay); 
        var $xmlObj = $(xml);

        // Compute offset: previous center - new map center
        var offset = {
            'lat': prev_center.lat - map.getCenter().lat,
            'lon': prev_center.lng - map.getCenter().lng
        };
        console.log("offset: " + String(offset));

        var newScale = $("#scale").val();
        var scaleFactor = newScale / prev_scale;
        console.log("Scale factor: " + scaleFactor);

        $xmlObj.find('trkpt').each(function (index) {
            // var lat = $(this).find('lat').text();
            // console.log($(this).attr('lat'));
            // var old_lat = $(this).attr('lat');
            // var new_lat  = prev_center.lat + (Number($(this).attr('lat')) - prev_center.lat)*scaleFactor 
            // - offset.lat;
            // console.log("Old lat: " + old_lat + " new_lat: " + new_lat)
            $(this).attr('lat', prev_center.lat + (Number($(this).attr('lat')) - prev_center.lat) * scaleFactor
                - offset.lat);
            $(this).attr('lon', prev_center.lng + (Number($(this).attr('lon')) - prev_center.lng) * scaleFactor
                - offset.lon);
        });

        // manipulate xml


        // var xmlHeader = '<?xml version="1.0" encoding="iso-8859-1"?>'
        // var xmlDocumentString = xmlHeader + $xmlObj.html();
        var xmlString;
        //IE
        if (window.ActiveXObject) {
            xmlString = xml.xml;
        }
        // code for Mozilla, Firefox, Opera, etc.
        else {
            xmlString = (new XMLSerializer()).serializeToString(xml);
        }
        // var xmlString = $xmlObj.html();

        $("#gpxData").html(xmlString);

        addOverlay(false);

        $("#loading").css("display", "none");

    }

    prev_center = map.getCenter();
    prev_scale = $("#scale").val();

    return overlay
}

function addOverlay(do_fit) {
    // console.log($("#gpxData").html());
    if (overlay) {
        map.removeLayer(overlay);
    }
    overlay = new L.GPX($("#gpxData").html(),
        {
            async: true,
            marker_options: {
                startIconUrl: undefined, // 'static/pin-icon-start.png',
                endIconUrl: undefined, //'static/pin-icon-end.png',
                shadowUrl: 'static/pin-shadow.png'
            },
        }
    ).on('loaded', function (e) {
        if (do_fit) {
            map.fitBounds(e.target.getBounds());
        }
    }).addTo(map);
}

$(function () {
    $('#convert').click(function () {
        console.log("Convert clicked!");
        $("#loading").css("display", "block");

        // If overlay already exists and file/algorithm hasn't changed, just move existing overlay
        if (overlay && $("#file").val() == current_file
            && current_algorithm == $("#algorithm option:selected").val()) {
            mapChanged();
        } else {
            var mapExists = map != undefined;
            convertImage(!mapExists);
        }
    });

    $('#downloadGPX').click(downloadGPX);


    $(document).ready(function () {
        makeMap();

    });

    document.querySelector('.custom-file-input').addEventListener('change', function (e) {
        var fileName = document.getElementById("file").files[0].name;
        var nextSibling = e.target.nextElementSibling
        nextSibling.innerText = fileName
    })
});


function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        alert("Geolocation is not supported by your browser.");
    }
}

function showPosition(position) {
    $("#position").val(position.coords.latitude + "," + position.coords.longitude);
    map.panTo(new L.LatLng(position.coords.latitude, position.coords.longitude));

    // Update overlay
    if (overlay) {
        mapChanged(false);
        console.log("Move overlay");
    } else {
        console.log("No overlay to move");
    }
}


