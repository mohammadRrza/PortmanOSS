angular.module('portman.adduser', ['myModule'])
    .config(function ($stateProvider) {
        $stateProvider
            .state('add-user', {
                url: '/users/add/:user_id?',
                views: {
                    'content': {
                        templateUrl: 'templates/user/add-user.html',
                         
                        controller: 'AddUserController'
                    }
                }
            });
    })
    .controller('AddUserController', function ($scope, fetchResult, $stateParams, ip) {

        $scope.btn_text = "Submit";
        $scope.reseller = '';
        $scope.type = '';
        $scope.edit_user = true;

        fetchResult.loadFile('global/plugins/select2/css/select2.min.css');
        fetchResult.loadFile('global/plugins/select2/js/select2.full.min.js', function () {
            fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/reseller/'
            }).then(function (result) {
                    $scope.resellers = result.data.results;
                    $(".select-reseller-array").select2({
                        data: $scope.resellers
                    });
                }, function (err) {
                }
            );

        });

        $scope.selectType = function (type_id) {
            $scope.type = type_id;
        };

        $scope.selectReseller = function (reseller_id) {
            $scope.reseller = reseller_id;
        };

        $scope.filluserInfo = function (id) {
              $('.passwd').hide();
              $('.username').hide();
            fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/users/' + id + '/'
            }).then(function (result) {
                $scope.edit_user = false;
                var user_info = result.data;
                console.log(user_info);

                $scope.username = user_info.username;
                $scope.firstname = user_info.first_name;
                $scope.lastname = user_info.last_name;
                $scope.tel = user_info.tel;
                $scope.email = user_info.email;
                $scope.active = user_info.is_active;
                $scope.btn_text = 'Edit';
                $scope.selectedType = user_info.type ;
                $scope.selectedReseller =  user_info.reseller_info ;
            }, function (err) {
            });
        };

        $scope.add_user = function () {
            if($scope.selectedType == "RESELLER" && ($scope.selectedReseller == '' || $scope.selectedReseller == null
                || $scope.selectedReseller == undefined))
            {
                    var notification = alertify.notify('Please Select Reseller', 'error', 5, function () {
                                    });
            }
            else  {

                var post_data = {
                    "username": $scope.username,
                    "first_name": $scope.firstname,
                    "last_name": $scope.lastname,
                    "email": $scope.email,
                    "tel": $scope.tel,
                    "reseller": $scope.selectedType == "RESELLER" ? $scope.selectedReseller.id : '',
                    "password": $scope.password,
                    "confirm_password": $scope.password2,
                    "is_active": $scope.active,
                    "type": $scope.type
                };

                $('#selectCommandErr').addClass('hide');
                var use_method = '';
                var post_url = '';
                if ($stateParams.user_id == undefined || $stateParams.user_id == '') {
                    use_method = 'POST';
                    post_url = ip + 'api/v1/users/';
                }
                else {
                    use_method = 'PUT';
                    post_url = ip + 'api/v1/users/' + $stateParams.user_id + '/';
                }
                fetchResult.fetch_result({
                    method: use_method,
                    url: post_url,
                    data: post_data
                }).then(function (result) {
                    if(parseInt( result.status) < 400 )
                    {
                        $scope.firstname = '';
                        $scope.lastname = '';
                        $scope.username = '';
                        $scope.email = '';
                        $scope.tel = '';
                        $scope.password = '';
                        $scope.password2 = '';
                        $scope.selectedType = '';
                        $scope.selectedReseller = '';
                        $scope.active = false;
                       var notification = alertify.notify('Done', 'success', 5, function () {
                                    });
                    }
                    else {
                            var notification = alertify.notify(result.statusText, 'error', 5, function () {
                                    });
                    }
                }, function (err) {
                     var notification = alertify.notify('error', 'error', 5, function () {
                                    });
                });
                $('#successSelectreseller').removeClass('hide');
            }
           
        };

        if (fetchResult.checkNullOrEmptyOrUndefined($stateParams.user_id)) {
            $scope.filluserInfo($stateParams.user_id);
        }
 $scope.getReseller = function(query){
            
            

            return fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/reseller/',
                   params: {
                    name : query
                }

            }).then(function (result) {
                
                 if(result.data.results){
                    return result.data.results
                 }
                 return [];
               
                }, function (err) {
                }
            );

        }
        $scope.getReseller();
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
        
        charCode !== 8 &&
        charCode !== 37 &&
        charCode !== 39 && charCode !== 09)
        keyEvent.preventDefault();
        }

    });
