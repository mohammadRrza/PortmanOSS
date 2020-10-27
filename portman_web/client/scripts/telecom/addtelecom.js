angular.module('portman.addtelecom', ['myModule'])

    .config(function ($stateProvider) {
        $stateProvider
            .state('add-telecom', {
                url: '/add-telecom/:telecom_id?',
                views: {
                    'content': {
                        templateUrl: 'templates/telecom/add-telecom.html',
                          
                        controller: 'AddTelecomController'
                    }
                }
            });
    })
    .controller('AddTelecomController', function ($scope, fetchResult, $stateParams, $compile, ip) {
        $scope.btn_text = "Submit";
        $scope.city = '';
        $scope.lat = 32;
        $scope.long = 53;
        $scope.marker = '';

    
        $scope.getProvince = function(query){
               
            return fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/city/?parent=all',
                params : {
                    city_name : query
                }
            }).then(function (result) {
                if(result.data.results){
                    return result.data.results ;}
                    return [];
                 
                   
                }, function (err) {
                }
            );
}
        $scope.getProvince();
      

        $scope.loadMap = function () {

            var mapOptions = {
                zoom: 6 ,
                center: new google.maps.LatLng($scope.lat, $scope.long),
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                scrollwheel: false,
                zoomControl: true,
                zoomControlOptions: {
                    style: google.maps.ZoomControlStyle.LARGE,
                    position: google.maps.ControlPosition.RIGHT_CENTER
                }
            };

            $scope.map = new google.maps.Map(document.getElementById('map'), mapOptions);

            google.maps.event.addListener($scope.map, 'click', function (event) {
                $scope.lat = event.latLng.lat();
                $scope.long = event.latLng.lng();
                $('#telecom_long').val($scope.long);
                $('#telecom_lat').val($scope.lat);
                placeMarker(event.latLng);
            });

            function placeMarker(location) {
                if($scope.marker!='')
                    $scope.marker.setMap(null);
                var marker = new google.maps.Marker({
                    position: location,
                    map: $scope.map
                });
                $scope.marker = marker;
            };
        };
        $scope.loadMap();
         $scope.show_city = false;
        $scope.selectCity = function (city_id) {
          
            $scope.city = $scope.selectedCity0.id;
            $scope.parent_id_children = $scope.selectedCity0.id
            $scope.fetchChildParent();
            fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/city/location/?city_id=' + $scope.selectedCity0.id
            }).then(function (result) {
                $scope.lat = result.data[0].city_lat;
                $scope.long = result.data[0].city_long;
                $scope.loadMap();
            }, function (err) {

            });
        };

        $scope.fetchChildParent = function (value) {
              
          return  fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/city/'  ,
                params : {
                    parent : $scope.parent_id_children ,
                    city_name : value
                }
            }).then(function (result) {
                if(result.data.results)
                {
                    $scope.show_city = true;
                    return result.data.results
                }
                return [];
                // $scope.show_city = true;
                // $scope.loaded_city = result.data.results;
                  
                }, function (err) {
                }
            );

        };

        $scope.fillTelecomInfo = function (id) {
            fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/telecom-center/' + id + '/'
            }).then(function (result) {
                $scope.show_city = true;
                
                var telecom_info = result.data;
                
                $scope.selectedCity = telecom_info.city_info;
                $scope.name = telecom_info.name;
                $scope.prefix_bukht_name = telecom_info.prefix_bukht_name;
                $scope.btn_text = 'Edit';

             
                 fetchResult.fetch_result({
                        method: 'GET',

                        url: ip + 'api/v1/city/' + telecom_info.city_info.parent + '/'
                }).then(function (result) {
                    
                    $scope.selectedCity0 = result.data;
                      
                }, function (err){

                });
                fetchResult.fetch_result({
                        method: 'GET',
                        url: ip + 'api/v1/telecom-center/location/?telecom_id=' + id
                }).then(function (result) {

                        $scope.telecomLocationID = result.data[0].id;

                        $scope.lat = result.data[0].telecom_lat;
                        $scope.long = result.data[0].telecom_long;
                        $scope.loadMap();
                }, function (err){

                });

            }, function (err) {
            });
        };

        $scope.add_telecom = function () {
            
                var post_data = {
                    "name": $scope.name,
                    "prefix_bukht_name": $scope.prefix_bukht_name,
                    "city": $scope.selectedCity.id
                };
                $('#selectCommandErr').addClass('hide');
                var use_method = '';
                var post_url = '';
                if (!fetchResult.checkNullOrEmptyOrUndefined($stateParams.telecom_id)) {
                    use_method = 'POST';
                    post_url = ip + 'api/v1/telecom-center/';
                }
                else {
                    use_method = 'PUT';
                    post_url = ip + 'api/v1/telecom-center/' + $stateParams.telecom_id + '/';
                }
                fetchResult.fetch_result({
                    method: use_method,
                    url: post_url,
                    data: post_data
                }).then(function (result) {
                    if(parseInt(result.status) < 400 ){
                        var notification = alertify.notify('Done', 'success', 5, function () {
                    });
                        $scope.name = '';
                        $scope.prefix_bukht_name = '';
                        $scope.selectedCity0 = '';
                        $scope.selectedCity = '';
                        $scope.lat = 32;
                        $scope.long = 53;
                    }
                    else{
                             var notification = alertify.notify('Bad Request', 'error', 5, function () {
                    });
                    }
                    //create teleccom location object
                    var telecom_location_post_url = null;
                    var params = null;
                    if (use_method == 'POST' || $scope.telecomLocationID == undefined) {
                        use_method = 'POST';
                        telecom_location_post_url = ip + 'api/v1/telecom-center/location/';
                        params = {
                            telecom_center: result.data.id,
                            telecom_lat: $scope.lat,
                            telecom_long: $scope.long
                        };
                    }
                    else {
                        telecom_location_post_url = ip + 'api/v1/telecom-center/location/' + $scope.telecomLocationID + '/';
                        params = {
                            telecom_center: $stateParams.telecom_id,
                            telecom_lat: $scope.lat,
                            telecom_long: $scope.long
                        };
                    }

                    fetchResult.fetch_result({
                        method: use_method,
                        url: telecom_location_post_url,
                        data: params
                    }).then(function (result) {
                    }, function (err) {
                    });

                    //end block create dslam location
                }, function (err) {
                });
                $('#successSelectCity').removeClass('hide');
            
        };

        if (fetchResult.checkNullOrEmptyOrUndefined($stateParams.telecom_id)) {
            $scope.fillTelecomInfo($stateParams.telecom_id);
        }

           $scope.ctrlDown = false;

        $scope.chekKeyUp = function(keyEvent){
            var charCode= keyEvent.which;
             vKey = 86,
             cKey = 67;
        if ($scope.ctrlDown && (charCode == vKey || charCode == cKey)) 
            $scope.ctrlDown = false;

        }

        $scope.checkNumber = function(keyEvent ){
        ctrlKey = 17,
        vKey = 86,
        cKey = 67;
        var charCode= keyEvent.which;

        if (charCode == ctrlKey) $scope.ctrlDown = true;
    

           if($scope.ctrlDown && (charCode == vKey || charCode==cKey))
           {
            console.log('doneeeeee');
           }
            
            else if ((charCode < 48 || charCode > 57) && (charCode < 96 || charCode > 105) &&
        charCode !== 46 &&
        charCode !== 8 &&
        charCode !== 37 &&
        charCode !== 39 && charCode !== 09)
        keyEvent.preventDefault();
        }
    });
