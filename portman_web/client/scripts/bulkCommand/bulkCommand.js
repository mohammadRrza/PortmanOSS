/**
* Created by Safari on 11/22/2016.
*/
angular.module('portman.bulkcommand', ['myModule', 'ngTouch' ])

.config(function ($stateProvider, $urlRouterProvider) {
$stateProvider
.state('bulkcommand', {
    url: '/bulkcommand',
    views: {
        'content': {
            templateUrl: 'templates/bilkCommand/bulk-command.html',
            
            controller: 'BulkCommandController'
        }
    },
});
})
.controller('BulkCommandController', ['$scope', 'fetchResult', '$http', '$stateParams' ,'ip', '$timeout',
function ($scope, fetchResult, $http,  $stateParams, ip , $timeout) {

    $scope.commandType = [];
    $scope.select = {};
    $scope.vpi_data = 0;
$scope.vci_data = 35;
$scope.count_data = 1;
    $scope.AddCommand = function () {
        $scope.wrong = true;
        if($scope.new_command.text == 'profile adsl delete' ){
            if($scope.profile_name_param != undefined && $scope.profile_name_param != '')
            {
                $scope.wrong = false;
                var param ={profile :  $scope.profile_name_param }; 
                $scope.profile_name_param = '';
                $scope.show_profile_input = false;
            }
            else
            {
             $scope.wrong = true ;
             var notification = alertify.notify('please compelete fields', 'error', 5, function () {
             });
         }

     }
     else if($scope.new_command.text == 'change lineprofile port' ){
        if(($scope.new_line_profile_param.name != undefined && $scope.new_line_profile_param.name != '' ) || 
             $scope.new_line_profile_param != undefined )
        {
         $scope.wrong = false;
         var param = {new_lineprofile : $scope.new_line_profile_param.name ? $scope.new_line_profile_param.name : $scope.new_line_profile_param }; 
         $scope.new_line_profile_param = '';
         $scope.show_new_line_profile_input = false;
     }
     else
     {
        $scope.wrong = true ;
        var notification = alertify.notify('please compelete fields', 'error', 5, function () {
        });
    }
    
}

else if($scope.new_command.text == 'create vlan' ){
    if($scope.vlan_name_param != undefined && $scope.vlan_name_param != ''
        && $scope.vlan_id_param != undefined && $scope.vlan_id_param != '')
    {
     $scope.wrong = false;
     var param = {
      "vlan_name" : $scope.vlan_name_param,
      "vlan_id"  : $scope.vlan_id_param
  } ; 
  $scope.vlan_id_param = '';
  $scope.vlan_name_param = '';
  $scope.show_create_vlan_inputs = false;
}
else
{
$scope.wrong = true ;
var notification = alertify.notify('please compelete fields', 'error', 5, function () {
});
}

}
else if($scope.new_command.text == 'vlan show' ){

$scope.wrong = false;
var param = {

   "vlan_id"  : $scope.vlan_id_param
} ; 
$scope.vlan_id_param = '';
$scope.show_vlan_show_command = false;


}
else if($scope.new_command.text == 'acl maccount set' ){
if($scope.vpi_data != null && $scope.vpi_data != undefined && $scope.count_data != null && $scope.count_data != undefined && $scope.vci_data != null && $scope.vci_data != undefined){
$scope.wrong = false;
var param = {
    vpi : $scope.vpi_data,
    vci : $scope.vci_data,
    count : $scope.count_data
  
} ; 
$scope.vpi_data = 0;
$scope.vci_data = 35;
$scope.count_data = 1;
$scope.show_acl_macaccount = false;
}
else
{
$scope.wrong = true ;
var notification = alertify.notify('please compelete fields', 'error', 5, function () {
});
}


}
else if($scope.new_command.text == 'port pvc set' ){

$scope.wrong = false;
var param = {
    mux : "llc",
    priority : 0,
    profile: "DEFVAL",
    vci : 35,
    vlan_id : 1 ,
    vpi : 0  
} ; 



}
else if($scope.new_command.text == 'show performance' ){
if( $scope.performance_command_opt != undefined && $scope.performance_command_opt != ''){
    $scope.wrong = false;
    var param = {
        time_elapsed : $scope.performance_command_opt
    } ; 
}
else{
  $scope.wrong = true ;
  var notification = alertify.notify('please compelete fields', 'error', 5, function () {
  });
}

}
else if($scope.new_command.text == 'profile adsl set' ){
if($scope.profile_name_param != undefined && $scope.profile_name_param != ''
    && $scope.us_max_rate_param != undefined && $scope.us_max_rate_param!= ''
    && $scope.ds_max_rate_param != undefined && $scope.ds_max_rate_param != ''
    )
{
    $scope.wrong = false;
    var param = {
        "profile": $scope.profile_name_param,
        "us-max-rate":  $scope.us_max_rate_param,
        "ds-max-rate":  $scope.ds_max_rate_param
    } ; 
    $scope.profile_name_param = '';
    $scope.us_max_rate_param = '';
    $scope.ds_max_rate_param = '';
    $scope.show_profile_adsl_set_input = false;
    
}
else
{
    $scope.wrong = true ;
    var notification = alertify.notify('please compelete fields', 'error', 5, function () {
    });
}

}
else if($scope.new_command != undefined && $scope.new_command != ''){
$scope.commandType.push({command_id:$scope.new_command.id,
    command_name : $scope.new_command.name,
    params: {}
});
$scope.show_add_new_command = false;
}
else{
var notification = alertify.notify('please compelete fields', 'error', 5, function () {
});
}
if(!$scope.wrong){
$scope.show_add_new_command = false;
$scope.commandType.push({command_id:$scope.new_command.id,
    command_name : $scope.new_command.name,
    params: param
});
}

$scope.new_command = '';
}
$scope.deleteCommand = function(i){
$scope.commandType.splice(i , 1);
}
$scope.optionsRadios = {};

$scope.getProveList = function(query){
return fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/city/'
}).then(function (result) {
    if(result.data.results){
        return result.data.results
    }
    return [] ;
    
}, function (err) {
}
);
}
$scope.getProveList();

fetchResult.fetch_result({
method: 'GET',
url: ip + 'api/v1/telecom-center/'
}).then(function (result) {
$scope.telecom_centers = result.data.results;

}, function (err) {
}
);


fetchResult.fetch_result({
method: 'GET',
url: ip + 'api/v1/dslam/dslam-type/'
}).then(function (result) {
$scope.vendor_list = result.data;
}, function (err) {
}
);

$scope.GetDslamList = function () {
$scope.select.vendor_id = $scope.select.vendor.id;
}
$scope.searchData = function () {
paginationOptions.pageNumber = 1;
$scope.gridApi.pagination.seek(1);
$scope.percent = 50 ;
getPage();
};
$scope.GetCityID = function () {
$scope.select.city_id =  $scope.select.city.id;
}
$scope.GetTeleID = function () {
$scope.select.tele_id =  $scope.select.tele.id;
}
$scope.optionsRadios = {};
$scope.optionsRadios.line = "all";
$scope.change_one_slot = false;
$scope.change_mulotiple_slot = false;
$scope.change_by_line_profile = false;
$scope.ChangeRadioButton = function(){
$scope.select.line_profile ='';
$scope.select.port_number ='';
$scope.select.slot_number = '';
$scope.select.slot_number_from ='';
$scope.select.slot_number_to ='';
$scope.select.port_number_from ='';
$scope.select.port_number_to ='';
if($scope.optionsRadios.line == 'one'){
    $scope.change_one_slot = true;
    $scope.change_multiple_slot = false;
    $scope.change_by_line_profile = false;
}
else if($scope.optionsRadios.line == 'two'){
    $scope.change_one_slot = false;
    $scope.change_multiple_slot = true;
    $scope.change_by_line_profile = false;
}
else if($scope.optionsRadios.line == 'all'){
    $scope.change_one_slot = false;
    $scope.change_multiple_slot = false;
    $scope.change_by_line_profile = false;
}
else{
    $scope.change_one_slot = false;
    $scope.change_multiple_slot = false;
    $scope.change_by_line_profile = true;

}
}
$scope.new_ip = [];
$scope.AddNewIp = function(){
if($scope.select.ip != undefined && $scope.select.ip != null && $scope.select.ip != ''){
    $scope.new_ip.push($scope.select.ip);
    $scope.select.ip= '';
    
}


}
$scope.DeleteNewIp = function(data , index){
$scope.new_ip.splice(index,1);


}

$scope.run_command_loader = false;
$scope.select.line_profile= {};
$scope.RunCommand = function () {

$scope.run_command_loader = true;
$scope.percent = 75;
$scope.command_lists = [];
if($scope.select.ip != undefined && $scope.select.ip != null && $scope.select.ip != '')
{
    if($scope.new_ip.indexOf($scope.select.ip ) == -1){
     $scope.new_ip.push($scope.select.ip);
 } 

}

fetchResult.fetch_result({
method: 'POST',
url: ip + 'api/v1/dslam/bulk-command/',
data:{
    title: $scope.commandType.title ,
    
    commands: $scope.commandType ,
    conditions:{
        telecom_center_id : $scope.select.tele_id,
        city_id : $scope.select.city_id,
        dslam_type_id : $scope.select.vendor_id,
        ip : $scope.new_ip,
        dslam_name :$scope.dslam,
        slot_port_conditions:
        {
            slot_number: $scope.select.slot_number,
            port_number: $scope.select.port_number,
            slot_number_to: $scope.select.slot_number_to,
            slot_number_from: $scope.select.slot_number_from,
            port_number_from: $scope.select.port_number_from,
            port_number_to: $scope.select.port_number_to,
            line_profile: $scope.select.line_profile.name ? $scope.select.line_profile.name : $scope.select.line_profile

        }
    }
}
}).then(function (result) {
$scope.run_command_loader = false;
$scope.commandType.title = '';
$scope.command_lists = [];
$scope.commandType.command = '';
$scope.select.tele= '';
$scope.select.city = '';
$scope.select.vendor = '';

$scope.new_ip = [];
$scope.percent = 100 ;
$timeout(function(){
    $scope.show_wizard_2 = false;
    $scope.show_wizard_3 = false;
    $scope.show_wizard_1 = true ;
    $scope.percent = 25 ;
},2000);


while($scope.commandType.length>0){
 $scope.commandType.pop();
}

// var notification = alertify.notify('Success', 'success', 5, function () {
// });

if(result.status < 400 ){
            var notification = alertify.notify('Success', 'success', 5, function () {
     });
        }
     else {
        var notification = alertify.notify(result.statusText, 'error', 5, function () {
     });
     }

}, function (err) {
$scope.run_command_loader = false;
}
);
}
$scope.GetLineProfileData = function(query){

return fetchResult.fetch_result({
method: 'GET',
url: ip + 'api/v1/lineprofile/?page=1',
params :{
    profile_name: query 
}

}).then(function (result) {
if(result.data.results){
    return result.data.results ;
}
return [];

}, function () {

});
}
$scope.GetLineProfileData();


$scope.lineProfileId = function () {

if($scope.select.line_profile !== undefined || $scope.select.line_profile != '')
    $scope.select.line_profile_id = $scope.select.line_profile.id;
else
    $scope.select.line_profile_id = '';

}

$scope.getCommandList = function(){
fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/command/'
}).then(function (result) {
    $scope.commands = result.data;
    $scope.command_list = $scope.commands ;
}, function (err) {
}
);
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
enableRowSelection: false,
enableHiding: false,
enableColumnResizing: true,
enableColResize: true,
multiSelect: false,
enableColumnMenus: false,
enableHorizontalScrollbar: 2,

            //declare columns
            columnDefs: [



            

            {
                field: 'name',
                displayName: 'DSLAM Name',
                width: "20%",
                enableSorting: true,
                cellTemplate: '<span><a href="#/dslam/{$ row.entity.id $}/report">{$ COL_FIELD $}</a> <br> {$ row.entity.ip $}</span>'
            },

            {
                field: 'telecom_center',
                displayName: 'Telecom Center',
                width: "15%",
                enableSorting: true,
                cellTemplate: "<span style='font-family:BYekan !important;'>{$ row.entity.telecom_center_info.city_info.text $} <br> {$ row.entity.telecom_center_info.name $} </span>"
            },

            {
                field: 'dslam_type_info.text',
                displayName: 'Type',
                width: "15%",
                enableSorting: true
            },
            {
                field: 'uptime',
                displayName: 'Up Time',
                width: "15%",
                enableSorting: false,

            },


            {
                field: 'total_up_down',
                displayName: 'Total/Up/Down',
                width: "15%",
                enableSorting: false,
                cellTemplate: '<span>{$ row.entity.total_ports_count $} / {$ row.entity.up_ports_count $} / {$ row.entity.down_ports_count $}</span>'
            },
            {
                field: 'status',
                displayName: 'Status',
                width: "10%",
                enableSorting: true,
                cellTemplate: '<div ng-switch on="row.entity.status" id="status_led" style="margin:10px 15px;">' +
                '<a ng-switch-when="new" href="javascript:;" class=" yellow" title="new"><i class="fa fa-ellipsis-h font-yellow"></i></a>' +
                '<a ng-switch-when="ready" href="javascript:;" class="green-turquoise" title="ready"><i class="fa fa-check font-green-turquoise"></i></a>' +
                '<a ng-switch-default href="javascript:;" class=" green" title="updating"><i class="fa fa-spinner fa-spin font-green"></i></a>' +

                '</div>'
            },
            {
                field: 'active',
                displayName: 'Active',
                width: "10%",
                enableSorting: true,
                cellTemplate: '<div ng-switch on="row.entity.active" id="status_led" style="margin:10px 15px;">' +
                '<a ng-switch-when="true" href="javascript:;" title="true" ><i class="fa fa-check font-green"></i></a>' +
                '<a ng-switch-default href="javascript:;" title="false" ><i class="fa fa-remove font-red"></i></a>' +
                '</div>'
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
        $scope.gridOptions2 = {
            paginationPageSizes: [10, 25, 50, 75],
            paginationPageSize: 10,
            useExternalPagination: true,
            useExternalSorting: true,
            rowHeight: 45,
            enableRowSelection: false,
            enableHiding: false,
            enableColumnResizing: true,
            enableColResize: true,
            multiSelect: false,
            enableColumnMenus: false,
            enableHorizontalScrollbar: 2,

            //declare columns
            columnDefs: [
            {
                field: 'title',
                displayName: 'Title',
                width: 160,
                enableSorting: true
            },
            
            {
                field: 'result_file',
                displayName: 'File',
                width: 250,
                enableSorting: true,
                cellTemplate: "<a href='{$ row.entity.result_file $}'> Download File </a>"
            },
            {
                field: 'dslam_success',
                displayName: 'Success',
                width: 240,
                enableSorting: true,
                cellTemplate: "<a href='{$ row.entity.success_file $}'> Download File </a>"
            },
            
            {
                field: 'dslam_error',
                displayName: 'Error',
                width: 160,
                cellTemplate: "<a href='{$ row.entity.error_file $}'> Download File </a>"
            },

            {
                field: 'created_at',
                displayName: 'Create time',
                width: 160,
                suppressSizeToFit: true,
                enableSorting: false
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
                    getPage1();
                });


                //fire pagination changed function
                gridApi.pagination.on.paginationChanged($scope, function (newPage, pageSize) {
                    paginationOptions.pageNumber = newPage;
                    paginationOptions.pageSize = pageSize;
                    getPage1();
                });

            }
        };

        
        $scope.startsWith = function(state, viewValue) {
          return state.toString().substr(0, viewValue.length).toLowerCase() == viewValue.toLowerCase();
      }


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
        if($scope.select.ip != undefined && $scope.select.ip != null && $scope.select.ip != '')
        {
            if( $scope.new_ip.indexOf($scope.select.ip) == -1){
                $scope.new_ip.push($scope.select.ip);
            }
            
        }


        $http({
            method: "GET",
            url: ip + 'api/v1/dslam/',
            params: {
                page: paginationOptions.pageNumber,
                page_size: paginationOptions.pageSize,
                sort_field: sort_field,
                search_ip_list : $scope.new_ip,
                search_dslam: $scope.dslam,
                search_active: $scope.active,
                search_status: $scope.status,
                search_telecom: $scope.select.tele_id,
                search_city: $scope.select.city_id,
                search_type : $scope.select.vendor_id
            }
        }).then(function mySucces(data) {
            $timeout(function(){
             $scope.gridOptions.totalItems = data.data.count;
             $scope.gridOptions.data = data.data.results;
         });
            
        }, function myError(response) {

        });
    };
    $scope.onFocus = function (e) {
        $timeout(function () {
          $(e.target).trigger('input');
      });
    };
    $scope.open = function() {
        $scope.opened = true;
    }
    $scope.close = function() {
        $scope.opened = false;
    }
    var getPage1 = function () {
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

        fetchResult.fetch_result({
            method: 'Get',
            url: ip + 'api/v1/dslam/bulk-command/result/',
        }).then(function (data) {

            $timeout(function(){
                $scope.gridOptions2.totalItems = data.data.count;
                $scope.gridOptions2.data = data.data.results;
            });
            
        }, function (err) {
        });
    };
    $scope.paginate = function(value) {
       var begin, end, index;
       begin = ($scope.currentPage - 1) * $scope.numPerPage;
       end = begin + $scope.numPerPage;
       return (begin ,  end);
   };

   $scope.currentPage_err = 1;
   $scope.currentPage_suc = 1;
   $scope.maxSize = 10;
   $scope.itemPerPage = 5;


   getPage();
   getPage1();
   $scope.show_wizard_1 = true;
   $scope.show_wizard_2 = false;
   $scope.show_wizard_3 = false;
   $scope.step = 1;
   $scope.percent = 25 ;
   $scope.GoToFirstWizard = function () {


    $scope.step = 1;
    $scope.percent = 25;
    $scope.show_wizard_1 = true;
    $scope.show_wizard_2 = false;
    $scope.show_wizard_3 = false;
    
    
}
$scope.GoToSecondWizard = function () {

 $scope.getCommandList();

 $scope.show_wizard_1 = false;
 $scope.show_wizard_2 = true;
 $scope.show_wizard_3 = false;
 $scope.step = 2;
 $scope.percent = 50;


};

