var portman = angular.module('portman', [
    'ui.router',
    'ui.bootstrap',
    'ngtimeago',
    'portman.dslamtable',
    'portman.dslamporttable',
    'portman.dslamreport',
    'portman.portstatusreport',
    'portman.adddslam',
    'portman.resellertable',
    'portman.addreseller',
    'portman.telecomtable',
    'portman.addtelecom',
    'portman.usertable',
    'portman.adduser',
    'portman.customertable',
    'portman.customeractiveport',
    'portman.addcustomer',
    'portman.addresellerport',
    'portman.addcity',
    'portman.dashboard',
    'portman.bukht',
    'portman.addlineprofile',
    'portman.login',
    'portman.userauditlog',
    'portman.dslamportstatustable',
    'portman.bulkcommand' ,
    'portman.userpermission',
    'portman.permissionprofile',
    'portman.vlan',
    'portman.editcustomer',
    'portman.lineprofile',
    'portman.addlineprofile',
    'portman.quickSearch',
    'portman.resellerreport',
    'ADM-dateTimePicker',
    'acute.select',
    'ngSanitize',
    'ui.select',
    'ng-ip-address',
    'ngSocket',
    'slick',
    'isteven-multi-select',
    'ui.select',
    'ngSanitize'



    ]).config(function ($stateProvider, $urlRouterProvider, $interpolateProvider, $httpProvider ) {

     $urlRouterProvider.otherwise('/quick-search');




     $httpProvider.defaults.headers.common['X-CSRFToken'] = csrftoken;
     $interpolateProvider.startSymbol('{$').endSymbol('$}');
     $httpProvider.interceptors.push('authInterceptor');
     delete $httpProvider.defaults.headers.common['X-Requested-With'];


 });



    portman.constant('ip','http://5.202.129.160:2080/');
    portman.constant('socket_ip','5.202.129.160:2083/');



    portman.controller('AppController',
        function ($scope  , $rootScope, $window , $timeout , fetchResult , ip , $location , $interval)
        {
            // $rootScope.isonline = false;
            // console.log(navigator.onLine);
            // $rootScope.isOnline = function(){
            //       if(navigator.onLine) {
            // $rootScope.isonline = true;
            //     }
            // }

          $rootScope.we_have_session = false;
            $rootScope.bc = new BroadcastChannel('need session');

            $scope.userPermissions = function(){

                fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/users/get_permission/' ,
                }).then(function (data, status) {


                 if(data.data.user_type == 'ADMIN'){
                  $rootScope.user_access_admin = true;
                  console.log('admin access' , $rootScope.user_access_admin);
              }

              else{
                $rootScope.user_access = data.data.permissions;
                if($rootScope.user_access.indexOf('view_dslam') != -1)
                {
                    $rootScope.user_access_view_dslam = true;

                }
                if($rootScope.user_access.indexOf('edit_dslam') != -1)
                {
                    $rootScope.user_access_edit_dslam = true;

                }
                if($rootScope.user_access.indexOf('view_reseller') != -1)
                {
                    $rootScope.user_access_view_reseller = true;

                }
                if($rootScope.user_access.indexOf('edit_reseller') != -1)
                {
                    $rootScope.user_access_edit_reseller = true;

                }
                if($rootScope.user_access.indexOf('view_command') != -1)
                {
                    $rootScope.user_access_view_command = true;

                }
                if($rootScope.user_access.indexOf('edit_command') != -1)
                {
                    $rootScope.user_access_edit_command = true;

                }
                if($rootScope.user_access.indexOf('edit_resellerport') != -1)
                {
                    $rootScope.user_access_edit_resellerport = true;

                }
                if($rootScope.user_access.indexOf('view_resellerport') != -1)
                {
                    $rootScope.user_access_view_resellerport = true;

                }
                if($rootScope.user_access.indexOf('view_userauditlog') != -1)
                {
                    $rootScope.user_access_view_userauditlog = true;

                }
                if($rootScope.user_access.indexOf('edit_vlan') != -1)
                {
                    $rootScope.user_access_edit_vlan = true;

                }
                if($rootScope.user_access.indexOf('edit_customerport') != -1)
                {
                    $rootScope.user_access_edit_customerport = true;

                }
                if($rootScope.user_access.indexOf('view_customerport') != -1)
                {
                    $rootScope.user_access_view_customerport = true;

                }
                if($rootScope.user_access.indexOf('view_telecom_center') != -1)
                {
                    $rootScope.user_access_view_telecomcenter = true;

                }
                if($rootScope.user_access.indexOf('edit_telecom_center') != -1)
                {
                    $rootScope.user_access_edit_telecomcenter = true;

                }
                if($rootScope.user_access.indexOf('view_user') != -1)
                {
                    $rootScope.user_access_view_user = true;

                }
                if($rootScope.user_access.indexOf('edit_user') != -1)
                {
                    $rootScope.user_access_edit_user = true;

                }



                $rootScope.user_type = data.data.type ;



            }
            $rootScope.we_have_session = true;
        }, function (err) {

        });

            }
              if (!$window.sessionStorage.token)
            {

                $rootScope.bc.postMessage('need_session');
            }
            if($window.sessionStorage.token)
            {
                 $rootScope.bc.postMessage($window.sessionStorage.token);
                  $scope.userPermissions();

            }
            $scope.is_anybody_listen = false ;


            $rootScope.bc.onmessage = function (ev) {

        if(!$window.sessionStorage.token || $window.sessionStorage.token == 'undefined')
          {
              $window.sessionStorage.token = ev.data ;
              $scope.is_anybody_listen = true ;

              $scope.userPermissions();
          }
          else if(ev.data == 'need_session' && $window.sessionStorage.token){
                    $rootScope.bc.postMessage($window.sessionStorage.token);

          }

      }

      $timeout(function(){
            if(!$scope.is_anybody_listen && (!$window.sessionStorage.token || $window.sessionStorage.token =='undefined' ))
            {
               $location.path("/login");
            }
           },3000);



      $rootScope.user_type =  $window.sessionStorage.user_type;

    $rootScope.scrollTop = function () {
      $window.scrollTo(0, 0);
    }


  });
