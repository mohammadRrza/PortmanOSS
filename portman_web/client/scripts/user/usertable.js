angular.module('portman.usertable', ['myModule'])
    .config(function ($stateProvider) {
        $stateProvider
            .state('users', {
                url: '/users',
                views: {
                    'content': {
                        templateUrl: 'templates/user/user-table.html',
                         
                        controller: 'UserTableController'
                    }
                }
            });
    })
    .controller('UserTableController', ['$scope', 'fetchResult', '$http', '$state', 'uiGridConstants', 'ip' , '$timeout', function ($scope, fetchResult, $http, $state, uiGridConstants, ip , $timeout) {
        $scope.searchText = null;
        $scope.searchData = function () {
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
            enableHiding: false,
            enableColumnResizing: true,
            enableColResize: true,
            multiSelect: false,
            enableColumnMenus: false,
            enableHorizontalScrollbar: 0,

            //declare columns
            columnDefs: [
                
                {field: 'username', displayName: 'Username', width: "13%", enableSorting: true},
                {field: 'first_name', displayName: 'First Name', width: "13%", enableSorting: true},
                {field: 'last_name', displayName: 'Last Name', width: "13%", enableSorting: true},
                {field: 'reseller_info.name', displayName: 'reseller', width: "12%", enableSorting: true},
                {field: 'type', displayName: 'Type', width: "12%", enableSorting: false},
                {field: 'is_active', displayName: 'Active', width: "12%", enableSorting: false,
             cellTemplate: '<div ng-switch on="row.entity.is_active" style="margin:10px 15px;" >' +
                                        '<a ng-switch-when="true" href="javascript:;"  title="true"><i class="fa fa-check font-green-turquoise"></i></a>' +
                                        '<a ng-switch-when="false" href="javascript:;"  title="false"><i class="fa fa-times font-red"></i></a>' +
                                         +
                                    '</div>'
             
                         },
                {field: 'last_login', displayName: 'Last Login', width: "12%", enableSorting: false},
                {
                    field: 'action',
                    displayName: 'Action',
                    width: "13%",
                    cellTemplate: '<div ng-show="user_type == ADMIN || user_access_edit_user" class="actions" ><a style="margin:5px !important;" href="#/users/add/{$ row.entity.id $}" class="btn btn-circle btn-icon-only btn-default"><i class="icon-wrench"></i></a><button ng-confirm-click="grid.appScope.delete_user(row.entity.id)" ng-confirm-message="Are You Sure To Delete user?" class="btn btn-circle btn-icon-only btn-default"><i class="icon-trash"></i></button></div>',
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
        $scope.searchText = {};
        var getPage = function () {
            sort_field = null;
            if (paginationOptions.sort) {
                if (paginationOptions.sort.name === 'reseller_info.name') {
                    paginationOptions.sort.name = 'reseller';
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
                url: ip + 'api/v1/users/',
                params: {
                    page: paginationOptions.pageNumber,
                    page_size: paginationOptions.pageSize,
                    sort_field: sort_field,
                    username: $scope.searchText.user_name,
                    first_name : $scope.searchText.first_name,
                    last_name: $scope.searchText.last_name,
                    type : $scope.searchText.type
                }
            }).then(function mySucces(data) {
                $timeout(function(){
                $scope.gridOptions.totalItems = data.data.count;
                $scope.gridOptions.data = data.data.results;
                });
            
            }, function myError(response) {
            });
        };

        $scope.delete_user = function (id) {
            fetchResult.fetch_result({
                method: 'delete',
                url: ip + 'api/v1/users/' + id+'/'
            }).then(function (result) {
                    if(result.status < 400){
                        var notification = alertify.notify('Deleted', 'success', 5, function () {
                                    });
                    }
                    $state.reload();
                }, function (err) {
                }
            );
        };

        //inital gird view
        getPage();

    }]);
