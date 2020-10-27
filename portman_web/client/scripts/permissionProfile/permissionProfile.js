angular.module('portman.permissionprofile', ['myModule'])
.config(function ($stateProvider, $urlRouterProvider) {
  $stateProvider
  .state('permission', {
    url: '/permission',
    views: {
      'content': {
        templateUrl: 'templates/permissionprofile/permission_profile.html',
        
        controller: 'PermissionProfileController'
      }
    },
  });
})
.controller('PermissionProfileController', function ($scope, fetchResult, $stateParams, ip ) {
 $scope.selected = {} ; 
 $scope.add_new_permission = {} ;
 $scope.add_new_permission.permission = [] ;
 $scope.GetPermissionList = function(query){
  return  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/permission/' ,
    params :{
      page_size : 50 ,
      search_title : query
    }
  }).then(function (result) {
    if(result.data.results)
    {
      console.log(result.data.results);
      $scope.select2_permission_list = result.data.results ;
                     //  return result.data.results
                   }
                   // return [];
                   
                 }, function (err) {

                 });
}

$scope.GetPermissionList();
$scope.permission_pagination = {};
$scope.permission_pagination.currentPage = 1 ;
$scope.permission_pagination.itemsPerPage = 10 ;

$scope.GetPermissionProfileList = function(){
 fetchResult.fetch_result({
  method: 'GET',
  url: ip + 'api/v1/profile/'  ,
  params : {
    page : $scope.permission_pagination.currentPage
  }
  
}).then(function (result) {
 $scope.permission_pagination.TotalItems = result.data.count ;
 $scope.permission_profile_list = result.data.results;
 
}, function (err) {

});
}
$scope.GetPermissionProfileList();

$scope.new_profile = [];
$scope.AddNewPermission = function(){
  angular.forEach($scope.enable_permissions , function(value,key){
    if($scope.add_new_permission.title == value.title){
      $scope.enable_permissions.splice(key,1);
    }
  });
  $scope.new_profile.push($scope.add_new_permission);



}
$scope.DeleteNewProfile = function(data , index){
  $scope.new_profile.splice(index,1);
  $scope.enable_permissions.push(data);

}
$scope.DeleteNewProfileInUpdate = function(data , index){
  $scope.update_permission_list_to_add.splice(index,1);

}
$scope.new_permission = {};
$scope.id_to_post = [];
$scope.CreateNewPermission = function(){
             //   console.log($scope.add_new_permission.permission);
             angular.forEach($scope.add_new_permission.permission , function(value,key){
              $scope.id_to_post.push(value.id);
            });
             
             $('#create-permission').modal('toggle');
             fetchResult.fetch_result({
              method: 'POST',
              url: ip + 'api/v1/permission-profile/' ,
              data : {
                permission_profile_name : $scope.new_permission.name,
                permissions :  $scope.id_to_post
              }
              
            }).then(function (result) {
              if(result.status >= 400){
                
                var notification = alertify.notify(result.statusText, 'error', 5, function () {
                });
              }
              else{
                $scope.new_profile = [];
                $scope.new_permission.name = '';
                var notification = alertify.notify('Success', 'success', 5, function () {
                });
                $scope.GetPermissionProfileList();
              }

              
              
              
            }, function (err) {

            });

          }

          $scope.DeletePermissionProfile = function(id){
            fetchResult.fetch_result({
              method: 'POST',
              url: ip + 'api/v1/permission-profile/delete_permission_profile/',
              data : {
               permission_profile_id : id
             }
             
           }).then(function (result) {
             if(parseInt (result.status) < 400)
             {
              var notification = alertify.notify('Deleted', 'success', 5, function () {
              });}
              else{
               var notification = alertify.notify(result.statusText, 'error', 5, function () {
               });
             }


             
             $scope.GetPermissionProfileList();
             
             
           }, function (err) {

           });
         }
         $scope.UpdatePermission = function(id){
          $scope.last_editable_id = id;
          
          $scope.update_permission_list_to_add = [];
          fetchResult.fetch_result({
            method: 'GET',
            url: ip + "api/v1/profile/" + id + '/',
            data : {
             permission_profile_id : id
           }
           
         }).then(function (result) {
          $scope.name = result.data.name;
          $scope.update_permission_list_to_add.permission = result.data.permissions;
          
          $scope.update_permission_list_input = $scope.permission_list ;
          
        }, function (err) {

        });
         
       }
       
      //  $scope.AddPermission = function(){
      //   angular.forEach($scope.update_permission_list_input , function(value,key){
      //     if(value.id == $scope.add_permission_name.id)
      //     {
      //      $scope.update_permission_list_input.splice(key,1);
      //    }
         
      //  });
      //   $scope.update_permission_list_to_add.push({id: $scope.add_permission_name.id , name :$scope.add_permission_name.title});
      //   $scope.add_permission_name = '';
      // }

      $scope.update_permission_list_to_add = {};
      $scope.UpdatePermissionInfo = function(){
       console.log($scope.update_permission_list_to_add.permission);
       $scope.send_permission = [];
       angular.forEach($scope.update_permission_list_to_add.permission , function(value,key){
        $scope.send_permission.push(value.id);
      });
       
       fetchResult.fetch_result({
        method: 'PUT',
        url: ip + 'api/v1/permission-profile/' +  $scope.last_editable_id + '/',
        data : {
         permission_profile_id : $scope.last_editable_id,
         name : $scope.name,
         permissions : $scope.send_permission
       }
       
       
     }).then(function (result) {
        if(parseInt (result.status) < 400)
             {
              var notification = alertify.notify('Done', 'success', 5, function () {
              });}
              else{
               var notification = alertify.notify(result.statusText, 'error', 5, function () {
               });
             }

     }, function (err) {

     });

   }
  //  $scope.DeleteFromPermissionList = function (index) {
  //   $scope.permission_list.splice(index,1);
  // };


});