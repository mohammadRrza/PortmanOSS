angular.module('portman.lineprofile', ['myModule','ui.grid', 'ui.grid.pagination', 'ui.grid.edit', 'ui.grid.cellNav', 'ui.grid.resizeColumns', 'ui.grid.autoResize'  ])
.config(function ($stateProvider) {
	$stateProvider
	.state('lineprofile', {
		url: '/lineprofile',
		views: {
			'content': {
				templateUrl: 'templates/lineProfile/line-profile.html',
              
				controller: 'lineProfileController'
			}
		}
	});
})
.controller('lineProfileController', function ($scope, fetchResult ,$http, ip , $timeout , $uibModal){

	paginationOptions= {};
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
        enableRowHashing: false,

            //declare columns
            columnDefs: [
            

            {field: 'name', displayName: 'Name', width: "11%", enableSorting: true},
            {field: 'template_type', displayName: 'Template type', width: "11%", enableSorting: true},
            {field: 'channel_mode', displayName: 'Chanel mode', width: "11%", enableSorting: true},
            {field: 'ports_count', displayName: 'Ports count', width: "11%", enableSorting: true},
            {field: 'max_ds_interleaved', displayName: 'Max ds interleaved', width: "6%", enableSorting: true},
            {field: 'max_us_interleaved', displayName: 'Max us interleaved', width: "6%", enableSorting: true},
            {field: 'ds_snr_margin', displayName: 'Ds snr margin', width: "6%", enableSorting: true},
            {field: 'us_snr_margin', displayName: 'Us snr margin', width: "6%", enableSorting: true},
            {field: 'min_ds_transmit_rate', displayName: 'Min ds transmit rate', width: "6%", enableSorting: true},
            {field: 'max_ds_transmit_rate', displayName: 'Max ds transmit rate', width: "6%", enableSorting: true},
            {field: 'min_us_transmit_rate', displayName: 'Min us transmit rate', width: "6%", enableSorting: true},
            {field: 'max_us_transmit_rate', displayName: 'Max us transmit rate', width: "6%", enableSorting: true},
            {field: 'Action', displayName: 'Action', width: "8%", 
            enableSorting: false ,  enableRowHashing: false,
            cellTemplate : '<div><a class="btn btn-circle btn-icon-only btn-default" style="margin:5px;" ng-confirm-click="grid.appScope.deleteLineProfile(row.entity.id)" ng-confirm-message="Are You Sure To Delete Lineprofile?"><i class="icon-trash"></i></a><a ng-click="grid.appScope.openModalBox(row.entity)"  class="btn btn-circle btn-icon-only btn-default " ><i class="icon-info"  data-toggle="modal" data-target="#mdf_id" ></i></a></div>'
            
        }

            ],

            //declare api
            onRegisterApi: function (gridApi) {
            	$scope.gridApi = gridApi;
            	paginationOptions.pageNumber = 1;

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
                    $scope.getPage();
                });


                //fire pagination changed function
                gridApi.pagination.on.paginationChanged($scope, function (newPage, pageSize) {
                	paginationOptions.pageNumber = newPage;
                	paginationOptions.pageSize = pageSize;
                	$scope.getPage();
                });

                $scope.gridApi.core.on.filterChanged($scope, function () {
                	if ($scope.gridApi.pagination.getPage() > 1) {
                		alert('change');
                	}
                });

            }
        };
        $scope.search = {};
        $scope.getPage = function () {
            sort_field = null;
            if (paginationOptions.sort) {
              
                       if (paginationOptions.sort.sort.direction === 'desc') {
                    sort_field = '-' + paginationOptions.sort.name;
                }
                else {
                    sort_field = paginationOptions.sort.name;
                }
            }


        	fetchResult.fetch_result({
        		method: "GET",
        		url: ip + 'api/v1/lineprofile/',
        		params :{
                    sort_field: sort_field,
        			page: paginationOptions.pageNumber ,
        			page_size : paginationOptions.pageSize,
        			profile_name : $scope.search.name
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
          $scope.getLineProfile = function (query) {

        	return fetchResult.fetch_result({
        		method: "GET",
        		url: ip + 'api/v1/lineprofile/',
        		params :{
        			page_size : 10,
        			profile_name : query
        		}
        	}).then(function mySucces(data) {
        		if(data.data.results)
        		{
        			return data.data.results ;
        		}
        		return [];
        	

        	}, function myError(response) {
        	});
        };

        $scope.getPage();
        $scope.new_line_profile = {};
        // $scope.createLineProfile = function(){

        // 	fetchResult.fetch_result({
        // 		method: "POST",
        // 		url: ip + 'api/v1/lineprofile/',
        // 		data: {
        // 			"template_type": $scope.new_line_profile.template_type ,
        // 			"ds_max_rate": $scope.new_line_profile.ds_max_rate,
        // 			"name": $scope.new_line_profile.name,
        // 			"us_max_rate": $scope.new_line_profile.us_max_rate
        // 		}


        // 	}).then(function mySucces(data) {
        		
        // 		if(parseInt (data.status) <400){
        // 			$scope.getPage();
        // 		var notification = alertify.notify('Done', 'success', 5, function () {
        //         });}
        //         else{
        //         	var notification = alertify.notify(data.statusText, 'error', 5, function () {
        //         });
        //         }


        // 	}, function myError(response) {
        // 	});
        // }
        $scope.searchName = function(query){
               return  $http({
                method: "GET",
                url: ip + 'api/v1/dslam/',
                params: {
                    page_size: 10,
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
        $scope.openModalBox = function(data){
            console.log(data);
            $scope.modal_box_data = data.extra_settings_info ;
        var modalInstance;
        modalInstance = $uibModal.open({
            templateUrl: "templates/lineProfile/line-profile-modal.html",
            size: 'lg',
            animation: !1,
            controller: ["$scope", "$uibModalInstance", "module", "flag", "title", "message", "okValue", "cancelValue",
                function ($scope, $uibModalInstance, module, flag, title, message, okValue, cancelValue) {
                    $scope.flag = flag;
                    $scope.module = module;
                    $scope.title = title;
                    $scope.message = message;
                    $scope.data = {
                    };
                   // $scope.searchParams = searchParams;
                    $scope.okValue = okValue;
                    $scope.cancelValue = cancelValue;
                    $scope.ok = function (data) {
                        $uibModalInstance.close(data);
                    };
                    $scope.cancel = function (url) {
                        $uibModalInstance.dismiss("cancel");
                    };
                }
            ],
            scope: $scope,
            resolve: {
                flag: function () {
                    return "info";
                },
                module: function () {
                    return data;
                },
                title: function () {
                    return "Lineprofile Info";
                },
                message: function () {
                    return '';
                },
                okValue: function () {
                    return "";
                },
                cancelValue: function () {
                    return "";
                }
            }
        }), modalInstance.result.then(function (data) {
        }, function () {
        });
        }


        $scope.searchName();

        $scope.setLineProfileToPort = function(){
         

fetchResult.fetch_result({
        		method: "POST",
        		url: ip + 'api/v1/lineprofile/assign_to_port/',
        		data: {
        			"dslam_id": $scope.new_line_profile.dslam.id ,
        			"slot_number": $scope.new_line_profile.slot_number,
        			"port_number": $scope.new_line_profile.port_number,
        			"new_lineprofile": $scope.new_line_profile.line_profile.name,
                    'us-max-rate' : $scope.new_line_profile.line_profile.us_max_rate ,
                    'ds-max-rate' : $scope.new_line_profile.line_profile.ds_max_rate
        		}


        	}).then(function mySucces(data) {
        	
        		if(parseInt (data.status) <400){
        		var notification = alertify.notify('Done', 'success', 5, function () {
                });}
                else{
                	var notification = alertify.notify(data.statusText, 'error', 5, function () {
                });
                }

        		

        	}, function myError(response) {
        	});
        }

        $scope.deleteLineProfile = function(id){
            fetchResult.fetch_result({
                method: "DELETE",
                url: ip + 'api/v1/lineprofile/' + id + '/',
             
            }).then(function mySucces(data) {
                $scope.getPage();
            
                if(parseInt (data.status) <400){
                var notification = alertify.notify('Done', 'success', 5, function () {
                });}
                else{
                    var notification = alertify.notify(data.statusText, 'error', 5, function () {
                });
                }

              
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
        charCode !== 39 && charCode !== 09)
        keyEvent.preventDefault();
        }

    });