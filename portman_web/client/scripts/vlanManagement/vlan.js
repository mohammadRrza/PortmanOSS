    angular.module('portman.vlan', ['myModule','ui.grid', 'ui.grid.pagination', 'ui.grid.edit', 'ui.grid.cellNav', 'ui.grid.resizeColumns', 'ui.grid.autoResize'  ])
    .config(function ($stateProvider) {
    $stateProvider
    .state('vlan', {
        url: '/vlan',
        views: {
            'content': {
                templateUrl: 'templates/vlanManagement/vlan.html',
                controller: 'vlanManagementController'
            }
        }
    });
    })
    .controller('vlanManagementController', function ($scope, fetchResult ,$http, ip , $timeout ){

        $scope.assign = {} ;
    $scope.selected = {};
    paginationOptions= {};
    $scope.getVlanList = function(query){
        return fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/vlan/',
            params:{
                vlan_name : query
            }
        }).then(function (result) {


         if (result.data.results)
            return result.data.results;
        return [];
    }, function (err) {
    }
    );
    }
    $scope.getVlanList();
    $scope.assign.reseller = [];
    $scope.getVlanListByReseller = function(query){
        return fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/vlan/',
            params:{
                vlan_name : query,
                reseller_id : $scope.assign.reseller.id
            }
        }).then(function (result) {


         if (result.data.results)
            return result.data.results;
        return [];
    }, function (err) {
    }
    );
    }
    $scope.getVlanListByReseller();
    $scope.getResellerList = function(query){
     return fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/reseller/',
        params:{
            name : query
        }
    }).then(function (result) {
        console.log(result);
        if( result.data.results){
            return  result.data.results

        }
        return [];

    }, function (err) {
    }
    );
    }
    $scope.getResellerList();
    $scope.SetVlan = function (){
      console.log('vlan' , $scope.selected.vlan3.id ,$scope.selected.vlan3);
    fetchResult.fetch_result({
        method: 'PUT',
        url: ip + 'api/v1/vlan/'+ $scope.selected.vlan3.id +'/' ,
        data : {
            dslam_id : $scope.dslam_id,
            reseller:$scope.selected.reseller.id,
            vlan_name:$scope.selected.vlan3.vlan_id,
            vlan_id:$scope.selected.vlan3.vlan_id,
            params :{
                type: "dslam",
                vlan_name:$scope.selected.vlan3.vlan_id,
                vlan_id:$scope.selected.vlan3.vlan_id
            }

        }
    }).then(function (result) {
        if(result.status < 400){
            $scope.selected.vlan3 = '';
            $scope.selected.reseller = '';
            var notification = alertify.notify('Done', 'success', 5, function () {
            });

        }
        else{
            var notification = alertify.notify(result.statusText, 'error', 5, function () {
            });
        }

    }, function () {
        var notification = alertify.notify('Bad Data', 'error', 5, function () {
        });
    }
    );

    }


    $scope.gridOptions = {
    paginationPageSizes: [10, 25, 50, 75],
    paginationPageSize: 10,
    useExternalPagination: true,
    useExternalSorting: true,
    rowHeight: 45,
    enableHiding: false,
    enableColumnResizing: true,
    enableColResize: true,
    multiSelect: false,
    enableColumnMenus: false,
    enableHorizontalScrollbar: 0,

            //declare columns
            columnDefs: [


            {field: 'vlan_id', displayName: 'Vlan ID', width: "20%", enableSorting: true},
            {field: 'vlan_name', displayName: 'Vlan Name', width: "20%", enableSorting: true},
            {field: 'ports_count', displayName: 'Port Count', width: "15%", enableSorting: true},
            {field: 'dslam_count', displayName: 'Dslam Count', width: "15%", enableSorting: true},
            {field: 'reseller_info.name', displayName: 'Reseller Name', width: "15%", enableSorting: true},

            {field: 'Action', displayName: 'Action', width: "15%",
            enableSorting: false ,  enableRowHashing: false,
            cellTemplate : '<button style="margin:5px;" class="btn btn-circle btn-icon-only btn-default"  ng-confirm-click="grid.appScope.deleteVlan(row.entity.id)" ng-confirm-message="Are You Sure To Delete Vlan?"><i class="icon-trash"></i></button>'
        }
        ],

            onRegisterApi: function (gridApi) {
                $scope.gridApi = gridApi;
                paginationOptions.pageNumber = 1;

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
                    $scope.getPage();
                });


                gridApi.pagination.on.paginationChanged($scope, function (newPage, pageSize) {
                    paginationOptions.pageNumber = newPage;
                    paginationOptions.pageSize = pageSize;
                    $scope.getPage();
                });

                $scope.gridApi.core.on.filterChanged($scope, function () {
                    if ($scope.gridApi.pagination.getPage() > 1) {
                        alert('change');
                    }
                });

            }
        };
        $scope.search = {};

        $scope.getPage = function () {
            sort_field = null;
            if (paginationOptions.sort) {
                     if (paginationOptions.sort.sort.direction === 'desc') {
                    sort_field = '-' + paginationOptions.sort.name;
                }
                else {
                    sort_field = paginationOptions.sort.name;
                }
            }
            var  params = {
                sort_field: sort_field,
             page: paginationOptions.pageNumber ,
             page_size : paginationOptions.pageSize,
                  vlan_id : ($scope.search.vlan_id) ? $scope.search.vlan_id.vlan_id : $scope.search.vlan_id ,
                  dslam_id : ($scope.search.dslam) ? $scope.search.dslam.id : $scope.search.dslam,
                  reseller_id : ($scope.search.reseller) ? $scope.search.reseller.id : $scope.search.reseller,
                  vlan_name : ($scope.search.vlan_name) ? $scope.search.vlan_name.vlan_name : $scope.search.vlan_name ,

              }


              fetchResult.fetch_result({
                method: "GET",
                url: ip + 'api/v1/vlan/',
                params : params


            }).then(function mySucces(data) {

              $scope.gridOptions.data = [];


              $timeout(function(){
                $scope.gridOptions.totalItems = data.data.count;
                Array.prototype.push.apply($scope.gridOptions.data, data.data.results);

            });

          }, function myError(response) {
          });
        };
        $scope.getPage();
        $scope.searchName = function(query){
           return  $http({
            method: "GET",
            url: ip + 'api/v1/dslam/',
            params: {
                page_size: 10,
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

    $scope.CreateNewVlan = function(){
      fetchResult.fetch_result({
        method: "POST",
        url: ip + 'api/v1/vlan/',
        data : {
            "vlan_name": $scope.selected.vlan2,
            "vlan_id": $scope.selected.vlan1
        }

    }).then(function mySucces(data) {
        if(parseInt(data.status) < 400)
        {
            $scope.selected.vlan1 = '';
            $scope.selected.vlan2 = '';
            var notification = alertify.notify('Done', 'success', 5, function () {
            });
        }
        else{
            var notification = alertify.notify(data.statusText, 'error', 5, function () {
            });
        }

    }, function myError(response) {
    });

    }
    $scope.getSubscriberList = function(query){

    return fetchResult.fetch_result({
    method: "GET",
    url: ip + 'api/v1/customer-port',
    params : {
        tel : query
    }

    }).then(function mySucces(data) {

    if(data.data.results){
     return data.data.results;
    }
    return [];


    }, function myError(response) {
    });
    }

    $scope.deleteVlan = function(id){

    fetchResult.fetch_result({
        method: "DELETE",
        url: ip + 'api/v1/vlan/' + id + '/',

    }).then(function mySucces(data) {
        $scope.getPage();

        if(parseInt (data.status) <400){
            var notification = alertify.notify('Done', 'success', 5, function () {
            });}
            else{
                var notification = alertify.notify(data.statusText, 'error', 5, function () {
                });
            }


        }, function myError(response) {
        });
    }


    $scope.checkData = function(){
    $scope.assign.vlan_id = '';
    $scope.assign.reseller = '';
    $scope.assign.flag = '' ;
    $scope.assign.new_vlan_id = '';
    $scope.assign.identifier = '' ;
    $scope.assign.dslam = '';
    $scope.assign.card = '';
    $scope.assign.port = '';
    }

    $scope.getIdentifierKey = function(value){
    return fetchResult.fetch_result({
        method: "GET",
        url: ip + 'api/v1/mdfdslam/',
        params:{
            page_size : 10 ,
            search_identifier_key : value
      }

    }).then(function mySucces(data) {
       console.log(data);
       if(data.data.results)
       {
       return data.data.results ;
        }
    return [] ;


        }, function myError(response) {
        });
    }
    $scope.getIdentifierKey();

    $scope.assignToSubscribers = function () {
    if($scope.assign.subscriber == "reseller"){
       $scope.send_data = {
        'new_vlan_id' : $scope.assign.vlan_id.vlan_id ,

        reseller_vlan : {
                'flag' : $scope.assign.flag ? $scope.assign.flag : null,
                'reseller_id' : $scope.assign.reseller.id,
                'vlan_id' : $scope.assign.new_vlan_id.vlan_id ,
            }
        }
    }
    else if($scope.assign.subscriber == "identifier"){
        $scope.send_data = {
        'new_vlan_id' : $scope.assign.vlan_id.vlan_id ,
        'identifier_key' : $scope.assign.identifier ,

        }
    }
    else{
        $scope.send_data = {
        'new_vlan_id' : $scope.assign.vlan_id.vlan_id ,

        'card_port' : {
            'dslam_id' : $scope.assign.dslam.id ,
            'port_number' : $scope.assign.port,
            'slot_number' : $scope.assign.card,
        }

        }
    }
       fetchResult.fetch_result({
        method: "POST",
        url: ip + 'api/v1/vlan/assign_to_subscibers/',
        data : $scope.send_data

    }).then(function mySucces(data) {
        if(parseInt (data.status) <400){
            var notification = alertify.notify('Done', 'success', 5, function () {
            });}
            else{
                var notification = alertify.notify(data.statusText, 'error', 5, function () {
                });
            }


        }, function myError(response) {
        });

    }

    $scope.searchName = function(query){
         return  $http({
            method: "GET",
            url: ip + 'api/v1/dslam/',
            params: {
                page: paginationOptions.pageNumber,
                page_size: 10,
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


    });
