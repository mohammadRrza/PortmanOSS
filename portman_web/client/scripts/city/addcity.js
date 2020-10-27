angular.module('portman.addcity', ['myModule'])
    .config(function ($stateProvider) {
        $stateProvider
            .state('add-city', {
                url: '/add-city',
                views: {
                    'content': {
                        templateUrl: 'templates/city/add-city.html',

                        controller: 'CityController'
                    }
                }
            });
    })
    .controller('CityController', function ($scope, fetchResult, $state, ip) {

        fetchResult.loadFile('global/plugins/jstree/dist/themes/default/style.min.css');

        $scope.selected_city = '';
        function reload_data() {
            fetchResult.loadFile('global/plugins/jstree/dist/jstree.js', function () {

                fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/city/tree_view/'
                }).then(function (result) {
                    console.log(result.data);
                    $scope.data_tree = [] ;
                    angular.forEach (result.data , function(value , key){
                        //console.log(value) ;
                        $scope.data_tree.push({
                            'text' : value.text + ' ' +  value.abbr ,
                             'id' : value.id ,
                             'parent' : value.parent });
                        // $scope.data_tree[key].text = value.text + ' ' +  value.abbr ;
                        // $scope.data_tree[key].id = value.id;
                        // $scope.data_tree[key].parent = value.parent;
                    });

                    // if($scope.data_tree.length == result.data.length)
                    // {
                    $('#city_tree').jstree({
                        'core': {
                            'data': $scope.data_tree , //result.data,
                            "themes": {"stripes": true},
                            "animation": true,
                            "check_callback": true
                        }
                    });
                //}
                });

                $('#city_tree').on("changed.jstree", function (e, data) {

                    $scope.selected_city = data.selected[0];


                });

            });

        }

        $scope.register_city = function () {
            if ($scope.selected_city != '' ) {
                if($scope.city != '' && $scope.city != undefined &&
                $scope.english_name != '' && $scope.english_name != undefined &&
                $scope.abbr != '' && $scope.abbr != undefined )
                {

                fetchResult.fetch_result({
                    method: 'post',
                    data: {
                        "name": $scope.city,
                        'english_name' : $scope.english_name ,
                        'abbr' : $scope.abbr ,
                        "parent": $scope.selected_city
                    },
                    url: ip + 'api/v1/city/'
                }).then(function (result) {
                   if(result.status <400 ){
                      var notification = alertify.notify('Done', 'success', 5, function () {
                });
                      $state.reload();
                }
                }, function (err) {
                });
            }
             else {
                var notification = alertify.notify('Incomplete Fields', 'error', 5, function () {
                });
            }

            }
            else {
                var notification = alertify.notify('No Province Selected', 'error', 5, function () {
                });
            }
        };

        $scope.selectCity = function (selectedVal) {
            $scope.parent_city = selectedVal;
        };
        $scope.delete_city = function () {
            fetchResult.fetch_result({
                method: 'delete',
                url: ip + 'api/v1/city/' + $scope.selected_city + "/"
            }).then(function (result) {
                if(result.status <400 ){
                      var notification = alertify.notify('Done', 'success', 5, function () {
                });
                      $state.reload();
                }


                }, function (err) {
                }
            );
        };

        $scope.register_province = function () {

                if($scope.city != '' && $scope.city != undefined &&
                $scope.english_name != '' && $scope.english_name != undefined &&
                $scope.abbr != '' && $scope.abbr != undefined )
                {
            fetchResult.fetch_result({
                method: 'POST',
                url: ip + 'api/v1/city/',
                data: {
                    'name': $scope.city,
                    'english_name' : $scope.english_name ,
                     'abbr' : $scope.abbr ,
                }
            }).then(function (result) {
                 if(result.status <400 ){
                      var notification = alertify.notify('Done', 'success', 5, function () {
                });
                      $state.reload();
                }
                else{
                      var notification = alertify.notify(result.statusText, 'error', 5, function () {
                });
                }


                }, function (err) {
                }
            );
        }
         else {
                var notification = alertify.notify('Incomplete Fields', 'error', 5, function () {
                });
            }
        };
        reload_data();
        $scope.test = function () {
            fetchResult.fetch_result({
                method: 'POST',
                url: ip + 'api/v1/dslamport/register-port/' ,
                data : {

"port":{
"telecom_center_name": "motahari",
"dslam_name": "TEH-Motahari2",
"card_number": "19",
"port_number": "29"
},
"reseller": {
"name": "fanava"
},
"subscriber":{
"username": "22608107"
}

                }
            }).then(function (result) {

                    console.log(result);

                }, function (err) {
                }
            );
        };
        $scope.test();
    });