portman.directive('ngConfirmClick', ['$uibModal', '$timeout', '$animateCss',
    function ($uibModal, $timeout , $animateCss) {
        return {
            priority: -1,
            restrict: 'A',
            scope: {confirmFunction: "&ngConfirmClick"},
            link: function (scope, element, attrs) {
                element.bind('click', function (e) {
                    e.stopImmediatePropagation();
                    e.preventDefault();
                    var message = attrs.ngConfirmMessage;
//                    if (message && !confirm(message)) {
//                    }

var ModalInstanceCtrl = function ($scope, $uibModalInstance) {
    $scope.ok = function () {
        $uibModalInstance.close();
    };

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
};

var modalHtml = '<div class="modal-body">' + message + '</div>';
modalHtml += '<div class="modal-footer"><button class="btn btn-primary" ng-click="ok()">OK</button><button class="btn btn-warning" ng-click="cancel()">Cancel</button></div>';

var modalInstance = $uibModal.open({
    template: modalHtml,
    controller: ModalInstanceCtrl
});

modalInstance.result.then(function () {
    scope.confirmFunction();
//                        $timeout(function() {
//                            attrs.cmClick();
//                        }, 0);
//                        scope.$apply(attrs.cmClick); //raise an error : $digest already in progress
}, function () {
                        //Modal dismissed
                    });
});
            }
        }
    }
    ]);

portman.filter('highlight', function() {
    function escapeRegexp(queryToEscape) {
        return ('' + queryToEscape).replace(/([.?*+^$[\]\\(){}|-])/g, '\\$1');
    }

    return function(matchItem, query) {
        return query && matchItem ? ('' + matchItem).replace(new RegExp(escapeRegexp(query), 'gi'), '<span class="ui-select-highlight">$&</span>') : matchItem;
    };
});

