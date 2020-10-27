angular.module('portman.dslamtable', ['myModule', 'ngTouch', 'ui.grid', 'ui.grid.pagination', 'ui.grid.edit', 'ui.grid.cellNav', 'ui.grid.resizeColumns', 'ui.grid.autoResize'])
.config(function ($stateProvider) {
    $stateProvider
    .state('dslams', {
        url: '/dslams',
        views: {
            'content': {
                templateUrl: 'templates/dslam/dslam-table.html',
                
                controller: 'DslamTableController'
            }
        }
    });
})
.controller('DslamTableController', ['$scope','$rootScope' , 'fetchResult', '$http', 'uiGridConstants', '$state', 'ip' , '$timeout', function ($scope,$rootScope, fetchResult, $http, uiGridConstants, $state, ip , $timeout) {
    $scope.ip = '';
    $scope.dslam = '';
    $scope.status = '';
    $scope.active = '';
    $scope.city = '';
    $scope.telecom = '';
    $scope.selected_telecom = '';
    $scope.selected_city = '';

    fetchResult.loadFile('global/plugins/select2/css/select2.min.css');
    $scope.getTelecomList = function(query){
        return fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/telecom-center/' ,
            params: {
                search_city: $scope.selected_city.id,
                search_name : query
            }
        }).then(function (result) {
            if (result.data.results)
            { 
                return result.data.results ;
            }
            return [];
            
        }, function (err) {
        }
        );
    }
    $scope.getTelecomList();
    $scope.getProvList = function(query){
        return fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/city/?parent=all',
            params: {
                city_name : query
            }
        }).then(function (result) {
            if(result.data.results){
                return result.data.results;
            }
            return [];
            
        }, function (err) {
        }
        );
    }
    $scope.getProvList();
     $scope.getCityList = function () {
              
           return fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/city/?parent=' + $scope.selected_pro.id,
                params : {
                    city_name : $scope.selected_city
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

    $scope.searchData = function () {
        paginationOptions.pageNumber = 1;
        $scope.gridApi.pagination.seek(1);
        getPage();
    };

    $scope.totalServerItems = 0;
    var paginationOptions = {
        pageNumber: 1,
        pageSize: 10,
        sort: null
    };

    $scope.gridOptions = {
        paginationPageSizes: [10, 25, 50, 75],
        paginationPageSize: 10,
        useExternalPagination: true,
        useExternalSorting: true,
        rowHeight: 45,
        enableRowSelection: true,
        enableHiding: false,
        enableColumnResizing: true,
        enableColResize: true,
        multiSelect: false,
        enableColumnMenus: false,
        enableHorizontalScrollbar: 2,
        enableRowHashing: false,

            //declare columns
            columnDefs: [

            {
                field: 'name',
                displayName: 'DSLAM Name',
                width: '12%',
                enableSorting: true,
                cellTemplate: '<div><a href="#/dslam/{$ row.entity.id $}/report">{$ COL_FIELD $} <br/> {$ row.entity.ip $}</a></div>'
            },

            {
                field: 'hostname',
                displayName: 'Host Name',
                width: '8%',
                enableSorting: true,
            },

            {
                field: 'telecom_center',
                displayName: 'Telecom Center',
                width: '8%',
                enableSorting: true,
                cellTemplate: "<span> {$ row.entity.telecom_center_info.name $} </span>"
            },
            {
                field: 'city',
                displayName: 'City',
                width: '8%',
                enableSorting: true,
                cellTemplate: "<span style='font-family: BYekan !important'>{$ row.entity.telecom_center_info.city_info.text $} </span>"
            },
            {
               field: 'version',
                displayName: 'Version',
                width: '7%',
                
            },

            {
                field: 'dslam_type_info.text',
                displayName: 'Type',
                width: '7%',
                enableSorting: true
            },
            {
                field: 'uptime',
                displayName: 'Up Time',
                width: '7%',
                enableSorting: false,

            },
             {
                field: 'dslam_availability',
                displayName: 'Availability',
                width: '5%',
                enableSorting: false,
                cellTemplate: '<span>{$ row.entity.dslam_availability $} % </span>'

            },

            {
                field: 'total_up_down',
                displayName: 'Total/Up/Down',
                width: '8%',
                enableSorting: false,
                cellTemplate: '<span>{$ row.entity.total_ports_count $} / {$ row.entity.up_ports_count $} / {$ row.entity.down_ports_count $}</span>'
            },
            {
                field: 'status',
                displayName: 'Status',
                width: '5%',
                enableSorting: true,
                cellTemplate: 
                '<div ng-switch on="row.entity.status" id="status_led" style="margin:10px 15px;">' +
                '<a ng-switch-when="new" href="javascript:;" class="yellow"  title="new"><i class="fa fa-ellipsis-h font-yellow"></i></a>' +
                '<a ng-switch-when="ready" href="javascript:;" class="green-turquoise" title="ready"><i class="fa fa-check font-green-turquoise"></i></a>' +
                '<a ng-switch-when="updating" href="javascript:;" class="green"  title="updating"><i class="fa fa-spinner fa-spin font-green"></i></a>' +
                '<a ng-switch-when="error" href="javascript:;" class="red" title="error"><i class="fa fa-close font-red"></i></a>' +
                '</div>'
            },
            {
                field: 'active',
                displayName: 'Active',
                width: '5%',
                enableSorting: true,
                cellTemplate: '<div ng-switch on="row.entity.active" id="status_led" style="margin:10px 15px;">' +
                '<a ng-switch-when="true" href="javascript:;" title="true"><i class="fa fa-check font-green-turquoise"></i></a>' +
                '<a ng-switch-default href="javascript:;" title="false"><i class="fa fa-remove font-red"></i></a>' +
                '</div>'
            },

            {
                field: 'action',
                displayName: 'Action',
                width: '20%',
                cellTemplate:  
                
                '<div class="btn-group text-center" style="position:absolute!important;margin-left:-40px;margin-top:5px;">'+
                '<a class="btn green " href="javascript:;" data-toggle="dropdown" aria-expanded="true">'+
                'Actions'+
                ' <i class="fa fa-angle-down"></i>'+
                '</a><div class="dropdown-backdrop"></div>'+
                '<ul class="dropdown-menu" >'+
                '<li  title="show dslam information">'+
                '<a ng-click="grid.appScope.showInfo(row.entity)" href="javascript:;">'+
                '<i class="icon-info"></i> Show Information </a>'+
                '</li>'+
                '<li ng-show="user_type == ADMIN || user_access_edit_dslam "   title="edit dslam">'+
                '<a href="#/add-dslam/{$ row.entity.id $}">'+
                '<i class="fa fa-pencil"></i> Edit </a>'+
                '</li>'+
                // '<li   title="show dslam ports">'+
                // '<a href="#/dslamport/{$ row.entity.id $}">'+
                // '<i class="icon-directions"></i> Dslam Ports </a>'+
                // '</li>'+
                '<li ng-show="user_type == ADMIN || user_access_edit_dslam "  title="delete dslam">'+
                '<a ng-confirm-message="Are you sure you want to delete dslam?"  ng-confirm-click="grid.appScope.delete_dslam(row.entity.id)"  >'+
                '<i class="fa fa-trash"></i> Delete </a>'+
                '</li>'+
                '<li  title="Update Dslam">'+
                '<a ng-click="grid.appScope.update_single_dslam_port({$ row.entity.id  $})"  >'+
                '<i class="i"></i> Update Dslam Port </a>'+
                '</li>'+
                '<li  title="General Update">'+
                '<a ng-click="grid.appScope.update_single_dslam_general({$ row.entity.id  $})"  >'+
                '<i class="i"></i> General Update   </a>'+
                '</li>'+
                '</ul></div>' ,
                
                enableSorting: false,
                allowCellFocus: false
                
                
            }

            ],

            //declare api
            onRegisterApi: function (gridApi) {
                $scope.gridApi = gridApi;


                //fire sortchanged function
                $scope.gridApi.core.on.sortChanged($scope, function (grid, sortColumns) {
                    if (sortColumns.length > 1) {
                        var column = null;
                        for (var j = 0; j < grid.columns.length; j++) {
                            if (grid.columns[j].name === sortColumns[0].field) {
                                column = grid.columns[j];
                                break;
                            }
                        }
                        if (column) {
                            sortColumns[1].sort.priority = 1; // have to do this otherwise the priority keeps going up.
                            column.unsort();
                        }
                    }
                    if (sortColumns.length == 0) {
                        paginationOptions.sort = null;
                    }
                    else {
                        paginationOptions.sort = sortColumns[0];
                    }
                    getPage();
                });


                //fire pagination changed function
                gridApi.pagination.on.paginationChanged($scope, function (newPage, pageSize) {
                    paginationOptions.pageNumber = newPage;
                    paginationOptions.pageSize = pageSize;
                    getPage();
                });

            }
        };

        $scope.selected_pro = [];
        var getPage = function () {
            send_params = null;
            sort_field = null;
            $scope.dslam_id=null;
            $scope.gridOptions.data = null;
            if (paginationOptions.sort) {
                if (paginationOptions.sort.name === 'telecom_center_info') {
                    paginationOptions.sort.name = 'telecom_center';
                }
                if (paginationOptions.sort.name === 'dslam_type_info.text') {
                    paginationOptions.sort.name = 'dslam_type';
                }

                if (paginationOptions.sort.sort.direction === 'desc') {
                    sort_field = '-' + paginationOptions.sort.name;
                }
                else {
                    sort_field = paginationOptions.sort.name;
                }
            }
            

            $http({
                method: "GET",
                url: ip + 'api/v1/dslam/',
                params: {
                    page: paginationOptions.pageNumber,
                    page_size: paginationOptions.pageSize,
                    sort_field: sort_field,
                    search_dslam: ($scope.dslam.name)? $scope.dslam.name : $scope.dslam,
                    search_ip: $scope.ip,
                    search_type: ($scope.search_type)? $scope.search_type.id : $scope.search_type,
                    search_telecom: $scope.telecom,
                    search_active: $scope.active,
                    search_status: $scope.status,
                    search_telecom: $scope.selected_telecom.id,
                  //  search_province : $scope.selected_pro.id,
                    search_city: ($scope.selected_city.id) ? $scope.selected_city.id :  $scope.selected_pro.id
                }
            }).then(function mySucces(data) {
              //  console.log(data.data.results);
                $scope.gridOptions.data = [];
                $scope.data = data.data.results;
                
                $timeout(function () {
                  $scope.gridOptions.data = $scope.data;
                  $scope.gridOptions.totalItems = data.data.count;
                  $timeout(function() {
                    document.getElementById('status_led').click();
                }, 100);
                 
              });

                
                
            }, function myError(response) {
            });
        };
        $scope.searchName = function(query){
            if($scope.selected_pro){
                if($scope.selected_pro.id)
                {
                    $scope.send_id_for_dslam = $scope.selected_pro.id;
                }
            }
             if($scope.selected_city){
                if($scope.selected_city.id)
                {
                    $scope.send_id_for_dslam = $scope.selected_city.id;
                }
            }
         return  $http({
            method: "GET",
            url: ip + 'api/v1/dslam/',
            params: {
                page: paginationOptions.pageNumber,
                page_size: paginationOptions.pageSize,
                search_city : $scope.send_id_for_dslam ,
                search_dslam: query,
            }
        }).then(function mySucces(data) {
            if(data.data.results){
                return data.data.results;
            }
            return [];
            
        }, function myError(response) {
        });
    }
    $scope.searchIp = function(query){
     return  $http({
        method: "GET",
        url: ip + 'api/v1/dslam/',
        params: {
            page: paginationOptions.pageNumber,
            page_size: paginationOptions.pageSize,
            search_ip: query,
        }
    }).then(function mySucces(data) {
        if(data.data.results){
            return data.data.results;
        }
        return [];
        
    }, function myError(response) {
    });
}
$scope.searchIp();

$scope.showInfo = function (row) {
    $scope.name = row.name;
    $scope.dslam_type = row.dslam_type_info.text;
    $scope.ip = row.ip;
    $scope.active = row.active;
    $scope.active = row.active;
    $scope.status = row.status;
    $scope.conn_type = row.conn_type;
    $scope.snmp_community = row.snmp_community;
    $scope.snmp_port = row.snmp_port;
    $scope.snmp_timeout = row.snmp_timeout;
    $scope.telecom_center = row.telecom_center_info.name + '->' + row.telecom_center_info.city_info.name;
    $scope.updated_at = row.updated_at;
    $scope.total_ports_count = row.total_ports_count;
    $scope.up_ports_count = row.up_ports_count;
    $scope.down_ports_count = row.down_ports_count;
    $scope.last_sync_duration = row.last_sync_duration;

    $('#showAboutBox').show('slow');
};

$scope.show_delete_box = function (id) {
    $scope.dslam_id = id;
    $('.delete_box').show('fast');
};

$scope.update_single_dslam_port = function(id ){

  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam/' + id + '/scan/',
    params : {
        type : 'port'
    }
}).then(function (result) {
    if(parseInt (result.status) < 400)
       {
        var notification = alertify.notify('Dslam Updated', 'success', 5, function () {
        });}
        else{
         var notification = alertify.notify(result.statusText, 'error', 5, function () {
         });
     }

 
}, function (err) {
    var notification = alertify.notify('error', 'error', 5, function () {
    });
}
);

}
$scope.update_single_dslam_general = function(id ){
  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam/' + id + '/scan/',
    params : {
        type : 'general'
    }
}).then(function (result) {
    if(parseInt (result.status) < 400)
       {
        var notification = alertify.notify('Dslam Updated', 'success', 5, function () {
        });}
        else{
         var notification = alertify.notify(result.statusText, 'error', 5, function () {
         });
     }

 
}, function (err) {
    var notification = alertify.notify('error', 'error', 5, function () {
    });
}
);

}

$scope.delete_dslam = function (dslam) {

    fetchResult.fetch_result({
        method: 'delete',
        url: ip + 'api/v1/dslam/' + dslam + '/'
    }).then(function (result) {
        if(result.status < 400 ){

             var notification = alertify.notify('Done', 'success', 5, function () {
    });
              $state.reload();
        }
        else{
             var notification = alertify.notify(result.statusText, 'error', 5, function () {
    });
        }
       // $state.reload();
    }, function (err) {
    }
    );
};

$scope.getValue=function(strObj){
    if(strObj!=null){
      return JSON.parse(JSON.stringify(strObj).replace(/\'/g, "\"")).value;
  }else{
    return "";
}
}

getPage();

fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam/dslam-type/'
}).then(function (result) {
    $scope.vendor_list = result.data;
}, function (err) {
}
);



}]);
