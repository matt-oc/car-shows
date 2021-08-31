function initMap() {

  var myOptions = {
    zoom: 7,
    scrollwheel: false,
    center: new google.maps.LatLng(53.318399480787555, -7.666736316345829),
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    styles: [{
      featureType: 'landscape.natural',
      elementType: 'all',
      stylers: [{
        color: '#f8f8f8',
        gamma: 5
      }]
    }]
  };
  map = new google.maps.Map(document.getElementById('gmap_canvas'), myOptions);


  if (window.location.href.split('/').slice(-2)[0] == "view_event") {
    let lat = document.getElementById('gmap_canvas').getAttribute('data-lat')
    let lng = document.getElementById('gmap_canvas').getAttribute('data-lng')
    def = new google.maps.Marker({
      map: map,
      position: new google.maps.LatLng(lat, lng)
    });
  } else if (window.location.href.substring(window.location.href.lastIndexOf('/') + 1) == "view_map") {
    let infowindow = new google.maps.InfoWindow();
let events = JSON.parse(document.getElementById('gmap_canvas').getAttribute('data-map'))
for (var i = 0; i < events.length; i++) {

    var marker = new google.maps.Marker({
        position: new google.maps.LatLng(events[i].lat, events[i].lng),
        map: map,
        title: events[i].event_name
    });

    google.maps.event.addListener(marker, 'click', (function(marker, i) {
        return function() {
            infowindow.setContent(events[i].event_name);
            infowindow.open(map, marker);
        }
    })(marker, i));
}
  }
  else {
    def = new google.maps.Marker({
      map: map,
      position: new google.maps.LatLng(53.318399480787555, -7.666736316345829)
    });

    google.maps.event.addDomListener(window, 'load', initMap);

    var clickmarker = new google.maps.Marker({
      draggable: true
    });

    google.maps.event.addListener(map, 'click', function(event) {

      def.setMap(null)
      clickmarker.setPosition(event.latLng);
      clickmarker.setMap(map);
      clickmarker.setAnimation(google.maps.Animation.DROP);
      var lat = clickmarker.getPosition().lat();
      var lng = clickmarker.getPosition().lng();
      jQuery("#lat").val(lat);
      jQuery("#lng").val(lng)
    });
  }

}
