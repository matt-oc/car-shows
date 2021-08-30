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
  esq = new google.maps.Marker({
    map: map,
    position: new google.maps.LatLng(53.318399480787555, -7.666736316345829)
  });


  infoEsq.open(map, esq);
  google.maps.event.addDomListener(window, 'load', initMap);

  var clickmarker = new google.maps.Marker({
     draggable: true
 });

  google.maps.event.addListener(map, 'click', function(event) {

    esq.setMap(null)
    clickmarker.setPosition(event.latLng);
    clickmarker.setMap(map);
    clickmarker.setAnimation(google.maps.Animation.DROP);
    var lat = clickmarker.getPosition().lat();
    var lng = clickmarker.getPosition().lng();
    jQuery("#lat").val(lat);
    jQuery("#lng").val(lng)


});
}