$scope.GoToThirdWizard = function () {
$scope.commands = $scope.command_list;


$scope.no_slot_entered =true;
$scope.no_slot_range_entered = true;
$scope.no_port_entered = true;
$scope.no_port_range_entered = true;
$scope.no_lineprofile_entered = true;


if($scope.optionsRadios.line == 'one'){

    if($scope.select.port_number !== undefined && $scope.select.port_number !== '' &&
        $scope.select.slot_number !== undefined && $scope.select.slot_number !== ''){

     fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/command/' ,
        params :{
            exclude_type : 'dslam',
        }

    }).then(function (result) {
     $scope.commands = result.data;

 }, function (err) {
 }
 );
}
else{
    var notification = alertify.notify('please compelete fields', 'error', 5, function () {
             });
    return ;
}

}
else if($scope.optionsRadios.line == 'two'){
if($scope.select.slot_number_from !== undefined && $scope.select.slot_number_from !== ''
  && $scope.select.slot_number_to !== undefined && $scope.select.slot_number_to !== ''
  && $scope.select.port_number_from !== undefined && $scope.select.port_number_from !== ''
  && $scope.select.port_number_to !== undefined && $scope.select.port_number_to !== '') {
                      //  $scope.no_slot_range_entered = false;
                  fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/command/' ,
                    params :{
                        exclude_type : 'dslam',
                    }

                }).then(function (result) {
                    $scope.commands = result.data;

                }, function (err) {
                }
                );

            }
