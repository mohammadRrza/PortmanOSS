angular.module('portman.dslamporttable', ['myModule', 'ngTouch', 'ui.grid', 'ui.grid.pagination', 'ui.grid.edit', 'ui.grid.cellNav', 'ui.grid.resizeColumns', 'ui.grid.autoResize', 'ngRangeSlider'])

.config(function ($stateProvider, $urlRouterProvider) {
    $stateProvider
    .state('dslamport', {
        url: '/dslamport/:dslam_id?',
        views: {
            'content': {
                templateUrl: 'templates/dslamport/dslam-port-table.html',

                controller: 'DslamPortTableController'
            }
        },
    });
})
.controller('DslamPortTableController', ['$scope', '$rootScope' ,  'fetchResult', '$http', 'uiGridConstants', '$stateParams', 'ip', '$timeout',
    function ($scope, $rootScope, fetchResult, $http, uiGridConstants, $stateParams, ip , $timeout) {
        $scope.up_snr_range = {from: 0, to: 1000};
        $scope.up_snr_max_range = 1000;
        $scope.up_attainable_rate_range = {from: 0, to: 100000000};
        $scope.up_attainable_rate_max_range = 100000000;
        $scope.up_tx_rate_range = {from: 0, to: 100000000};
        $scope.up_tx_rate_max_range = 100000000;
        $scope.up_attenuation_range = {from: 0, to: 1000};
        $scope.up_attenuation_max_range = 1000;

        $scope.down_snr_range = {from: 0, to: 1000};
        $scope.down_snr_max_range = 1000;
        $scope.down_attainable_rate_range = {from: 0, to: 100000000};
        $scope.down_attainable_rate_max_range = 100000000;
        $scope.down_tx_rate_range = {from: 0, to: 100000000};
        $scope.down_tx_rate_max_range = 100000000;
        $scope.down_attenuation_range = {from: 0, to: 1000};
        $scope.down_attenuation_max_range = 1000;

        $scope.selected_telecom = '';
        $scope.selected_line_profile = '';
        $scope.selected_city = '';
        $scope.dslam_id = '';
        $scope.dslam_name = '';
        $scope.port_index = '';
        $scope.port_name = '';
      //  $scope.oper_status = 'SYNC';
      $scope.admin_status = '';
      $scope.min_snr_range = '';
      $scope.max_snr_range = '';





      $scope.getTelecomList = function(query){
         return fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/telecom-center/',
            params: {
              search_name : query
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
  $scope.getTelecomList();

  $scope.getLineProfileList = function(query){
    return fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/lineprofile/',
        params: {
            dslam_id : $scope.dslam_id,
            profile_name : query
        }
    }).then(function (result) {
       if (result.data.results)
       {
        return result.data.results;
    }
    return [];


}, function () {

});
}
$scope.getLineProfileList();


$scope.selected_pro = [];
$scope.getCityList = function(query){
   return fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/city/?parent=' + $scope.selected_pro.id,
    params : {
        city_name : query
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
}

$scope.getCityList();

$scope.getProveList = function(query){
 return fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/city/?parent=all',
    params : {
        city_name : query
    }

}).then(function (result) {

    if(result.data)
    {
        return result.data.results ;
    }
    return [];

}, function (err) {
}
);
}
$scope.getProveList();
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

if($rootScope.user_access_admin || $rootScope.user_access_view_dslam ){
    $scope.gesture = '<a  href="#/dslam/{$ row.entity.dslam $}/report"> {$ COL_FIELD $} </a>'
}
else{
   $scope.gesture = '<a> {$ COL_FIELD $} </a>'
}

$scope.gridOptions = {
    paginationPageSizes: [10, 25, 50, 75],
    paginationPageSize: 10,
    enableCellSelection: true,
    allowCellFocus: true,
    useExternalPagination: true,
    useExternalSorting: true,
    rowHeight: 45,
    enableHiding: false,
    enableColumnResizing: true,
    enableColResize: true,
    multiSelect: false,
    enableColumnMenus: false,
    enableHorizontalScrollbar: 1,


            //declare columns
            columnDefs: [
            {
                field: 'dslam_info.name',
                displayName: 'DSLAM',
                width: '12%',
                enableSorting: true,
                enableCellSelection: true,
                allowCellFocus: true,
                cellTemplate: $scope.gesture
            },
            {
                field: 'hostname',
                displayName: 'Host Name',
                width: '12%',
                enableSorting: true,
                enableCellSelection: true,
                allowCellFocus: true,

            },

            {field: 'port_number', displayName: 'Port',
            width: '5%', enableSorting: true,
            enableCellSelection: true,
            allowCellFocus: true,
        },
        {field: 'slot_number', displayName: 'Slot',
        width: '5%', enableSorting: true,
        enableCellSelection: true,
        allowCellFocus: true,
    }

    ,
    {
        field: 'port_name',
        displayName: 'Port Name',
        width: '10%',
        enableSorting: true,
        enableCellSelection: true,
        allowCellFocus: true,
        cellTemplate: '<a href="#/dslamport/{$ row.entity.dslam $}/{$ row.entity.id $}/status-report"> {$ COL_FIELD $} </a>'
    },
    {field: 'admin_oper_status', displayName: 'Admin/Oper Status', width: '16%', enableSorting: false,
    enableCellSelection: true,
    allowCellFocus: true,
    cellTemplate:'<span id="id_click">{$ row.entity.admin_status + " / " +row.entity.oper_status $}</span>'},
    {field: 'dslam_info.uptime', displayName: 'Up Time', width: '10%', enableSorting: false,
    enableCellSelection: true,
    allowCellFocus: true,},
    {field: 'line_profile', displayName: 'Line Profile', width: '10%', enableSorting: true,
    enableCellSelection: true,
    allowCellFocus: true,},
    {field: 'updated_at', displayName: 'Updated At', width: '10%', enableSorting: true ,
    enableCellSelection: true,
    allowCellFocus: true,},
    {
        field: 'action',
        displayName: 'Action',
        width: '10%',
        enableCellSelection: true,
        allowCellFocus: true,
        cellTemplate: '<div class="actions" style="margin:5px !important;"><button class="btn btn-circle btn-icon-only btn-default "  ng-click="grid.appScope.showInfo(row.entity)"><i class="icon-info"></i></button></div>'
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

            if ($scope.dslam_name != '') {
                $scope.dslam_id = '';
            } else {
                if (fetchResult.checkNullOrEmptyOrUndefined($stateParams.dslam_id)) {
                    $scope.dslam_id = $stateParams.dslam_id;
                }
            }

            $scope.this_params =  {
                    page: paginationOptions.pageNumber,
                    page_size: paginationOptions.pageSize,
                    sort_field: sort_field,
                    search_type: $scope.search_type,
                    search_dslam_id: $scope.dslam_id,
                    search_dslam_name: $scope.dslam_name,
                    search_dslam_ip: $scope.dslam_ip,
                    search_telecom: $scope.selected_telecom ? $scope.selected_telecom.id : $scope.selected_telecom,
                    search_port_number: $scope.port,
                    search_slot_number: $scope.slot,
                    search_port_name: $scope.port_name,
                    search_admin_status: $scope.admin_status,
                    search_oper_status: $scope.oper_status,
                    search_city: $scope.selected_city.id,
                    search_line_profile: $scope.selected_line_profile,
                    search_up_snr_range: $scope.up_snr_range,
                    search_down_snr_range: $scope.down_snr_range,
                    search_up_attenuation_range: $scope.up_attenuation_range,
                    search_down_attenuation_range: $scope.down_attenuation_range,
                    search_down_attainable_rate_range: $scope.down_attainable_rate_range,
                    search_up_attainable_rate_range: $scope.up_attainable_rate_range,
                    search_down_tx_rate_range: $scope.down_tx_rate_range,
                    search_up_tx_rate_range: $scope.up_tx_rate_range
                }
                console.log($scope.this_params);
            $http({
                method: "GET",
                url: ip + 'api/v1/dslam-port/',
                params: $scope.this_params
            }).then(function mySucces(data) {
                //console.log(data);
                $timeout(function(){
                    $scope.gridOptions.totalItems = data.data.count;
                    $scope.gridOptions.data = data.data.results;

                });
              //   $timeout(function() {
              //   document.getElementById('id_click').click();
              // }, 1000);

          }, function myError(response) {
          });
        }

        $scope.showInfo = function (row) {

            $scope.admin_status = row.admin_status;
            $scope.updated_at = row.updated_at;
            $scope.downstream_attainable_rate = row.downstream_attainable_rate;
            $scope.downstream_attenuation = row.downstream_attenuation;
            $scope.downstream_snr = row.downstream_snr;
            $scope.downstream_tx_rate = row.downstream_tx_rate;
            $scope.dslam_info = row.dslam_info.name;
            $scope.line_profile = row.line_profile; //_info.name;
            $scope.oper_status = row.oper_status;
            $scope.port_index = row.port_index;
            $scope.port_name = row.port_name;
            $scope.upstream_attainable_rate = row.upstream_attainable_rate;
            $scope.upstream_attenuation = row.upstream_attenuation;
            $scope.upstream_snr = row.upstream_snr;
            $scope.upstream_tx_rate = row.upstream_tx_rate;

            $('#showAboutBox').show('slow');
        };

        //initial grid table
        getPage();
        $scope.create_vlan_command = false;
        $scope.profile_adsl_delete = false;
        $scope.show_slot_number = false;
        $scope.profile_adsl_set = false;


        $scope.getParams = function () {
            var commandType = $scope.selected_command_type.command;
            if (commandType === 'lcman show' ||
                commandType === 'profile adsl show') {
                $scope.params = {
                    "type": "dslam"
                }
            }
            else if (commandType === 'lcman show slot' ||
                commandType === 'lcman enable slot' ||
                commandType === 'lcman disable slot' ||
                commandType === 'lcman reset slot') {
                if ($scope.command_params.slot_number === '') {
                    return false;
                }
                $scope.params = {
                    "type": "dslam",
                    "slot": $scope.command_params.slot_number
                };
            }
            else if (commandType === 'profile adsl set') {
                if ($scope.command_params.profile === '' ||
                    $scope.command_params.us_max_rate === '' ||
                    $scope.command_params.ds_max_rate === '') {
                    return false;
            }
            $scope.params = {
                "type": "dslam",
                "profile": $scope.command_params.profile,
                "us-max-rate": $scope.command_params.us_max_rate,
                "ds-max-rate": $scope.command_params.ds_max_rate
            };
        }
        else if (commandType === 'profile adsl delete') {
            if ($scope.command_params.profile === '') {
                return false;
            }
            $scope.params = {
                "type": "dslam",
                "profile": $scope.command_params.profile
            }
        }
        else if (commandType === 'change lineprofile port') {

            if($scope.change_one_slot){
                $scope.params = {
                    "isqueue" :false,
                    "type": "dslam",
                    "lineprofile": $scope.search.lineProfile,
                    "card_ports" : [{'card':$scope.search.slot_number,'port':$scope.search.port_number},]
                }
            }
            else{
                $scope.params = {
                    "isqueue" :false,
                    "type": "dslam",
                    "lineprofile": $scope.search.lineProfile,
                    "card_ports" : $scope.card_port_param

                }
            }

        }
        else if (commandType === 'vlan show')
        {
            $scope.params = {
                "type": "dslam",
            }
        }
        else if(commandType === 'create vlan'){
            $scope.params = {
                "type": "dslam",
                "vlan_name" : $scope.command_params.vlan_name,
                "vlan_id" : $scope.command_params.vlan_id
            }
        }
        return true;
    };

    $scope.searchDslamName = function(query){
        return  $http({
            method: "GET",
            url: ip + 'api/v1/dslam/',
            params: {
                page: paginationOptions.pageNumber,
                page_size: paginationOptions.pageSize,
                sort_field: sort_field,

                search_dslam: query,

            }
        }).then(function mySucces(data) {
            if(data.data.results){
                return data.data.results;
            }
            return [];

        });
    }
    $scope.searchIp = function(query){
        return  $http({
            method: "GET",
            url: ip + 'api/v1/dslam/',
            params: {
                page: paginationOptions.pageNumber,
                page_size: paginationOptions.pageSize,
                sort_field: sort_field,

                search_ip: query,

            }
        }).then(function mySucces(data) {
            if(data.data.results){
                return data.data.results;
            }
            return [];

        });
    }
    $scope.searchPortName = function(query){
        return  $http({
            method: "GET",
            url: ip + 'api/v1/dslam-port/',
            params: {
                page: paginationOptions.pageNumber,
                page_size: paginationOptions.pageSize,
                sort_field: sort_field,

                search_port_name: query,

            }
        }).then(function mySucces(data) {
            if(data.data.results){
                return data.data.results;
            }
            return [];

        });
    }
    fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam/dslam-type/'
}).then(function (result) {
    $scope.vendor_list = result.data;
}, function (err) {
}
);

    $scope.ctrlDown = false;

    $scope.chekKeyUp = function(keyEvent){
        var charCode= keyEvent.which;
        console.log(charCode);
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
        console.log(charCode);
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
