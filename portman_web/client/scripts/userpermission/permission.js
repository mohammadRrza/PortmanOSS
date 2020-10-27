angular.module('portman.userpermission', ['myModule'])
.config(function ($stateProvider, $urlRouterProvider) {
    $stateProvider
    .state('userpermission', {
        url: '/userpermission',
        views: {
            'content': {
                templateUrl: 'templates/userpermission/user_permission.html',

                controller: 'UserPermissionController',

            }
        },
    });
})
.controller('UserPermissionController', function ($scope, fetchResult, $stateParams,$filter, ip ,$uibModal ) {

   $scope.AddUserPermissionModal = function (size, module, searchParams) {
    angular.forEach($scope.dslam_list, function (values, key) {
        values.ticked = false;
    });

    angular.forEach($scope.command_list, function (values, key) {
        values.ticked = false;
    });


    modalInstance = $uibModal.open({
        templateUrl: "myModalContent.html",
                  //  templateUrl: 'templates/userpermission/user-permission.add.html',
                  size: size,
                  animation: !1,
                  controller: ["$scope", "$uibModalInstance", "module", "flag", "title", "message", "okValue", "cancelValue",
                  function ($scope, $uibModalInstance, module, flag, title, message, okValue, cancelValue) {
                    $scope.flag = flag;
                    $scope.module = module;
                    $scope.title = title;
                    $scope.message = message;
                    $scope.new_data = {
                    };
                    $scope.searchParams = searchParams;
                    $scope.okValue = okValue;
                    $scope.cancelValue = cancelValue;
                    $scope.ok = function (new_data) {
//                               
$uibModalInstance.close(new_data);
};
$scope.cancel = function () {
    $uibModalInstance.dismiss("cancel");
};
}
],
scope: $scope,
resolve: {
    flag: function () {
        return "primary";
    },
    module: function () {
        return module;
    },
    title: function () {
        return "Add New User Permission";
    },
    message: function () {
        return '';
    },
    okValue: function () {
        return "";
    },
    cancelValue: function () {
        return "";
    },
}
}), modalInstance.result.then(function (new_data) {
}, function () {
});
};

$scope.AddUserPermission = function (new_data) {
    $scope.cancel = false;
    modalInstance.close();
    if (new_data.username !== null && new_data.username != '' && new_data.username !== undefined)
    {


        if(new_data.username.id){
            new_data.user = new_data.username.id;
        }
        else{
            $scope.cancel = true;
            var notification = alertify.notify('Invalid User', 'error', 5, function () {


            });
        }
    }
    new_data.dslams = [];
    if (new_data.dslam_name !== null && new_data.dslam_name != '' && new_data.dslam_name !== undefined)
    {
        angular.forEach(new_data.dslam_name, function (value, key) {
            new_data.dslams.push(value.id);
        });
    }
    new_data.commands = [];
    if (new_data.command_name !== null && new_data.command_name != '' && new_data.command_name !== undefined)
    {
        angular.forEach(new_data.command_name, function (value, key) {
            new_data.commands.push(value.id);
        });
    }
    if (new_data.permission_profile_name !== null && new_data.permission_profile_name != '' && new_data.permission_profile_name !== undefined)
    {
        if( new_data.permission_profile_name.id){
            new_data.permission_profile = new_data.permission_profile_name.id;
        }
        else{
            $scope.cancel = true;
            var notification = alertify.notify('Wrong Permission Profile', 'error', 5, function () {


            });
        }

    }
    if(new_data.action == undefined){
        new_data.action = 'allow';
    }
    if(new_data.is_active == undefined){
        new_data.is_active = 'true';
    }
    new_data.device_name = [];
    new_data.network_name = [];
    var data =  {
        "user": new_data.user,
        "action": new_data.action,
        "is_active": new_data.is_active,
        "objects":[
        {"type":'dslam', id: new_data.dslams},
        {"type":'command', id: new_data.commands}
        ]}


        if(!$scope.cancel){
          fetchResult.fetch_result({
            method: 'POST',
            url: ip + 'api/v1/users/permission-profile/',
            data : {
                "user": new_data.user,
                "action": new_data.action,
                "is_active": new_data.is_active,
                'permission_profile' : new_data.permission_profile,
                "objects":[
                {"type":'dslam', id: new_data.dslams},
                {"type":'command', id: new_data.commands}
                ]}
            }).then(function (result) {
              if(parseInt (result.status) < 400)
              {
                var notification = alertify.notify('Done', 'success', 5, function () {
                });}
                else{
                   var notification = alertify.notify(result.statusText, 'error', 5, function () {
                   });
               }

           
            $scope.getUserPermissionList();
            new_data = '';


        }, function (err) {
        }
        );
}
};
$scope.permission_list_pagination = {};
$scope.permission_list_pagination.currentPage = 1;
$scope.permission_list_pagination.itemsPerPage = 10;
$scope.getUserPermissionList = function(){

   fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/users/permission-profile/',
    params:{
        page: $scope.permission_list_pagination.currentPage
    }
}).then(function (result) {
    $scope.permission_list_pagination.TotalItems = result.data.count ;
    $scope.user_permission_list = result.data.results ;

}, function (err) {
}
);
}
$scope.getUserPermissionList();

