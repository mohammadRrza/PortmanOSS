angular.module('portman.addreseller', ['myModule'])
    .config(function ($stateProvider) {
        $stateProvider
            .state('add-reseller', {
                url: '/add-reseller/:reseller_id?',
                views: {
                    'content': {
                        templateUrl: 'templates/reseller/add-reseller.html',
                         
                        controller: 'AddResellerController'
                    }
                }
            });
    })
    .controller('AddResellerController', function ($scope, fetchResult, $stateParams, $compile, ip) {
        $scope.btn_text = "Submit";
        $scope.city = '';
        fetchResult.loadFile('global/plugins/select2/css/select2.min.css');
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
                 
                   
                }, function (err) {
                }
            );
}
        $scope.getProveList();
     
        fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/vlan/'
        }).then(function (result) {
            }, function (err) {
            }
        );

        $scope.selectCity = function (city_id) {
            $scope.city = city_id;
            $scope.getCityList(city_id);
        };

        $scope.getCityList = function (parent_id) {
            fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/city/?parent=' + parent_id
            }).then(function (result) {
                   

                }, function (err) {
                }
            );

        };

        $scope.fillResellerInfo = function (id) {
            fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/reseller/' + id+'/'
            }).then(function (result) {
                
                var reseller_info = result.data;
                $scope.name = reseller_info.name;
                $scope.vpi = reseller_info.vpi;
                $scope.vci = reseller_info.vci;
                $scope.tel = reseller_info.tel;
                $scope.fax = reseller_info.fax;
                $scope.address = reseller_info.address;
                $scope.selectedCity = reseller_info.city_info.text ;
                $scope.btn_text = 'Edit';
                if(reseller_info.city_info.parent){
                   fetchResult.fetch_result({
                        method: 'GET',
                        url: ip + 'api/v1/city/'+ reseller_info.city_info.parent + '/'
                })
                .then(function (result) {
                   
                    $scope.show_city = true;
                    $scope.selectedCity0 = result.data;
                      
                }, function (err){

                });
            }
            }, function (err) {
            });
        };
        $scope.show_city = false;
         $scope.fetchChildParent = function (parent_id , query) {
           
           return fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/city/'  , 
                params : {
                    parent : parent_id ,
                    city_name : query
                }
            }).then(function (result) {
                $scope.show_city = true;
                if(result.data.results){
                    return result.data.results
                }
                return [] ;
                
                 
                }, function (err) {
                }
            );

        };

        $scope.add_reseller = function () {
            if ($scope.selectedCity0 != '') {
                var post_data = {
                    "name": $scope.name,
                    "vpi": $scope.vpi,
                    "vci": $scope.vci,
                    "tel": $scope.tel,
                    "fax": $scope.fax,
                    "address": $scope.address,
                    "city": $scope.selectedCity.id
                };

            
                var use_method = '';
                var post_url = '';
                if (!fetchResult.checkNullOrEmptyOrUndefined($stateParams.reseller_id)) {
                    use_method = 'POST';
                    post_url = ip + 'api/v1/reseller/';
                }
                else {
                    use_method = 'PUT';
                    post_url = ip + 'api/v1/reseller/' + $stateParams.reseller_id + '/';
                }
               
                fetchResult.fetch_result({
                    method: use_method,
                    url: post_url,
                    data: post_data
                }).then(function (result) {
                   
                    if(parseInt( result.status) < 400){
                        $scope.selectedCity0 = '';
                        $scope.selectedCity1 = '';
                        $scope.address = '';
                        $scope.fax = '';
                        $scope.tel = '';
                        $scope.vpi = '';
                        $scope.vci = '';
                        $scope.name = '';
                     var notification = alertify.notify('Reseller Added', 'success', 5, function () {
                    });
                }
                else{
                     var notification = alertify.notify(result.statusText, 'error', 5, function () {
         });
                }
                   
                }, function (err) {
                    
                });
                $('#successSelectCity').removeClass('hide');
            }
            else {
                $('#selectCommandErr').removeClass('hide');
                $('#successSelectCity').addClass('hide');
            }
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
            
            else if ((charCode < 48 || charCode > 57) &&   (charCode < 96 || charCode > 105) &&
        charCode !== 46 &&
        charCode !== 8 &&
        charCode !== 37 &&
        charCode !== 39 && charCode !== 09)
        keyEvent.preventDefault();
        }

        if (fetchResult.checkNullOrEmptyOrUndefined($stateParams.reseller_id)) {
            $scope.fillResellerInfo($stateParams.reseller_id);
        }



    });
