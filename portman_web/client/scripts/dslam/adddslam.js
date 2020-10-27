angular.module('portman.adddslam', ['myModule'])
.config(function ($stateProvider) {
$stateProvider
.state('add-dslam', {
    url: '/add-dslam/:dslam_id?',
    views: {
        'content': {
            templateUrl: 'templates/dslam/add-dslam.html',
              
            controller: 'AddDslamController'
        }
    }
});
})
.controller('AddDslamController', function ($scope, fetchResult, $stateParams, ip) {
$('#secess_alert').hide('fast');
$scope.btn_text = "Submit";
$scope.command = '';
$scope.title = 'Add New DSLAM';
$scope.action = 'added';
$scope.snmp_community = '';
$scope.dslam_id = $stateParams.dslam_id ;

$scope.selected_City = '';

$scope.marker = '';

    //load province
    $scope.provinceList = function(query){
        return fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/city/?parent=all',
            params:{
                city_name : query
            }
        }).then(function (result) {
         if(result.data.results)
         {
            return result.data.results;
        }
        return[];
        
        
    }, function (err) {

    });
    }
    $scope.provinceList();

    $scope.loadMap = function () {
        if($scope.lat !== undefined && $scope.lat != '' &&  $scope.long!== undefined &&  $scope.long != ''){
           var mapOptions = {
            zoom: 10,
            center: new google.maps.LatLng($scope.lat, $scope.long),
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            scrollwheel: false,
            zoomControl: true,
            zoomControlOptions: {
                style: google.maps.ZoomControlStyle.LARGE,
                position: google.maps.ControlPosition.RIGHT_CENTER
            }
        };
    }
    else{
      var mapOptions = {
        zoom: 10,
        center: new google.maps.LatLng(32, 50),
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        scrollwheel: false,
        zoomControl: true,
        zoomControlOptions: {
            style: google.maps.ZoomControlStyle.LARGE,
            position: google.maps.ControlPosition.RIGHT_CENTER
        }
    };
}



$scope.map = new google.maps.Map(document.getElementById('map'), mapOptions);

google.maps.event.addListener($scope.map, 'click', function (event) {
    $scope.lat = event.latLng.lat();
    $scope.long = event.latLng.lng();
    $('#dslam_long').val($scope.long);
    $('#dslam_lat').val($scope.lat);
    placeMarker(event.latLng);
});

function placeMarker(location) {
    if ($scope.marker != '')
        $scope.marker.setMap(null);
    var marker = new google.maps.Marker({
        position: location,
        map: $scope.map
    });
    $scope.marker = marker;
};
};
$scope.loadMap();
$scope.loadCityLocation = function () {
console.log($scope.selectedCity0);
        //load province
        fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/city/location/?city_id=' + $scope.selectedCity0.id
        }).then(function (result) {
            console.log(result);
            if(result.data.length > 0)
            {
                $scope.lat = result.data[0].city_lat;
            $scope.long = result.data[0].city_long;
            $scope.loadMap();
            }
            
        }, function (err) {

        });
    };

    $scope.onSelect = function(dslam_typeId) {
    if(dslam_typeId == 3 || dslam_typeId == 4 || dslam_typeId == 5)
        {
            $scope.isRequired = false;
        }
        else
        {
            $scope.isRequired = true;
        }
    }

    fetchResult.loadFile('global/plugins/select2/css/select2.min.css');
    fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/dslam/dslam-type/'
    }).then(function (result) {
        $scope.dslam_type = result.data;
        
    }, function (err) {
    }
    );
    setTimeout(function () {
        $(".select-dslam-type-data-array").val($scope.dslam_type_selected).trigger("change")
    }, 500);

    $scope.getTelecomCenter = function(query){
        console.log(query);
        return fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/telecom-center/',

            params : {
                search_name : $scope.selectedTelecomCenter,
                search_city_id : $scope.selectedCity0.id ,
                
            }
        }).then(function (result) {
            if(result.data.results)
            {
                return result.data.results ;
            }
            return []
            
        }, function (err) {
        }
        );
    }

    


    $scope.fillDSLAMInfo = function () {
        fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/dslam/' + $scope.dslam_id + '/' 
        }).then(function (result) {
            var dslam_info = result.data;
            $scope.name = dslam_info.name;
            $scope.telecom_center_info_selected = dslam_info.telecom_center_info;
            $scope.selectedTelecomCenter = dslam_info.telecom_center_info;
            $scope.dslam_type_selected = dslam_info.dslam_type_info;
            $scope.selectedDslamType = dslam_info.dslam_type_info;
            $scope.ip = dslam_info.ip;
            $scope.active = dslam_info.active;
            $scope.conn_type = dslam_info.conn_type;
            $scope.get_snmp_community = dslam_info.get_snmp_community;
            $scope.set_snmp_community = dslam_info.set_snmp_community;
            $scope.snmp_port = dslam_info.snmp_port;
            $scope.snmp_timeout = dslam_info.snmp_timeout;
            $scope.telnet_username = dslam_info.telnet_username;
            $scope.telnet_password = dslam_info.telnet_password;
 	    $scope.selectedCity0= dslam_info.telecom_center_info.city_info;
 	        $scope.selected_city= dslam_info.telecom_center_info.city_info.text;
            $scope.fqdn = dslam_info.fqdn;
            $scope.btn_text = 'Edit';
            $scope.title = 'Edit DSLAM';
            $scope.action = 'edited';
            
            $scope.getLocation();
            $scope.loadMap();

        }, function (err) {
        });
    };

    $scope.getLocation = function(){
       fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/dslam/location/?dslam_id=' + $scope.dslam_id
    }).then(function (result) {
        if(result.data[0] != undefined){
            $scope.lat = result.data[0].dslam_lat;
            $scope.long = result.data[0].dslam_long;
            $scope.dslamLocationID = result.data[0].id;
        }

        
    }, function (err) {

    });
}

