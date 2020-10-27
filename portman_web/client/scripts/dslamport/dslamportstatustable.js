angular.module('portman.dslamportstatustable', ['myModule', 'ngTouch', 'ui.grid', 'ui.grid.pagination', 'ui.grid.edit', 'ui.grid.cellNav', 'ui.grid.resizeColumns', 'ui.grid.autoResize', 'ngRangeSlider'])

    .config(function ($stateProvider, $urlRouterProvider) {
        $stateProvider
            .state('dslamportstatus', {
                url: '/dslamportstatus',
                views: {
                    'content': {
                        templateUrl: 'templates/dslamport/dslam-port-status-table.html',
                         
                        controller: 'DslamPortTableStatusController'
                    }
                },
            });
    })
    .controller('DslamPortTableStatusController', ['$scope','$rootScope' ,  'fetchResult', '$http', 'uiGridConstants', '$stateParams', 'ip','$timeout',
        function ($scope,$rootScope, fetchResult, $http, uiGridConstants, $stateParams, ip , $timeout) {
           console.log($rootScope.user_access_admin);
           if($rootScope.user_access_admin || $rootScope.user_access_view_dslam ){
                    $scope.gesture = '<a  href="#/dslam/{$ row.entity.dslam $}/report"> {$ COL_FIELD $} </a>'
            }
                    else{
                         $scope.gesture = '<a> {$ COL_FIELD $} </a>'
                    }
            $scope.downstream_snr_flag = '';
            $scope.upstream_snr_flag = '';
            $scope.downstream_attenuation_flag = '';
            $scope.upstream_attenuation_flag = '';
            $scope.slot_number = '';
            $scope.port_number = '';
            $scope.dslam_name = '';

            $scope.searchData = function () {
                paginationOptions.pageNumber = 1;
                getPage();
            }


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
                enableHorizontalScrollbar: 2,

                //declare columns
                columnDefs: [
                    {
                        field: 'dslam_info.name',
                        displayName: 'DSLAM',
                        width: 120,
                        enableSorting: true,
                        cellTemplate:  $scope.gesture
                    },
                    {
                        field: 'port_name',
                        displayName: 'Port Name',
                        width: 75,
                        enableSorting: true,
                        cellTemplate: '<a href="#/dslamport/{$ row.entity.dslam $}/{$ row.entity.id $}/status-report"> {$ COL_FIELD $} </a>'
                    },
                    {field: 'slot_number', displayName: 'Card', width: 40, enableSorting: true},
                    {field: 'port_number', displayName: 'Port', width: 40, enableSorting: true},
                    {field: 'admin_oper_status', displayName: 'Admin | Oper Status', width: 120, enableSorting: false, cellTemplate: '<div class="actions" style="margin:5px !important;"> {$ row.entity.admin_status $} | {$ row.entity.oper_status $}</div>'},
                    {field: 'updated_at', displayName: 'Updated At', width: 140, enableSorting: true},
                    {field: 'up_down_snr', displayName: 'Up | Down SNR', width: 90, enableSorting: false, cellTemplate: '<div class="actions" style="margin:5px !important;"> {$ row.entity.upstream_snr $} | {$ row.entity.downstream_snr $}</div>'},
                    {field: 'up_down_atten', displayName: 'Status', width: 80, enableSorting: true , cellTemplate: '<div  class="actions" style="margin:5px !important;"> {$ row.entity.downstream_snr $} | {$ row.entity.downstream_attenuation $}</div>'},
                    {field: 'upstream_snr_flag', displayName: 'Status', width: 80, enableSorting: true},
                    {field: 'downstream_snr_flag', displayName: 'Status', width: 80, enableSorting: true},
                    {field: 'upstream_attenuation_flag', displayName: 'Status', width: 80, enableSorting: true},
                    {field: 'downstream_attenuation_flag', displayName: 'Status', width: 80, enableSorting: true},
                    {field: 'line_profile_info.name', displayName: 'Line Profile', width: 110, enableSorting: true},
                    
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

                $http({
                    method: "GET",
                    url: ip + 'api/v1/dslam-port/',
                    params: {
                        page: paginationOptions.pageNumber,
                        page_size: paginationOptions.pageSize,
                        sort_field: sort_field,
                        search_down_snr_flag: $scope.downstream_snr_flag,
                        search_up_snr_flag: $scope.upstream_snr_flag,
                        search_down_atten_flag: $scope.downstream_attenuation_flag,
                        search_up_atten_flag: $scope.upstream_attenuation_flag,
                        search_slot_number: $scope.slot_number,
                        search_port_number: $scope.port_number,
                        search_dslam_name: $scope.dslam_name
                    }
                }).then(function mySucces(data) {
                   
                    $timeout(function(){
                        $scope.gridOptions.totalItems = data.data.count;
                    $scope.gridOptions.data = data.data.results;
                  //   $timeout(function() {
                  //   document.getElementById('click_table').click();
                  // }, 1000);
                    });
                    
                 
                }, function myError(response) {
                });
            }
            $scope.getDslamNameList = function(query){
               return fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/dslam/',
                      params: {
                        page: paginationOptions.pageNumber,
                        page_size: paginationOptions.pageSize,
                        sort_field: sort_field,
                        search_dslam: query
                    }
                }).then(function (result) {
                    if(result.data.results){
                        return result.data.results
                    }
                    return [];
                        
                    }, function (err) {
                    }
                )
              
        }

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
            
            else if ((charCode < 48 || charCode > 57) && (charCode < 96 || charCode > 105) &&
        charCode !== 46 &&
        charCode !== 8 &&
        charCode !== 37 &&
        charCode !== 39 && charCode !== 09)
        keyEvent.preventDefault();
        }

        }]);