portman.controller('HeaderController',
   function ($rootScope , $scope, $http , ip , fetchResult , $location , $window) {
    $scope.quick_access = {};
    $scope.quick_access.search = 'Search Phone Number' ;


$scope.quick_access.telecom_center = [];
$scope.quick_access.city = [];
$scope.quick_access.dslam_name = [];
$scope.searchPort = function(){
    fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/dslam-port/',
        params: {
            search_username : $scope.quick_access.number,
            search_mac_address : $scope.quick_access.mac,
            search_identifiyer_key : $scope.quick_access.identifier,
            search_dslam_id: $scope.quick_access.dslam_name.id ,
            search_telecom: ($scope.quick_access.telecom_center.id) ? $scope.quick_access.telecom_center.id : $scope.quick_access.telecom_center,
            search_port_number: $scope.quick_access.port,
            search_slot_number: $scope.quick_access.slot,
            search_city: ($scope.quick_access.city.id) ? $scope.quick_access.city.id : $scope.quick_access.city,
                        // search_line_profile: $scope.selected_line_profile,
                    }
                }).then(function (result) {
                    $scope.null_data = false

                    $scope.port_data = result.data.results;
                    if($scope.port_data.length <1){
                        $scope.null_data = true;
                    }
             //   url =  '/dslamport/' + {$ result.dslam_info.id $} + '/status-report/' + {$ result.slot_number $} +'/' + {$ result.port_number $}
              //  $location.path("/login");


          }, function (err) {
          }
          );


            }
            $scope.logout = function(){
             fetchResult.fetch_result({
                method: 'POST',
                url: ip + 'api/v1/users/logout/'
            }).then(function (result) {
               $location.path("/login");

               delete $window.sessionStorage.token;
               delete $window.sessionStorage.user_type;
               delete $window.sessionStorage.ID;

           }, function (err) {
           }
           );
        }
        $scope.getProveList = function(query){
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
                  //  $scope.cities = result.data.results;

              }, function (err) {
              }
              );
        }
        $scope.selectCity = function (query) {
            if($scope.quick_access.city.id || $scope.quick_access.prove.id)
            {
                if($scope.quick_access.city.id)
                {
                 var city_ids = $scope.quick_access.city.id;
             }
             else
             {
                 var  city_ids= $scope.quick_access.prove.id;
             }
         }


         return  fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/telecom-center/',
            params : {
                search_city : city_ids ,
                search_name : query
            }
        }).then(function (result) {
            if(result.data.results){
                return result.data.results;
            }
            return [];

              //  $scope.tele = result.data

          },function () {

          });
    }
    $scope.fetchChildParent = function () {

     return fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/city/?parent=' + $scope.quick_access.prove.id,
        params : {
            city_name : $scope.quick_access.city
        }
    }).then(function (result) {
        if(result.data.results)
        {
            return result.data.results
        }
        return [] ;

    }, function (err) {
    }
    );

};
$scope.quick_access.telecom_center = [];
       // $scope.quick_access.prove = [];
       $scope.searchDslamName = function(query){
           return $http({
            method: "GET",
            url: ip + 'api/v1/dslam/',
            params: {

                page_size: 20,
                search_city : ($scope.quick_access.city.id) ? $scope.quick_access.city.id : $scope.quick_access.city,
                search_dslam: query,
                search_telecom : ($scope.quick_access.telecom_center.id) ? $scope.quick_access.telecom_center.id : $scope.quick_access.telecom_center

            }
        }).then(function mySucces(data) {
            if(data.data.results){

                return data.data.results;
            }
            return [];

        });
    }
    $scope.closeModal = function(){
        $('#header-test').modal('toggle');
    }

    $scope.quickSearch = function(query){
       return fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/quick-search/',
        params : {
            value : query
        }
    }).then(function (result) {
        $scope.quick_access_data = result.data.result ;

    }, function (err) {
    }
    );

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
        charCode !== 13 &&
        charCode !== 8 &&
        charCode !== 37 &&
        charCode !== 39 && charCode !== 09)
        keyEvent.preventDefault();
}

});


