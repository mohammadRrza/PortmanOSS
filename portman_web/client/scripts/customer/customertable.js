angular.module('portman.customertable', ['myModule'])
    .config(function ($stateProvider) {
        $stateProvider
            .state('subscribers', {
                url: '/subscribers',
                views: {
                    'content': {
                        templateUrl: 'templates/customer/customer-table.html',
                        
                        controller: 'CustomerTableController'
                    }
                }
            });
    })
    .controller('CustomerTableController', ['$scope', 'fetchResult', '$http', '$state', 'uiGridConstants', 'ip' , '$timeout', function ($scope, fetchResult, $http, $state, uiGridConstants, ip , $timeout) {
        $scope.searchText = null;
        $scope.search = {};

        $scope.active_port_select = {reseller:'' , vlan:'' , customer:''};
        $scope.active_port_select.vlan=[];

        fetchResult.loadFile('global/plugins/select2/css/select2.min.css');
        fetchResult.loadFile('global/plugins/select2/js/select2.full.min.js', function () {
            fetchResult.fetch_result({
                url: ip + 'api/v1/reseller/',
            }).then(function (result) {
                    $scope.reseller_active_port = result.data.results;//.data;
                    $(".select-line-profile-data-array").select2({
                        data: $scope.reseller_active_port
                    });
                }, function (err) {
                }
            );
            fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/command/?type=dslamport'
            }).then(function (result) {
                    $scope.commands = result.data;
                    $(".select-command-type-data-array").select2({
                        data: $scope.commands
                    });
                }, function (err) {
                }
            );
        });
        $scope.SelectReseller= function () {
            url = ip +  'api/v1/vlan/';
            fetchResult.loadFile('global/plugins/select2/js/select2.full.min.js', function () {
                fetchResult.fetch_result({
                    url: ip + 'api/v1/reseller/',
                }).then(function (result) {
                        $scope.reseller_active_port = result.data.results;//.data;
                        $(".select-line-profile-data-array").select2({
                            data: $scope.reseller_active_port
                        });
                    }, function (err) {
                    }
                );
                fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/vlan/',
                    params: {reseller_id: $scope.active_port_select.reseller}
                }).then(function (result) {
                        
                        $(".select-command-type-data-array1").select2({
                            data: result.data
                        });
                    }, function (err) {
                    }
                );
            });
            $http.get(ip , $scope.active_port_select.reseller);
        }
        $scope.searchData = function () {
            getPage();
        };


        $scope.totalServerItems = 0;
        var paginationOptions = {
            pageNumber: 1,
            pageSize: 10,
            sort: null
        };
        $scope.avtivePort = {vlan:''};
        $scope.activeCustomerPort = function (identifier , user) {
           
            fetchResult.fetch_result({
                method: 'post',
                url: ip + 'api/v1/customer-port/activeport/',
                data : {
                    vlan : $scope.avtivePort.vlan,
                    identifier_key : identifier,
                   
                }
            }).then(function (result) {
               
                    $state.reload();
                }, function (err) {
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
            enableHorizontalScrollbar: 2,

           
            columnDefs: [
               
                {field: 'username', displayName: 'Username', width: 140, enableSorting: true},
                {field: 'identifier_key', displayName: 'Identifier Key', width: 180, enableSorting: true},
                {field: 'firstname', displayName: 'First Name', width: 120, enableSorting: true , 
                    cellTemplate: "<span style='font-family: BYekan !important'>{$ row.entity.firstname $} </span>"},
                {field: 'lastname', displayName: 'Last Name', width: 120, enableSorting: true , 
                cellTemplate: "<span style='font-family: BYekan !important'>{$ row.entity.lastname $} </span>"},
                {field: 'email', displayName: 'Email', width: 180, enableSorting: false},
                {field: 'tel', displayName: 'Tel', width: 140, enableSorting: false},
                {field: 'mobile', displayName: 'mobile', width: 140, enableSorting: false},
                {field: 'national_code', displayName: 'National Code', width: 140, enableSorting: false},
                {
                    field: 'action',
                    displayName: 'Action',
                    width: 140,
                    cellTemplate: '<div class="actions" ><a style="margin:5px !important;" title="edit" href="#/edit-subscriber/{$ row.entity.id $}"  class="btn btn-circle btn-icon-only btn-default"><i class="icon-wrench"></i></a><button title="Delete" ng-confirm-click="grid.appScope.delete_customer(row.entity.id)" ng-confirm-message="Are You Sure To Delete Subscriber?" class="btn btn-circle btn-icon-only btn-default"><i class="icon-trash"></i></button></div>',
                    enableSorting: false
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
        var getPage = function () {
            var sort_field = null;
            if (paginationOptions.sort) {
                if (paginationOptions.sort.name === 'dslam_info.name') {
                    paginationOptions.sort.name = 'dslam';
                }

                if (paginationOptions.sort.sort.direction === 'desc') {
                    sort_field = '-' + paginationOptions.sort.name;
                }
                else {
                    sort_field = paginationOptions.sort.name;
                }
            }
            console.log($scope.search.mail);
            $http({
                method: "GET",
                url: ip + 'api/v1/customer-port/',
                params: {
                    page: paginationOptions.pageNumber,
                    page_size: paginationOptions.pageSize,
                    sort_field: sort_field,
                    firstname : $scope.search.fname ,
                    identifier_key : $scope.search.identifier ,
                    lastname : $scope.search.lname,
                    username : $scope.search.username,
                    email : $scope.search.mail,
                    tel : $scope.search.tel,
                    mobile : $scope.search.mobile ,
                    national_code : $scope.search.code,

                }
            }).then(function mySucces(data) {
                $timeout(function(){
                $scope.gridOptions.totalItems = data.data.count;
                $scope.gridOptions.data = data.data.results;
                });
               
            }, function myError(response) {
            });
        };

        $scope.delete_customer = function (id) {
            fetchResult.fetch_result({
                method: 'delete',
                url: ip + 'api/v1/customer-port/' + id
            }).then(function (result) {
                    $state.reload();
                }, function (err) {
                }
            );
        };

        //inital gird view
        getPage();

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
            
            else if ((charCode < 48 || charCode > 57) &&   (charCode < 96 || charCode > 105)&&
        charCode !== 46 &&
        charCode !== 8 &&
        charCode !== 37 &&
        charCode !== 39 && charCode !== 09)
        keyEvent.preventDefault();
        }
    }]);