var getDslamList = function(){
 fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam/get_dslam_names/'
}).then(function (result) {
    $scope.dslam_list =  result.data.result ;

}, function (err) {
}
);
};
getDslamList();
var getCommandList = function(){
 fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/command/?page_size=50'
}).then(function (result) {
    $scope.command_list =  result.data ;

}, function (err) {
}
);
};
getCommandList();
$scope.GetPermissionProfileList = function(query){
    return fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/profile/' ,
        params:{
            search_name : query
        }

    }).then(function (result) {
        if(result.data.results){
            return result.data.results;
        }
        return [];

    }, function (err) {

    });
};
$scope.GetPermissionProfileList();

$scope.getUserList = function(query){
   return fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/users/' ,
    params : {
        username : query
    }

}).then(function (result) {
    if(result.data.results)
    {
        return  result.data.results;
    }
    return [];

}, function (err) {

});
}
$scope.getUserList();
$scope.singleUserPermissionData = function(id){
 fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/users/permission-profile/' + id + '/objects/'

}).then(function (result) {
    $scope.permission_detailes = result.data.result ;


}, function (err) {

});
}
$scope.DeletePermissionProfile =function(id){
  fetchResult.fetch_result({
    method: 'DELETE',
    url: ip + 'api/v1/users/permission-profile/' + id + '/',

}).then(function (result) {
      if(parseInt (result.status) < 400)
       {
        var notification = alertify.notify('Deleted', 'success', 5, function () {
        });}
        else{
         var notification = alertify.notify(result.statusText, 'error', 5, function () {
         });
     }

 $scope.getUserPermissionList();

}, function (err) {
}
);
}

$scope.UpdatePermission = function (size, module, searchParams , id) {
    $scope.dslam_added = [];
    $scope.command_added = [];
    $scope.id = id;
    $scope.user_info = searchParams.record.user_info.username;
    fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/users/permission-profile/' + id + '/objects/'

    }).then(function (result) {
        $scope.permission_detailes = result.data.result ;
        $scope.command_added = [];
        $scope.dslam_added = [];
        angular.forEach($scope.permission_detailes, function (v, k) {
            if(v.model_type == 'dslam')
            {
                $scope.dslam_added.push(v);
            }
            else{
                $scope.command_added.push(v);
            }
        });




        angular.forEach($scope.command_list, function (values, key) {
           angular.forEach($scope.permission_detailes, function (v, k) {
            if(v.object_id == values.id)
                values.ticked = true;
            else
                values.ticked = false;
        });
       });


    }, function (err) {

    });
    searchParams = angular.copy(searchParams);


    searchParams.record.dslam_name = [];
    searchParams.record.command_name = [];

    modalInstance = $uibModal.open({
        templateUrl: "myModalContent.html",
        size: size,
        animation: !1,
        controller: ["$scope", "$uibModalInstance", "module", "flag", "title", "message", "okValue", "cancelValue",
        function ($scope, $uibModalInstance, module, flag, title, message, okValue, cancelValue) {
            $scope.flag = flag;
            $scope.module = module;
            $scope.title = title;
            $scope.message = message;
            $scope.new_data = {
            };
            $scope.searchParams = searchParams;
            $scope.okValue = okValue;
            $scope.cancelValue = cancelValue;
            $scope.ok = function (new_data) {
                $uibModalInstance.close(new_data);
            };
            $scope.cancel = function () {
                $uibModalInstance.dismiss("cancel");
            };
        }
        ],
        scope: $scope,
        resolve: {
            flag: function () {
                return "primary";
            },
            module: function () {
                return module;
            },
            title: function () {
                return "Update User Permission";
            },
            message: function () {
                return '';
            },
            okValue: function () {
                return "";
            },
            cancelValue: function () {
                return "";
            },
        }
    }), modalInstance.result.then(function (new_data) {
    }, function () {
    });

};