else{
    var notification = alertify.notify('please compelete fields', 'error', 5, function () {
             });
    return ;
}

        }

        else if($scope.optionsRadios.line == 'three')
        {
            if($scope.select.line_profile !== undefined && $scope.select.line_profile !== ''){

                fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/command/' ,
                    params :{
                        type : 'port',
                    } 
                }).then(function (result) {
                    $scope.commands = result.data;

                }, function (err) {
                }
                );
            }
             else{
    var notification = alertify.notify('please compelete fields', 'error', 5, function () {
             });
    return ;
}

        }
        else if($scope.optionsRadios.line == 'all'){
          fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/command/' ,
params :{
                        type : 'dslam',
                    } 
        }).then(function (result) {
            $scope.commands = result.data;
            
        }, function (err) {

        });

    }
    $timeout(function(){
        $scope.show_wizard_1 = false;
        $scope.show_wizard_2 = false;
        $scope.show_wizard_3 = true;
        $scope.step = 3;
        $scope.percent = 75;
    });


};

$scope.show_profile_input = false;
$scope.show_new_line_profile_input = false;
$scope.show_profile_adsl_set_input = false;
$scope.show_create_vlan_inputs = false;
$scope.show_add_new_command = false;
$scope.show_vlan_show_command = false;
$scope.show_performance_command = false;
$scope.show_acl_macaccount = false;

