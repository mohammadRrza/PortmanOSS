angular.module('portman.resellertable', ['myModule'])
    .config(function ($stateProvider) {
        $stateProvider
            .state('resellers', {
                url: '/resellers',
                views: {
                    'content': {
                        templateUrl: 'templates/reseller/reseller-table.html',
                         
                        controller: 'ResellerTableController'
                    }
                }
            });
    })
    .controller('ResellerTableController', ['$scope', 'fetchResult', '$http', '$state', 'uiGridConstants', 'ip','$timeout', function ($scope, fetchResult, $http, $state, uiGridConstants, ip , $timeout) {
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
            enableHorizontalScrollbar: 2,

            //declare columns
            columnDefs: [
                
                {field: 'name', displayName: 'Name', width: "15%", enableSorting: true ,
                    cellTemplate: "<a href='#/reseller/{$ row.entity.id $}/report'>{$ row.entity.name $} </a>"          
                      },


                {field: 'vpi', displayName: 'VPI', width: "5%", enableSorting: false},
                {field: 'vci', displayName: 'VCI', width: "5%", enableSorting: false},

                {field: 'tel', displayName: 'Tel', width: "15%", enableSorting: false},
                {field: 'fax', displayName: 'Fax', width: "15%", enableSorting: false},
                {field: 'city_info.text', displayName: 'City', width: "20%", enableSorting: true ,
            cellTemplate: "<span style='font-family: BYekan !important'>{$ row.entity.city_info.text $} </span>"},
                {field: 'address', displayName: 'Address', width: "20%", enableSorting: false},
                {
                    field: 'action',
                    displayName: 'Action',
                    width: "15%",
                    cellTemplate: '<div ng-show="user_type == ADMIN || user_access_edit_reseller" class="actions" ><a style="margin:5px !important;" href="#/add-reseller/{$ row.entity.id $}" class="btn btn-circle btn-icon-only btn-default"><i class="icon-wrench"></i></a><a ng-confirm-click="grid.appScope.delete_reseller(row.entity.id)" ng-confirm-message="Are you Sure?" class="btn btn-circle btn-icon-only btn-default"><i class="icon-trash"></i></a></div>',
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
        $scope.filter = {};
        $scope.filter.city = [];
        var getPage = function () {
            var sort_field = null;
            if (paginationOptions.sort) {
                if (paginationOptions.sort.name === 'city_info.text') {
                    paginationOptions.sort.name = 'city';
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
                url: ip + 'api/v1/reseller/',
                params: {
                    page: paginationOptions.pageNumber,
                    page_size: paginationOptions.pageSize,
                    sort_field: sort_field,
                    name: $scope.filter.name,
                    tel : $scope.filter.tel,
                    fax: $scope.filter.fax,
                    city_id : ($scope.filter.city.id) ? $scope.filter.city.id : $scope.filter.city,
                    address: $scope.filter.address,
                }
            }).then(function mySucces(data) {
                $timeout(function(){
                    $scope.gridOptions.totalItems = data.data.count;
                    $scope.gridOptions.data = data.data.results;

                });
                
            }, function myError(response) {
            });
        };

         //inital gird view
        getPage();
       

        $scope.delete_reseller = function (id) {
            fetchResult.fetch_result({
                method: 'delete',
                url: ip + 'api/v1/reseller/' + id+'/'
            }).then(function (result) {
                    
                  
                    $state.reload();
                }, function (err) {
                }
            );
        };

       
        

        $scope.getReseller = function(query , name){
            $scope.req_name = name ;
            
            if(name == 'name'){
                var param = {
                name: query
            }
            }
             else if(name == 'tel'){
                var param = {
                tel: query
            }
            }
            else if(name == 'fax'){
                var param = {
                fax: query
            }
            }
            else if(name == 'city'){
                var param = {
                city: query
            }
            }
            

            return fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/reseller/',
                   params: param
            }).then(function (result) {
               
                 if(result.data.results){
                    return result.data.results
                 }
                 return [];
               
                }, function (err) {
                }
            );

        }
        $scope.getReseller();

        $scope.getCity = function(query){
             return fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/city/',
                   params: {
                    city_name : query
                   }
            }).then(function (result) {
                
                 if(result.data.results){
                    return result.data.results
                 }
                 return [];
               
                }, function (err) {
                }
            );
        }

        $scope.getCity();
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
