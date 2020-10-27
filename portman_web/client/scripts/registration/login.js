angular.module('portman.login', ['myModule'])
.config(function ($stateProvider) {
  $stateProvider
  .state('login', {
    url: '/login',
    views: {
      'body': {
        templateUrl: 'templates/registration/login.html',

        controller: 'LoginController'
      }
    }
  });
})
.controller('LoginController', function ($rootScope,$scope, fetchResult, $window, $location, ip) {
  $scope.username = '';
  $scope.password = '';
  $scope.callLogin = function(event) {
    if(event.keyCode == 13) {
      // event.preventDefault();
      window.stop(); // Works in all browsers but IE
      document.execCommand("Stop"); // Works in IE
      $scope.login();
    }
  };
  $scope.login = function () {
    fetchResult.fetch_result({
      method: 'POST',
      url: ip + 'api/v1/users/login/',
      data: {'username': $scope.username, 'password': $scope.password}
    }).then(function (data, status) {
      if (parseInt(data.status) > 400) {
        var notification = alertify.notify(data.statusText, 'error', 5, function () {
        });

      }
      else{
        $window.sessionStorage.token = data.data.token;
        $window.sessionStorage.ID = data.data.id;
        $rootScope.we_have_session = true;
        $scope.userPermissions();
        if(data.data.type == 'ADMIN')
        {
          $rootScope.user_access_admin = true;
        }
        $rootScope.user_type = data.data.type ;


        if($window.sessionStorage.user_type == 'ADMIN')
        {
          $location.path("/dashboard");
        }

        else {
          $location.path("/dslamport");
        }

      }
    }, function (err) {
    });
  };

  $scope.userPermissions = function(){
    fetchResult.fetch_result({
      method: 'GET',
      url: ip + 'api/v1/users/get_permission/' ,
    }).then(function (data, status) {


      if(data.data.user_type == 'ADMIN'){
        $rootScope.user_access_admin = true;
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
        if($rootScope.user_access.indexOf('view_telecomcenter') != -1)
        {
          $rootScope.user_access_view_telecomcenter = true;

        }
        if($rootScope.user_access.indexOf('edit_telecomcenter') != -1)
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
  };

});
