angular.module('portman.telecomtable', ['myModule', 'ngTouch', 'ui.grid', 'ui.grid.pagination', 'ui.grid.edit', 'ui.grid.cellNav', 'ui.grid.resizeColumns', 'ui.grid.autoResize'])
.config(function ($stateProvider) {
$stateProvider
    .state('telecom', {
        url: '/telecom',
        views: {
            'content': {
                templateUrl: 'templates/telecom/telecom-table.html',
                controller: 'TelecomTableController'
            }
        }
    });
})
.controller('TelecomTableController', ['$scope', '$rootScope' ,'fetchResult', '$http', '$state', 'uiGridConstants', 'ip', '$timeout' , function ($scope, $rootScope , fetchResult, $http, $state, uiGridConstants, ip , $timeout) {
$scope.searchText = null;
$scope.searchData = function () {
    getPage();
};
if($rootScope.user_access_admin || $rootScope.user_access_edit_telecomcenter ){
                $scope.gesture = '<div   class="btn-group text-center" style="position:absolute!important;margin-left:-40px;margin-top:5px;">'+
             '<a class="btn green " href="javascript:;" data-toggle="dropdown" aria-expanded="true">'+
             'Actions'+ ' <i class="fa fa-angle-down"></i>'+
             '</a><div class="dropdown-backdrop"></div>'+
             '<ul class="dropdown-menu" >'+
             '<li  title="Edit">'+
             '<a  href="#/add-telecom/{$ row.entity.id $}">'+
             '<i class="fa fa-pencil"></i> Edit </a>'+ '</li>'+
             '<li title="Delete">'+
             '<a ng-confirm-click="grid.appScope.delete_telecom(row.entity.id)" ng-confirm-message="Are You Sure To Delete Telecome?">'+
             '<i class="fa fa-trash"></i> Delete </a>'+'</li>'+
             '<li title="Bukht">'+'<a href="#/bukht/{$ row.entity.id $}">'+
             '<i class="icon-wrench"></i> Bukht </a>'+ '</li>'+
             '</ul></div>'
        }
else{
        $scope.gesture = '<div style="margin-top:5px;">'+'<a class="btn green" href="#/bukht/{$ row.entity.id $}">'+
             '<i class="icon-wrench"></i> Dslam </a>'+ '</li>'+
             '</div>'
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
    enableHorizontalScrollbar: 0,

    //declare columns
    columnDefs: [
       
        {field: 'name', displayName: 'Telecom Center Name', width: '10%', enableSorting: true},
        {field: 'prefix_bukht_name', displayName: 'Prefix Name', width: '10%', enableSorting: true},
        {field: 'total_ports_count', displayName: 'Total Ports', width: '10%', enableSorting: true},
        {field: 'down_ports_count', displayName: 'Down Ports', width: '10%', enableSorting: true},
        {field: 'up_ports_count', displayName: 'Up Ports', width: '10%', enableSorting: true},
        {field: 'dslams_count', displayName: 'Dslam Ports', width: '10%', enableSorting: true},
        {field: 'city_info.text', displayName: 'City', width: '20%', enableSorting: true,
         cellTemplate: "<span style='font-family: BYekan !important'>{$ row.entity.city_info.text $} </span>"},
        {
            field: 'action',
            displayName: 'Action',
            width: '20%',
            cellTemplate: $scope.gesture ,
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
$scope.getCityList = function(query){
 return fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/city/',
            params : {
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
    $scope.getCityList();

        $scope.checkCity= function(a){
            if(a==1 ){
                    $scope.city_id = $scope.searchText.city.id;
            }
            else {
                $scope.city_id = '';
            }
            
        }
$scope.searchText = {};
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
        url: ip + 'api/v1/telecom-center/',
        params: {
            page: paginationOptions.pageNumber,
            page_size: paginationOptions.pageSize,
            sort_field: sort_field,
            search_name: $scope.searchText.dslam_name , 
            search_prefix_bukht_name : $scope.searchText.pre_name , 
            search_city_id : $scope.city_id,
            
        }
    }).then(function mySucces(data) {
        $timeout(function(){
            $scope.gridOptions.totalItems = data.data.count;
        $scope.gridOptions.data = data.data.results;

        })
        
    }, function myError(response) {
    });
};

$scope.delete_telecom = function (id) {
    fetchResult.fetch_result({
        method: 'delete',
        url: ip + 'api/v1/telecom-center/' + id+'/'
    }).then(function (result) {
            
            $state.reload();
        }, function (err) {
        }
    );
};

//inital gird view
getPage();

$scope.getName = function(query){
     return fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/telecom-center/' ,
         params: {
            page: paginationOptions.pageNumber,
            page_size: paginationOptions.pageSize,
            
            search_name:  query, 
         
            
        }
    }).then(function (result) {
        if(result.data.results)
        {
            return result.data.results ;
        }
        return result.data.results ;
           
        }, function (err) {
        }
    );
    
   
}
}]);