// portman.service('storageService', function($window) {

//     this.storage = function() {
//           if (!$window.sessionStorage.token)
//         {
//             $window.localStorage.setItem('getSessionStorage', Date.now());
//         }

//         angular.element($window).on('storage', function (event) {
//             if (event.originalEvent.key === 'getSessionStorage') {
//                 $window.localStorage.setItem('sessionStorage', JSON.stringify($window.sessionStorage));
//                 //$setTimeout(function() {$window.localStorage.removeItem('sessionStorage');}, 2000);

//             } else if (event.originalEvent.key == 'sessionStorage' && !$window.sessionStorage.token)
//             {
//                 var data = JSON.parse(event.originalEvent.newValue),
//                         value;

//                 for (key in data) {
//                     $window.sessionStorage[key] = data[key];
//                 }
//             }
//         });
//         return $window.sessionStorage.token; };

// });

portman.directive('typeaheads' ,  [ '$timeout','$parse',
    function ( $timeout , $parse)  {
       return {
        require: 'ngModel',
        link: function (scope, element, attr, ngModel){

            var aux_modelValue, aux_viewValue,
            modelGetter = $parse(attr.ngModel),
            modelSetter = modelGetter.assign;

            var noViewValue = function(){
              return
              ngModel.$$lastCommittedViewValue === undefined ||
              !ngModel.$$lastCommittedViewValue.trim();
          };

          var forceEvent = function(){
              ngModel.$setViewValue();
              ngModel.$viewValue = ' ';
              ngModel.$setViewValue(' ');
              ngModel.$render();
              scope.$apply();
              element.val(element.val().trim());
          };

          element.on('mousedown', function(e){
              e.stopPropagation();
              forceEvent();
          });

          element.on('blur', function(e){
              e.stopPropagation();
              if(aux_modelValue){
                modelSetter(scope, aux_modelValue);
                scope.$apply();
            }
        });

          scope.$watch(function () {
              return ngModel.$modelValue;
          }, function(newValue, oldValue){
              if(newValue || (!newValue && !oldValue))
                aux_modelValue = newValue;
        });

      }
  }
    //  return {
    //     require: 'ngModel',
    //     link: function (scope, element, attr, ctrl) {
    //         element.bind('click', function () {
    //             var vv = ctrl.$viewValue;
    //             ctrl.$setViewValue(vv ? vv+' ': ' ' );
    //             $timeout(function(){ctrl.$setViewValue(vv ? vv : '');},50)
    //         });
    //     }
    // };

}]);

portman.directive('ngEnter', function() {
    return function(scope, element, attrs) {
        element.bind("keydown keypress", function(event) {
            if(event.which === 13) {
                scope.$apply(function(){
                    scope.$eval(attrs.ngEnter, {'event': event});
                });

                event.preventDefault();
            }
        });
    };
});
portman.factory('authInterceptor', function ($rootScope, $q, $window, $location, $timeout) {
    return {
        request: function (config) {
            config.headers = config.headers || {};

            if ($window.sessionStorage.token) {

                config.headers.Authorization = 'Token ' + $window.sessionStorage.token;

            }
            else if($window.localStorage.sessionStorage) {

                $window.sessionStorage.token = $window.localStorage.sessionStorage.token ;
               // $window.localStorage.removeItem('sessionStorage');
               config.headers.Authorization = 'Token ' + $window.localStorage.sessionStorage.token;

           }
           return config;
       },
       responseError: function (response) {
        if (response.status === 401 ) {

            $location.path("/login");

            }

          return response || $q.when(response);
      }
  };
});
