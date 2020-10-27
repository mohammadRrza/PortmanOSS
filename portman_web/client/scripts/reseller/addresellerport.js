angular.module('portman.addresellerport', ['myModule', 'ngTouch', 'ui.grid', 'ui.grid.pagination', 'ui.grid.edit', 'ui.grid.cellNav', 'ui.grid.resizeColumns', 'ui.grid.autoResize', 'ngRangeSlider'])
    .config(function ($stateProvider) {
        $stateProvider
            .state('add-reseller-port', {
                url: '/add-reseller-port',
                views: {
                    'content': {
                        templateUrl: 'templates/reseller/add-reseller-port.html',
                        
                        controller: 'ResellerPortController'
                    }
                }
            });
    })
    .controller('ResellerPortController', ['$scope', 'fetchResult', '$http', 'uiGridConstants', 'ip' ,'$timeout', function ($scope, fetchResult, $http, uiGridConstants, ip , $timeout) {
        fetchResult.loadFile('global/plugins/select2/css/select2.min.css');
        $scope.port_name = '';
        $scope.dslam = '';
        $scope.reseller = '';
        $scope.search_port_name = '';
        $scope.search_selectedDslam = '';
        $scope.search_selectedReseller = '';
        $scope.serach_port_number_from = '';
        $scope.serach_port_number_to = '';
        $scope.slot_numbers = '';
        $scope.selected_slot_number = '';

        fetchResult.loadFile('global/plugins/select2/js/select2.full.min.js', function () {

            $scope.getDslamList = function(query){
             return fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/dslam/',
                params : {
                    page:1,
                    page_size:10,
                    search_dslam: query
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

            $scope.getDslamList();
            $scope.getDslamList2 = function(){
                 fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/dslam/',
                params : {
                    page:1,
                    page_size:10,
                    search_dslam: $scope.dslam_model_2,
                }
            }).then(function (result) {
                $scope.dslam_list_2 = result.data.results ;
                    
                }, function (err) {
                }
            );
            }

            $scope.getResellerList = function(query){
            return fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/reseller/',
                 params : {
                    page:1,
                    page_size:10,
                    name: query,
                }
            }).then(function (result) {
                if(result.data.results)
                {
                    return result.data.results;
                }
                return[];
             
                }, function (err) {
                }
            );
        }
        $scope.getResellerList();

        });

        $scope.submit = function () {
        
                fetchResult.fetch_result({
                    method: 'post',
                    data: {
                         dslam: $scope.dslam_model.id,
                         reseller: $scope.reseller.id,
                    
                        slot_number: $scope.search_slot_number,
                        port_number: $scope.search_port_number,
                        slot_number_to: $scope.search_slot_number_to,
                        slot_number_from: $scope.search_slot_number_from,
                        port_number_from: $scope.search_port_number_from,
                        port_number_to: $scope.search_port_number_to,
                        identifier_key : $scope.id_key,
                        vlan_id: $scope.vlan_data,

                    },
                    url: ip + 'api/v1/reseller-port/'
                }).then(function (result) {

                    if (result.data.exist_item !== undefined && result.data.exist_item.length > 0) {
                        var show_reserved_item = '<hr/><div class="alert alert-danger alert-dismissable">\
                                    <button type="button" class="icon-close" style="float:right;" data-dismiss="alert" aria-hidden="true"></button>\
                                <strong>Error!</strong><br/>';
                        angular.forEach(result.data.exist_item, function (value, index) {
                            show_reserved_item += value.identifier_key + '-' + value.reseller + ' - ' + value.port_number + ' is reserved.<br/>';
                        });
                        show_reserved_item += '</div>';
                        $('#error_reserved_port').html(show_reserved_item);
                    }
                    else{
                        if(parseInt(result.status) < 400){
                              var notification = alertify.notify('Reseller port Added Successfully', 'success', 5, function () {
                            });
                           
                        }
                        else{
                           var notification = alertify.notify(result.statusText, 'error', 5, function () {
                            });
                        }


                    }
                    $scope.gridApi.pagination.seek(1);
                    paginationOptions.pageNumber = 1;
                    getPage();

                }, function (err) {
                    var notification = alertify.notify(err.responseText, 'error', 5, function () {
                    });
                });
              
           
        };




        $scope.iden_key = false;
        $scope.bukht = false;
        $scope.range = false;
        $scope.single = false;
        $scope.has_vlan = false;

        $scope.AddResellerPort = function () {
            $scope.iden_key = false;
            $scope.bukht  = false;
            $scope.range  = false;
            $scope.single = false;
            $scope.id_key = undefined;
            $scope.search_slot_number_from = undefined;
            $scope.search_slot_number_to = undefined;
            $scope.search_port_number_from = undefined;
            $scope.search_port_number_to = undefined;
            $scope.search_port_number = undefined;
            $scope.search_slot_number = undefined;
           
            if($scope.tab == '1'){
                $scope.iden_key = true;
            }
            else if($scope.tab == '2'){
                $scope.bukht  = true;
            }
            else if($scope.tab == '3'){
                $scope.range  = true;
            }
            else{
                $scope.single = true;
            }
            
        }

        $scope.dslam_loading = false;
        $scope.selectValue = function (selectedVal, type , number) {
            if (type == 'dslam') {
                $('.showAboutBox').show();
                $scope.dslam_loading = true;
                fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/dslam/' + selectedVal + '/dslamslot/'
                }).then(function (result) {
                        $scope.slot_numbers  = result.data.slot_numbers;

                    fetchResult.fetch_result({
                        method: 'GET',
                        url: ip + 'api/v1/mdfdslam/get_free_identifier/' ,
                        params:{
                            dslam_id: selectedVal
                        }
                    }).then(function (result) {
                        $scope.identifier_list = result.data;

                        $scope.dslam_loading = false;
                        $('.showAboutBox').hide();
                        if($scope.identifier_list.length > 0)
                        {
                            $scope.show_identifier = true;
                        }
                        else{
                            $scope.show_identifier = false;
                        }

                    },function () {

                    });


                    }, function (err) {
                    }
                );

                $scope.dslam = selectedVal;
            

            }
            else if (type == 'reseller' && number == 1) {
                fetchResult.fetch_result({
                        method: 'GET',
                        url: ip + 'api/v1/vlan/' ,
                        params:{
                            reseller_id: $scope.selectedReseller.id
                        }
                    }).then(function (result) {
                        $scope.vlan_list = angular.fromJson(result.data.results);
                        if(result.data.results.length>0){
                            //$scope.show_create_vlan_box = false;
                            $scope.has_vlan = true;
                        }
                        else{
                           // $scope.show_create_vlan_box = true;
                            $scope.has_vlan = false;
                        }

                    },function () {

                    });
                $scope.reseller = selectedVal;
            }
             else if (type == 'reseller' && number == 2) {
                fetchResult.fetch_result({
                        method: 'GET',
                        url: ip + 'api/v1/vlan/' ,
                        params:{
                            reseller: $scope.search_selectedReseller.id
                        }
                    }).then(function (result) {
                        $scope.vlan_list = angular.fromJson(result.data.results);

                    },function () {

                    });
                $scope.reseller = selectedVal;
            }
            else {
                $scope.port_name = $('.select-portname-data-array').select2('data')[0]['port_name'];
            }
        };
        

        $scope.search = function () {
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
            enableRowHashing: false,
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
              
                {field: 'id', displayName: 'ID', width: "10%"},
                {field: 'identifier_key', displayName: 'Identifier Key', width: "10%"},
                {field: 'reseller_info.name', displayName: 'Reseller Name', width: "20%", enableSorting: true},
                {field: 'dslam_fqdn', displayName: 'DSLAM FQDN', width: "20%"},
                {field: 'dslam_slot', displayName: 'Slot', width: "10%"},
                {field: 'dslam_port', displayName: 'Port', width: "10%"},

                {
                    field: 'action',
                    displayName: 'Action',
                    width: "25%",
                    enableRowHashing: false,
                    cellTemplate: '<div ng-show="user_type == ADMIN || user_access_edit_resellerport" class="actions" style="margin:5px !important;"><button ng-confirm-message="Are you sure ?" ng-confirm-click="grid.appScope.delete_reseller_port( row.entity )" class="btn btn-circle btn-icon-only btn-default "><i class="icon-trash"></i></button></div>',
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

                $scope.gridApi.core.on.filterChanged($scope, function () {
                    if ($scope.gridApi.pagination.getPage() > 1) {
                        alert('change');
                    }
                });

            }
        };


        var getPage = function () {
            if($scope.dslam_model_2 != undefined & $scope.dslam_model_2!= null)
            {
                if($scope.dslam_model_2.name)
                    $scope.dslam_model_2 = $scope.dslam_model_2.name;

                
            }
            if($scope.search_selectedReseller != undefined & $scope.search_selectedReseller != null)
            {
                if($scope.search_selectedReseller.name)
                    $scope.search_selectedReseller = $scope.search_selectedReseller.name;

            }
            

            var sort_field = null;
            if (paginationOptions.sort) {
                if (paginationOptions.sort.name === 'reseller_info.name') {
                    paginationOptions.sort.name = 'reseller';
                }
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
                url: ip + 'api/v1/reseller-port/',
                params: {
                    page: paginationOptions.pageNumber,
                    page_size: paginationOptions.pageSize,
                    sort_field: sort_field,
                    
                    search_reseller_name: $scope.search_selectedReseller  ,
                    search_dslam_name: $scope.dslam_model_2 
                }
            }).then(function mySucces(data) {
                $scope.gridOptions.data = [];
                $timeout(function(){
                $scope.gridOptions.totalItems = data.data.count;
               
                Array.prototype.push.apply($scope.gridOptions.data, data.data.results);
               
                });
                
             
            }, function myError(response) {
            });
        };

        $scope.delete_reseller_port_id = '';
        // $scope.show_delete_box = function (id) {
        //     $scope.delete_reseller_port_id = id.id;
        //     $scope.row_entity_data = id;
        //     $('.delete_box').show('slow');
        // };

        $scope.delete_reseller_port = function (id) {
            fetchResult.fetch_result({
                method: 'delete',
                url: ip + 'api/v1/reseller-port/' + id.id + '/'
            }).then(function (result) {
               
                   
                         var index = $scope.gridOptions.data.indexOf(id);
                     $scope.gridOptions.data.splice(index, 1);
                    getPage();
                }, function (err) {
                }
            );
        };
        getPage();
    }]);
