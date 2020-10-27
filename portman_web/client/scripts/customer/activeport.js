angular.module('portman.customeractiveport', ['myModule'])
    .config(function ($stateProvider) {
        $stateProvider
            .state('customer-active-port', {
                url: '/subscriber/active-port',
                views: {
                    'content': {
                        templateUrl: 'templates/customer/active-port.html',
                         
                        controller: 'CustomerActivePortController'
                    }
                }
            });
    })
    .controller('CustomerActivePortController', ['$scope', 'fetchResult', '$http', '$state', 'uiGridConstants', 'ip' ,'$timeout' , function ($scope, fetchResult, $http, $state, uiGridConstants, ip , $timeout) {

        $scope.active_port_select = {reseller:'' , vlan:'' , customer:''};
        $scope.active_port_select.vlan=[];
        $scope.port_pvc = {
                            'vpi' : 0,
                            'vci' : 35,
                            'profile' : 'DEFVAL',
                            'mux' : 'llc',
                            'vlan_id': 1,
                            'priority' : 0
        };

        $scope.show_detailes = false;
        $scope.openDetailes = function(){
            $scope.show_detailes = !$scope.show_detailes ;
        };
        
       
                ////////////////////////////////////////
                ///////////grid options ///////////////
                ///////////////////////////////////////
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

            //declare columns
            columnDefs: [

                {
                    field: 'email',
                    displayName: 'Email',
                    width: "20%",
                    suppressSizeToFit: true,
                    enableSorting: false
                },

                {
                    field: 'lastname',
                    displayName: 'Family',
                    width: "20%",
                    cellTemplate: "<span style='font-family: BYekan !important'>{$ row.entity.lastname $} </span>"
                },

                {
                    field: 'identifier_key',
                    displayName: 'Identifier Key',
                    width: "20%",
                    enableSorting: true,
                },

                {
                    field: 'tel',
                    displayName: 'Tel',
                    width: "20%",
                    enableSorting: true,
                },

                {
                    field: 'telecom_center_id',
                    displayName: 'Telecom Center',
                    width: "20%",
                    enableSorting: true
                },
         


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
          var getPage = function () {
            send_params = null;
            sort_field = null;
            $scope.dslam_id=null;
            $scope.gridOptions.data = null;
              if (paginationOptions.sort) {
       
                if (paginationOptions.sort.sort.direction === 'desc') {
                    sort_field = '-' + paginationOptions.sort.name;
                }
                else {
                    sort_field = paginationOptions.sort.name;
                }
            }

             fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/customer-port/',
                    params : {
                        sort_field: sort_field,
                    }
                }).then(function (result) {
                    $timeout(function(){
                    $scope.gridOptions.totalItems = result.data.count;
                    $scope.gridOptions.data = result.data.results;
                    });
                  
                    }, function (err) {
                    }
                );
        };
        getPage();

                ////////////////////////////////////////
                ///////////grid options End///////////////
                ///////////////////////////////////////
        
       
            $scope.getResellerList = function(query){
            return fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/reseller',
                params :{
                    name : $scope.active_port_select.reseller
                }
            }).then(function (result) {
                console.log(result);
                    if(result.data.results){
                        return result.data.results
                    }
                    return [];
                   
                }, function (err) {
                }
            );
        }



            fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/command/?type=dslamport'
            }).then(function (result) {
                    $scope.commands = result.data;
                   
                }, function (err) {
                }
            );
   
        $scope.SelectReseller= function () {

            url = ip +  'api/v1/vlan/';
                fetchResult.fetch_result({
                    url: ip + 'api/v1/reseller/',
                }).then(function (result) {
                        $scope.reseller_active_port = result.data.results;//.data; 
                    }, function (err) {
                    }
                );
                fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/vlan/',
                    params: {reseller_id: $scope.active_port_select.reseller.id}
                }).then(function (result) {
                    $scope.vlan_list = result.data.results ;
                    }, function (err) {
                    }
                );
           
            $http.get(ip , $scope.active_port_select.reseller);
        }

        $scope.getCustomer = function(query){
         return $http({
                method: "GET",
                url: ip + 'api/v1/customer-port/',
                params: {
                    page_size: 1000,
                    username : query 
                }
            }).then(function mySucces(data) {
                if(data.data.results)
                {
                    return data.data.results ;
                }
                return [] ;
               // $scope.customer_list = data.data.results ;
               
            }, function myError(response) {
            });
        }
        
        $scope.getCustomer();
        $scope.check = function(){
           
           
            if($scope.active_port_select.reseller !== undefined ){
                if($scope.active_port_select.vlan_id === undefined )
                {
                    var notification = alertify.notify('Vlan is empty', 'error', 5, function () {
                        });
                   
                }
                else{
                    $scope.run_port_pvc();
                }
             
                
           }
           else{
            
                $scope.run_port_pvc();
           }
        }

        $scope.setButton = function(command){
            if(command == 'active'){
                    $scope.command_type = 'port pvc set';
            }
            else if(command == 'deactive'){
                     $scope.command_type = 'port pvc delete';
            }
            $scope.run_port_pvc();

        }
        $scope.run_port_pvc = function(){

                         if($scope.active_port_select.vlan_id === undefined){
                              var params = {
                            "type": "dslamport",
                            "is_queue": false,
                            'vpi' : $scope.port_pvc.vpi,
                            'vci' : $scope.port_pvc.vci,
                            'profile' : $scope.port_pvc.profile,
                            'mux' : $scope.port_pvc.mux,
                            'priority' : $scope.port_pvc.priority,
                            "command":  $scope.command_type ,
                             vlan_id : 1,
                         };
                        var posted_data = {
                        identifier_key : $scope.active_port_select.identifier_key.identifier_key,
                        "params": params,
                        
                    };
                         }
                         else{
                    var params = {
                            "type": "dslamport",
                            "is_queue": false,
                            'vpi' : $scope.port_pvc.vpi,
                            'vci' : $scope.port_pvc.vci,
                            'profile' : $scope.port_pvc.profile,
                            'mux' : $scope.port_pvc.mux,
                            'priority' : $scope.port_pvc.priority,
                            "command": $scope.command_type,
                             "vlan_id" : $scope.active_port_select.vlan_id.vlan_id,
                         };
                          var posted_data = {
                        identifier_key : $scope.active_port_select.identifier_key.identifier_key,
                        vid : $scope.active_port_select.vlan_id,
                        "params": params,
                        
                    };
                         }
                         
                         
                          fetchResult.fetch_result({
                    method: 'post',
                    url : ip + 'api/v1/customer-port/activeport/',
                    data: posted_data 
                
                }).then(function (result) {
                    
                    if(parseInt (result.status) >= 400 ){
                  var notification = alertify.notify(result.statusText, 'error', 5, function () {
                        });}
                  else{
                    var notification = alertify.notify('Done', 'success', 5, function () {
                        });
                  }
                   
                   
                }, function (err) {
                    var notification = alertify.notify('Done', 'error', 5, function () {
                        });
                   
                  
                });
        }
         
    }]);