$scope.add_dslam = function () {
    if ($scope.selectedDslamType != undefined && $scope.selectedTelecomCenter != undefined) {

        post_data = {
            "name": $scope.name,
            "telecom_center": $scope.selectedTelecomCenter.id,
            "dslam_type": $scope.selectedDslamType.id,
            "ip": $scope.ip,
            "active": $scope.active,
            "status": "new",
            "conn_type": $scope.conn_type,
            "get_snmp_community": $scope.get_snmp_community,
            "set_snmp_community": $scope.set_snmp_community,
            "telnet_username": $scope.telnet_username,
            "telnet_password": $scope.telnet_password,
            "snmp_port": $scope.snmp_port,
            "snmp_timeout": $scope.snmp_timeout,
            'fqdn' : $scope.fqdn
        };

       
        var use_method = '';
        var post_url = '';
        
        if (!fetchResult.checkNullOrEmptyOrUndefined($stateParams.dslam_id)) {
            use_method = 'POST';
            post_url = ip + 'api/v1/dslam/';
        }
        else {
           
            use_method = 'PUT';
            post_url = ip + 'api/v1/dslam/' + $stateParams.dslam_id + '/';
        }
        fetchResult.fetch_result({
            method: use_method,
            url: post_url,
            data: post_data
        }).then(function (result) {
            console.log(result);
            console.log(result.data[0]);
            if(parseInt (result.status) <400 ){
            var notification = alertify.notify('Done', 'success', 5, function () {
     });
        }
     else {
        var notification = alertify.notify(result.statusText, 'error', 5, function () {
     });
        angular.forEach(result.data , function(key,value){
             var notification = alertify.notify(key[0], 'error', 5, function () {
        });
        })

        
     
     }
           
       var dslam_location_post_url = null;
            
            if (use_method == 'POST' ||  $scope.dslamLocationID == undefined) {
                use_method = "POST" ;
                if(($scope.lat !== null || $scope.lat !== undefined || $scope.lat !== '') &&
                   ($scope.long !== null || $scope.long !== undefined || $scope.long !== ''))
                {
                    dslam_location_post_url = ip + 'api/v1/dslam/location/';
                    params = {
                        dslam: result.data.id,
                        dslam_lat: $scope.lat,
                        dslam_long: $scope.long
                    };}

                }
                else {
                   if(($scope.lat !== null || $scope.lat !== undefined || $scope.lat !== '') &&
                       ($scope.long !== null || $scope.long !== undefined || $scope.long !== ''))
                   {
                    dslam_location_post_url = ip + 'api/v1/dslam/location/' + $scope.dslamLocationID + '/';
                    params = {
                        dslam: $stateParams.dslam_id,
                        dslam_lat: $scope.lat,
                        dslam_long: $scope.long
                    };
                }

            }

            fetchResult.fetch_result({
                method: use_method,
                url: dslam_location_post_url,
                data: params
            }).then(function (result) {
                if($scope.dslam_id  !== null && $scope.dslam_id !== undefined && $scope.dslam_id !== ''){
                    $scope.fillDSLAMInfo();
                }

                if(($scope.lat !== null && $scope.lat !== undefined && $scope.lat !== '') &&
                   ($scope.long !== null && $scope.long !== undefined && $scope.long !== ''))
                {
                    $scope.loadCityLocation();
                }
            }, function (err) {
            });

            
            $scope.reset_form();
            $('#secess_alert').show('fast');
            setTimeout(function () {
                $('#secess_alert').hide('fast');
            }
            , 3000);
        }, function (err) {
        });
        
    }
    else {
        $('#selectCommandErr').removeClass('hide');
        $('#successCommandE').addClass('hide');
    }
};

$scope.reset_form = function () {
    dslam_info = '';
    $scope.name = '';
    $scope.ip = '';
    $scope.active = false;
    $scope.conn_type = '';
    $scope.get_snmp_community = '';
    $scope.set_snmp_community = '';
    $scope.snmp_port = '';
    $scope.snmp_timeout = '';
    $scope.tellnet_username = '';
    $scope.telnet_password = '';
};

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

if (fetchResult.checkNullOrEmptyOrUndefined($stateParams.dslam_id)) {
    $scope.fillDSLAMInfo($stateParams.dslam_id);
}

$scope.LoadCity = function () {
          
       return fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/city/?parent=' + $scope.selected_city.id ,
            params : {
            city_name : $scope.selectedCity0
          }
        }).then(function (result) {
            console.log(result);
            if(result.data.results)
            {
                return result.data.results ;
            }
            return [];
            
              
            }, function (err) {
            }
        );

    };

});
