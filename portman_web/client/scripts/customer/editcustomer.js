angular.module('portman.editcustomer', ['myModule'])
    .config(function ($stateProvider) {
        $stateProvider
            .state('edit-subscriber', {
                url: '/edit-subscriber/:customer_id?',
                views: {
                    'content': {
                        templateUrl: 'templates/customer/edit-customer.html',
                         
                        controller: 'EditCustomerController'
                    }
                }
            });
    })
    .controller('EditCustomerController', function ($scope, fetchResult, $stateParams, $compile, ip) {
        $scope.customer_id = $stateParams.customer_id ;

      
         fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/customer-port/' + $scope.customer_id + '/',
              
            }).then(function (result) {
                
                $scope.customer_detaile = result.data ;
                 
                }, function (err) {
                });

            $scope.UpdateCustomer = function(){
                
                fetchResult.fetch_result({
                method: 'PUT',
                url: ip + 'api/v1/customer-port/' + $scope.customer_id + '/',
                data : $scope.customer_detaile
              
            }).then(function (result) {
                
                
                }, function (err) {
                });
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

      