$scope.CheckParams = function(){

    $scope.show_profile_input = false;
    $scope.show_new_line_profile_input = false;
    $scope.show_profile_adsl_set_input = false;
    $scope.show_create_vlan_inputs = false;
    $scope.show_add_new_command = false;
    $scope.show_vlan_show_command = false;
    $scope.show_performance_command = false;
    $scope.show_acl_macaccount = false;

    if($scope.new_command.name == undefined || $scope.new_command == ''){
        $scope.show_profile_input = false;
        $scope.show_new_line_profile_input = false;
        $scope.show_profile_adsl_set_input = false;
        $scope.show_create_vlan_inputs = false;
        $scope.show_add_new_command = false;
        $scope.show_vlan_show_command = false;
        $scope.show_performance_command = false;
        $scope.show_acl_macaccount = false;
    }

    else if($scope.new_command.name == 'profile adsl delete')
    {
        $scope.show_profile_input = true;
    }
    else if($scope.new_command.name == 'change lineprofile port')
    {

        $scope.show_new_line_profile_input = true;
    }
    else if($scope.new_command.name == 'profile adsl set')
    {

        $scope.show_profile_adsl_set_input = true;
    }
    else if($scope.new_command.name == 'create vlan')
    {

        $scope.show_create_vlan_inputs   = true;

    }
    else if($scope.new_command.name == 'vlan show')
    {

        $scope.show_vlan_show_command   = true;

    }
    else if($scope.new_command.name == 'show performance')
    {

        $scope.show_performance_command   = true;

    }
    else if($scope.new_command.name == 'acl maccount set')
    {
        $scope.show_acl_macaccount = true;
    }
    else
    {
        $scope.show_add_new_command = true;
    }
}

$scope.searchName = function(query){
   return  $http({
    method: "GET",
    url: ip + 'api/v1/dslam/',
    params: {
        page: paginationOptions.pageNumber,
        page_size: paginationOptions.pageSize,
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
    charCode !== 39 && charCode !== 09 )
    keyEvent.preventDefault();
    }



}]);