$scope.UpdatePermissionInfo = function(new_data)   {
    new_data.commands = [];
    new_data.dslams = [];
    modalInstance.close();
    angular.forEach($scope.command_added , function(value,key){
        new_data.commands.push(value.object_id);
    });

    angular.forEach ($scope.dslam_added, function(value , key)
    {
       new_data.dslams.push(value.object_id);
   });

    var data =  {
        "user": new_data.user,
        "action": new_data.action,
        "is_active": new_data.is_active,
        'permission_profile' : new_data.permission_profile,
        'id':  $scope.id,
        "objects":[
        {"type":'dslam', id: new_data.dslams},
        {"type":'command', id: new_data.commands}
        ]};
        if( $scope.user_is_changed){
         data.user = $scope.new_user ;
     }

     if($scope.profile_is_changed)  { 
        data.permission_profile =   $scope.new_profile ;
    }  

    fetchResult.fetch_result({
        method: 'PUT',
        url: ip + 'api/v1/users/permission-profile/' +  $scope.id + '/',
        data : data


    }).then(function (result) {
     
         if(parseInt (result.status) < 400)
       {
        var notification = alertify.notify('Done', 'success', 5, function () {
        });}
        else{
         var notification = alertify.notify(result.statusText, 'error', 5, function () {
         });
     }
       $scope.getUserPermissionList();
       new_data = '';


   }, function (err) {
   }
   );
}
$scope.getDslam = function(query){
    $scope.exclude_dslam_id = [];
    angular.forEach($scope.dslam_added , function(value , key){

        $scope.exclude_dslam_id.push(value.object_id);
    });

    return fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/dslam/get_dslam_names/',
        params:{
            exclude_dslam_id : [$scope.exclude_dslam_id]  ,
            dslam_name : query

        }
    }).then(function (result) {
        if(result.data.result)
            return result.data.result;
        return [];



    }, function (err) {
    }
    );
}
$scope.edit = {};
$scope.getCommands = function(query){
 $scope.exclude_command_id = [];
 angular.forEach($scope.command_added , function(value , key){
    $scope.exclude_command_id.push(value.object_id);
});

 return fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/command/',
    params : {
       command_name : $scope.edit.command_name,
       exclude_command_id : [$scope.exclude_command_id],

   }
}).then(function (result) {
    if(result.data)
        return result.data;
    return [];
}, function (err) {
}
);
                  //  exclude_command_id
              }

              $scope.addTodslam_added = function(a){
                $scope.dslam_added.push({
                    object_id : $scope.edit.dslam_name.id,
                    object_name : $scope.edit.dslam_name.name,

                });
                $scope.edit.dslam_name = null;
                
            }
            $scope.addTocommand_added = function(){
                $scope.command_added.push({
                    object_id : $scope.edit.command_name.id,
                    object_name : $scope.edit.command_name.name,

                });
                $scope.edit.command_name = null;
            }

            $scope.userChanged = function(a){
                $scope.user_is_changed = true;
                $scope.new_user = a.id;
            }
            $scope.profileChanged = function(a){
              $scope.profile_is_changed = true;
              $scope.new_profile = a.id;
          }
          $scope.DeleteFromList = function(i){
            $scope.dslam_added.splice(i,1);
        }
        $scope.DeleteFromCList = function(i){
            $scope.command_added.splice(i,1);
        }

    });