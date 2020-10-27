angular.module('portman.userauditlog', ['myModule', 'ngTouch', 'ui.grid', 'ui.grid.pagination', 'ui.grid.edit', 'ui.grid.cellNav', 'ui.grid.resizeColumns', 'ui.grid.autoResize' ])
    .config(function ($stateProvider) {
        $stateProvider
            .state('userauditlog', {
                url: '/users/auditlog',
                views: {
                    'content': {
                        templateUrl: 'templates/user/user-audit-log.html',
                          
                        controller: 'UserAuditLogController'
                    }
                }
            });
    })
    .controller('UserAuditLogController', ['$scope', 'fetchResult', '$http', 'uiGridConstants', '$state', 'ip' , function ($scope, fetchResult, $http, uiGridConstants, $state, ip) {
        $scope.ip = '';
        $scope.username = '';
        $scope.selectedaction = '';
        $scope.keywords = '';
       
       
            $scope.setCalendar = function(i,date){
                        if(i==1){
                            $scope.search.date_from = date;
                        }
                        else if (i==2){
                            $scope.search.date_to = date ; 

                        }
                     
            }
      

        fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/users/auditlog/actions/'
        }).then(function (result) {
                $scope.actions = result.data;
            }, function (err) {
            }
        );
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

            //declare columns
            columnDefs: [

                {
                    field: 'number',
                    displayName: '#',
                    width: 30,
                    cellTemplate: '<div class="ngCellText" data-ng-class="col.colIndex()"><span>{$ grid.renderContainers.body.visibleRowCache.indexOf(row)+1 $}</span></div>',
                    suppressSizeToFit: true,
                    enableSorting: false
                },

                {
                    field: 'id',
                    displayName: 'ID',
                    width: 40
                },

                {
                    field: 'username',
                    displayName: 'User Name',
                    width: 100,
                    enableSorting: true
                },

                {
                    field: 'action',
                    displayName: 'Action',
                    width: 180,
                    enableSorting: true
                },

                {
                    field: 'description',
                    displayName: 'description',
                    width: 360,
                    enableSorting: true
                },

                {
                    field: 'ip',
                    displayName: 'IP',
                    width: 115,
                    enableSorting: true
                },

                {
                    field: 'created_at',
                    displayName: 'Date Time',
                    width: 120,
                    enableSorting: true
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

        // fill ui-grid
        $scope.search = {username : '' , selected_action: '' ,keywords :'' ,ip:''};
        var getPage = function () {
            send_params = null;
            sort_field = null;
            if (paginationOptions.sort) {
                if (paginationOptions.sort.sort.direction === 'desc') {
                    sort_field = '-' + paginationOptions.sort.name;
                }
                else {
                    sort_field = paginationOptions.sort.name;
                }
            }
            $http({
                method: "GET",
                url: ip + 'api/v1/users/auditlog/',
                params: {
                    page: paginationOptions.pageNumber,
                    page_size: paginationOptions.pageSize,
                    sort_field: sort_field,
                    search_username: $scope.search.username,
                    search_ip: $scope.search.ip,
                    search_keywords: $scope.search.keywords,
                    search_action: $scope.search.selected_action,
                    search_date_from: $scope.search.date_from,
                    search_date_to: $scope.search.date_to
                }
            }).then(function mySucces(data) {
                
                $scope.gridOptions.totalItems = data.data.count;
                $scope.gridOptions.data = data.data.results;
            }, function myError(response) {
            });
        };

        $scope.showInfo = function (row) {
            //
        };

        //initial grid table
        getPage();

    }]);
