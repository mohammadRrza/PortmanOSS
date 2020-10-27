angular.module('portman.dashboard', ['myModule'])
        .config(function ($stateProvider) {
            $stateProvider
                    .state('dashboard', {
                        url: '/dashboard',
                        views: {
                            'content': {
                                templateUrl: 'templates/dashboard/dashboard.html',
                                controller: 'DashboardController'
                            }
                        }
                    });
        })
        .controller('DashboardController', function ($scope, fetchResult, $compile, ip, uiGridConstants) {
            //Event Block

            $scope.showDslamEventsDeleteBox = function (id) {
                $scope.dslam_id = id;
                $('.dslam_events_delete_box').show('fast');
            };

            $scope.dslam_events = '';
            $scope.dslamport_events = '';
            var dslam_events_sort_field = null;
            var dslam_events_paginationOptions = {
                pageNumber: 1,
                pageSize: 10,
                sort: null
            };
            $scope.dslamEventsGridOptions = {
                enableFiltering: true,
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
                    {field: 'id', displayName: '#', width: 30, suppressSizeToFit: true, enableSorting: false},
                    {
                        field: 'dslam_info.name', displayName: 'DSLAM', suppressSizeToFit: true, enableSorting: true, width: 120,
//                        filter: {
//                            term: '1',
//                            type: uiGridConstants.filter.SELECT,
//                            selectOptions: [{value: '1', label: 'male'}, {value: '2', label: 'female'}, {value: '3', label: 'unknown'}, {value: '4', label: 'not stated'}, {value: '5', label: 'a really long value that extends things'}]
//                        },
//                        cellFilter: 'mapGender', 
                        headerCellClass: $scope.highlightFilteredHeader
                    },
                    {field: 'type', displayName: 'Event Type', width: 160, enableSorting: true},
                    {field: 'message', displayName: 'Message', width: 280, enableSorting: true},
                    {field: 'status', displayName: 'Status', width: 120, enableSorting: true,
                        cellTemplate: '<div ng-switch on="row.entity.status" id="status_led" style="float:left;margin:10px 15px;"><span ng-switch-when="new" class="badge badge-success" title="new"> &nbsp;&nbsp;</span><span ng-switch-when="ready" class="badge badge-info" title="ready"> &nbsp;&nbsp;</span><span ng-switch-default class="badge badge-danger" title="updating">&nbsp;&nbsp;</span><label style="margin-left:2px;">{$ row.entity.status $}</label></div>'},
                    {field: 'action', displayName: 'Action', width: 160,
                        cellTemplate: '<div class="actions" style="margin:5px !important;"><button ng-click="grid.appScope.show_delete_box({$ row.entity.id $})" class="btn btn-circle btn-icon-only btn-default red" title="delete dslam" style="margin-right:2px;"><i class="icon-trash"></i></button></div>', enableSorting: false, allowCellFocus: false}


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
                            dslam_events_paginationOptions.sort = null;
                        }
                        else {
                            dslam_events_paginationOptions.sort = sortColumns[0];
                        }
                        $scope.getDslamEventsPage();
                    });

                    $scope.gridApi.core.on.filterChanged($scope, function () {
                        var grid = this.grid;
//                        console.log("grid",grid);
                        if (grid.columns[1].filters[0].term !== '') {
                            $scope.getDslamEventsPage();
                            
                        }
                        
                    });


                    //fire pagination changed function
                    $scope.gridApi.pagination.on.paginationChanged($scope, function (newPage, pageSize) {
                        dslam_events_paginationOptions.pageNumber = newPage;
                        dslam_events_paginationOptions.pageSize = pageSize;
                        $scope.getDslamEventsPage();
                    });

                }
            };

            $scope.getDslamEventsPage = function () {


                if (dslam_events_paginationOptions.sort) {
                    if (dslam_events_paginationOptions.sort.name === 'telecom_center_info') {
                        dslam_events_paginationOptions.sort.name = 'telecom_center';
                    }
                    if (dslam_events_paginationOptions.sort.name === 'dslam_type_info.text') {
                        dslam_events_paginationOptions.sort.name = 'dslam_type';
                    }

                    if (dslam_events_paginationOptions.sort.sort.direction === 'desc') {
                        dslam_events_sort_field = '-' + dslam_events_paginationOptions.sort.name;
                    }
                    else {
                        dslam_events_sort_field = dslam_events_paginationOptions.sort.name;
                    }
                }

                fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/dslam/events/',
                    params: {
                        page: dslam_events_paginationOptions.pageNumber,
                        page_size: dslam_events_paginationOptions.pageSize,
                        sort_field: dslam_events_sort_field,
                        
                    }
                }).then(function (response) {
//                    $scope.dslam_events = response.data.results;
                    $scope.dslamEventsGridOptions.totalItems = response.data.count;
                    $scope.dslamEventsGridOptions.data = response.data.results;

                }, function (err) {

                });
            };
            $scope.getDslamEventsPage();





//            $scope.keyFilterChecker = function (e)
//            {
//                var key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;
//                if (key == 13)
//                {
//                    return false;
//                }
//                var allow = false;
//                // allow Ctrl+A
//                if ((e.ctrlKey && key == 97 /* firefox */) || (e.ctrlKey && key == 65) /* opera */)
//                    return false;
//                // allow Ctrl+X (cut)
//                if ((e.ctrlKey && key == 120 /* firefox */) || (e.ctrlKey && key == 88) /* opera */)
//                    return true;
//                // allow Ctrl+C (copy)
//                if ((e.ctrlKey && key == 99 /* firefox */) || (e.ctrlKey && key == 67) /* opera */)
//                    return false;
//                // allow Ctrl+Z (undo)
//                if ((e.ctrlKey && key == 122 /* firefox */) || (e.ctrlKey && key == 90) /* opera */)
//                    return true;
//                // allow or deny Ctrl+V (paste), Shift+Ins
//                if ((e.ctrlKey && key == 118 /* firefox */) || (e.ctrlKey && key == 86) /* opera */
//                        || (e.shiftKey && key == 45))
//                    return true;
//                // F1 - F12
//                if (key <= 123 && key >= 112)
//                {
//                    return false;
//                }
//
//                // if a number was not pressed
//                if (key < 48 || key > 57)
//                {
//                    // check for other keys that have special purposes
//                    if (
//                            key == 9 /* tab */ ||
//                            key == 13 /* enter */ ||
//                            key == 16 /* shift */ ||
//                            key == 17 /* CTRL */ ||
//                            key == 18 /* alt */ ||
//                            key == 20 /* CAPSLOCK */ ||
//                            key == 27 /* esc */ ||
//                            key == 33 /* pageup */ ||
//                            key == 34 /* pagedown */ ||
//                            key == 35 /* end */ ||
//                            key == 36 /* home */ ||
//                            key == 37 /* left */ ||
//                            key == 38 /* up */ ||
//                            key == 39 /* right */ ||
//                            key == 40 /* down */ ||
//                            key == 42 /* printscr */ ||
//                            key == 45 /* insert */ ||
//                            key == 91 /* window */
//
//                            )
//                    {
//                        allow = false;
//                    }
//                    else if (
//                            key == 8 /* backspace */ ||
//                            key == 46 /* del */
//
//                            )
//                    {
//                        allow = true;
//                    }
//                    else
//                    {
//                        // for detecting special keys (listed above)
//                        // IE does not support 'charCode' and ignores them in keypress anyway
//                        if (typeof e.charCode != "undefined")
//                        {
//                            // special keys have 'keyCode' and 'which' the same (e.g. backspace)
//                            if (e.keyCode == e.which && e.which != 0)
//                            {
//                                allow = true;
//                                // . and delete share the same code, don't allow . (will be set to true later if it is the decimal point)
//                                if (e.which == 46)
//                                    allow = false;
//                            }
//                            // or keyCode != 0 and 'charCode'/'which' = 0
//                            else if (e.keyCode != 0 && e.charCode == 0 && e.which == 0)
//                            {
//                                allow = true;
//                            }
//                        }
//                    }
//                }
//                else
//                {
//                    allow = true;
//                }
//                return allow;
//            };
//
//
//            $scope.showDslamEventsDeleteBox = function (id) {
//                $scope.dslam_id = id;
//                $('.dslam_events_delete_box').show('fast');
//            };
//
//            $scope.dslam_events_options = {
//                numPerPageOpt: [3, 5, 10, 20],
//                numPerPage: 5,
//                currentPage: 1,
//                totalItems: 0,
//                searchKeywords: "",
//                sortField: "",
//            };
//            $scope.dslam_search = {};
//// $scope.loadDslamEventsPage(page, $scope.dslam_events_options.numPerPage, $scope.searchKeywords, $scope.ID, $scope.ASIACode, $scope.CertNo, $scope.CertType, $scope.PlaceF, $scope.Expire, $scope.Issue, $scope.Fuel, $scope.Cond, $scope.Check, $scope.SurveyID, $scope.ExpireF, $scope.IssueF, $scope.PlaceE);                
//            $scope.loadDslamEventsPage = function (currentPage) {
//                var params = {
//                    page: currentPage,
//                    page_size: $scope.dslam_events_options.numPerPage,
//                    sort_field: $scope.dslam_events_options.sortField,
//                };
//                if ($scope.dslam_search.dslam_name !== null)
//                    params.name = $scope.dslam_search.dslam_name;
//
//                fetchResult.fetch_result({
//                    method: 'GET',
//                    url: ip + 'api/v1/dslam/events/',
//                    params: params,
//                }).then(function (response) {
//                    $scope.dslam_events_options.totalItems = response.data.count;
////                    $scope.dslamEventsGridOptions.totalItems = response.data.count;
//                    $scope.dslamEvents = response.data.results;
//                }, function (err) {
//
//                });
//            };
//            $scope.goToDslamEventsPage = function (page) {
//                if (!page || page == '')
//                    page = 1;
//
//                $scope.dslam_events_options.totalPageCount = Math.ceil($scope.dslam_events_options.totalItems / $scope.dslam_events_options.numPerPage);
//                if (page > $scope.dslam_events_options.totalPageCount)
//                {
//                    page = $scope.dslam_events_options.totalPageCount;
//                    $scope.dslam_events_options.gotopage = $scope.dslam_events_options.totalPageCount;
//                }
//                return $scope.selectDslamEvents(page, true), $scope.dslam_events_options.currentPage = page;
//            };
//            $scope.selectDslamEvents = function (page, resetGoToPage) {
//                resetGoToPage = typeof resetGoToPage !== 'undefined' ? resetGoToPage : false;
//                if (resetGoToPage == false)
//                    $scope.dslam_events_options.gotopage = "";
//                return $scope.dslam_events_options.gotopage, $scope.dslamEvents = $scope.loadDslamEventsPage(page);
////                    return $scope.dslam_events_options.gotopage, $scope.dslamEvents = $scope.loadDslamEventsPage(page, $scope.dslam_events_options.numPerPage, $scope.searchKeywords, $scope.ID, $scope.ASIACode, $scope.CertNo, $scope.CertType, $scope.PlaceF, $scope.Expire, $scope.Issue, $scope.Fuel, $scope.Cond, $scope.Check, $scope.SurveyID, $scope.ExpireF, $scope.IssueF, $scope.PlaceE);
//            };
//            $scope.onDslamEventsFilterChange = function () {
//                return $scope.selectDslamEvents(1), $scope.dslam_events_options.currentPage = 1
//            };
//            $scope.onDslamEventsNumPerPageChange = function () {
//                return $scope.selectDslamEvents(1), $scope.dslam_events_options.currentPage = 1
//            };
//            $scope.onOrderChange = function () {
//                return $scope.selectDslamEvents(1), $scope.dslam_events_options.currentPage = 1
//            };
//            $scope.searchDslamEvents = function (event, val, oldVal, isSelect) {
//                if (isSelect == undefined)
//                    isSelect = false;
//
//                if (event)
//                {
//                    if (!$scope.keyFilterChecker(event))
//                        return;
//                }
//                if (val != undefined && isSelect == false)
//                    if (val.length < 2)
//                        return;
//                return $scope.onDslamEventsFilterChange();
//            };
//            $scope.searchDslamEvents();
//
////                $scope.order = function(rowName) {
////                    return $scope.row !== rowName ? ($scope.row =
////                            rowName, $scope.filteredFuelCarry =
////                            $filter("orderBy")($scope.FuelCarry,
////                            rowName), $scope.onOrderChange()) :
////                            void 0
////                };
//



            fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/dslamport/events/'
            }).then(function (result) {
                $scope.dslamport_events = result.data.results;
            }, function (err) {

            });
            //End Event Block

            //Map Block
            $scope.map = {center: {latitude: 45, longitude: -73}, zoom: 8};
            $scope.selected_object_id = '';
            $scope.selected_City = '';

            $scope.lat = 32;
            $scope.long = 53;

            $scope.traceRouteResult = '';
            $scope.pingTimeout = 0.2;
            $scope.pingCount = 4;

            //load province
            fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/city/?parent=all'
            }).then(function (result) {
                $scope.cities = result.data;
            }, function (err) {

            });

            $scope.getTelecomCenterLocation = function () {
                fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/telecom-center/location/'
                }).then(function (result) {
                    $scope.markers = result.data;
                    $scope.loadMap();
                }, function (err) {

                });
            };

            $scope.loadMap = function () {
                $scope.keep_markers = [];
                var mapOptions = {
                    zoom: 5,
                    center: new google.maps.LatLng($scope.lat, $scope.long),
                    mapTypeId: google.maps.MapTypeId.ROADMAP,
                    scrollwheel: false,
                    zoomControl: true,
                    zoomControlOptions: {
                        style: google.maps.ZoomControlStyle.LARGE,
                        position: google.maps.ControlPosition.RIGHT_CENTER
                    }
                };
                $scope.map = new google.maps.Map(document.getElementById('map'), mapOptions);
                var infoWindow = new google.maps.InfoWindow();
                var boundbox = new google.maps.LatLngBounds();

                angular.forEach($scope.markers, function (item) {
                    var content = '';
                    var marker = new google.maps.Marker({
                        map: $scope.map
                    });
                    $scope.keep_markers.push(marker);

                    if (item.hasOwnProperty('telecom_center')) {
                        position = new google.maps.LatLng(item.telecom_lat, item.telecom_long);
                        marker.setPosition(position);
                        boundbox.extend(new google.maps.LatLng(item.telecom_lat, item.telecom_long));
                        marker.setIcon('http://maps.google.com/mapfiles/ms/icons/green-dot.png');
                        marker.setTitle(item.telecom_center_info.id.toString());
                        content = '<div class="infoWindowContent">' +
                                '<h3>Name: ' + item.telecom_center_info.name + '</h3><hr/>' +
                                '<table class="dslamport-info-report">' +
                                '<tbody>' +
                                '<tr>' +
                                '<th>Address</th>' +
                                '<td>' + item.telecom_center_info.text + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                '<th>Action</th>' +
                                '<td><a class="btn btn-lg blue" ng-click="loadDSLAMMarker()">Show DSLAM</a></td>' +
                                '</tr>' +
                                '</tbody></table>' +
                                '</div>';
                    } else {
                        position = new google.maps.LatLng(item.dslam_lat, item.dslam_long);
                        boundbox.extend(new google.maps.LatLng(item.dslam_lat, item.dslam_long));
                        marker.setPosition(position);
                        if (item.dslam_info.status == 'updating') {
                            marker.setIcon('http://maps.google.com/mapfiles/ms/icons/yellow-dot.png');
                            marker.setAnimation(google.maps.Animation.BOUNCE);
                        }
                        else if (item.dslam_info.status == 'ready') {
                            marker.setIcon('http://maps.google.com/mapfiles/ms/icons/blue-dot.png');
                        }
                        else if (item.dslam_info.status == 'error') {
                            marker.setIcon('http://maps.google.com/mapfiles/ms/icons/red-dot.png');
                            marker.setAnimation(google.maps.Animation.BOUNCE);
                        }
                        marker.setTitle(item.dslam_info.id.toString());
                        content = '<div class="infoWindowContent">' +
                                '<h3>' + item.dslam_info.name + '</h3><hr/>' +
                                '<table class="dslamport-info-report" style="width:500px">' +
                                '<tbody>' +
                                '<tr>' +
                                '<th>ID</th>' +
                                '<td>' + item.dslam_info.id + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                '<th>Name</th>' +
                                '<td><a class="btn btn-lg blue" href="#/dslam/' + item.dslam_info.id + '/report">' + item.dslam_info.name + '</a></td>' +
                                '</tr>' +
                                '<tr>' +
                                '<th>IP</th>' +
                                '<td>' + item.dslam_info.ip + '</td>' +
                                '</tr>' +
                                '<th>Status</th>' +
                                '<td>' + item.dslam_info.status + '</td>' +
                                '</tr>' +
                                '<th>Telecom Center</th>' +
                                '<td>' + item.dslam_info.telecom_center_info.name + '</td>' +
                                '</tr>' +
                                '<th>Port Count | Up | Down</th>' +
                                '<td>' + item.dslam_info.total_ports_count + ' | ' + item.dslam_info.up_ports_count + ' | ' + item.dslam_info.down_ports_count + '</td>' +
                                '</tr>' +
                                '</tbody>' +
                                '</table>' +
                                '<hr/>' +
                                '<br/>' +
                                '<div style="clear:both">' +
                                '<a class="btn btn-lg blue pull-left" ng-click="getPingResult()">Ping</a>' +
                                '<div class="pull-left"  style="margin-left:30px">' +
                                '<div class="form-group form-md-line-input has-success col-md-3">' +
                                '<input type="number" class="form-control ng-pristine ng-valid ng-touched" id="pingCount" placeholder="Ping Count" data-ng-model="pingCount">' +
                                '<label for="pingCount">Ping Count</label>' +
                                '</div>' +
                                '<div class="form-group form-md-line-input has-success col-md-3">' +
                                '<input type="number" class="form-control ng-pristine ng-valid ng-touched" id="pingTimeout" placeholder="Timeout" data-ng-model="pingTimeout">' +
                                '<label for="pingTimeout">Ping Timeout</label>' +
                                '</div>' +
                                '</div>' +
                                '</div>' +
                                '<div style="clear:both"></div>' +
                                '<div class="portlet light bordered">' +
                                '<div class="portlet-title">' +
                                '<div class="caption">' +
                                '<i class="icon-settings font-red"></i>' +
                                '<span class="caption-subject font-red sbold uppercase">Ping Result</span>' +
                                '</div>' +
                                '</div>' +
                                '<div class="portlet-body">' +
                                '<div class="table-scrollable">' +
                                '<table class="table table-hover table-light">' +
                                '<thead>' +
                                '<tr>' +
                                '<th>Host</th>' +
                                '<th>Sent</th>' +
                                '<th>Received</th>' +
                                '<th>Packet Loss</th>' +
                                '<th>Jitter</th>' +
                                '<th>Max Ping</th>' +
                                '<th>Min Ping</th>' +
                                '<th>Avg Ping</th>' +
                                '</tr>' +
                                '</thead>' +
                                '<tbody>' +
                                '<tr>' +
                                '<td> {$ pingResult.host $} </td>' +
                                '<td> {$ pingResult.sent $} </td>' +
                                '<td> {$ pingResult.received $} </td>' +
                                '<td> {$ pingResult.packet_loss $} </td>' +
                                '<td> {$ pingResult.jitter $} </td>' +
                                '<td> {$ pingResult.maxping $} </td>' +
                                '<td> {$ pingResult.minping $} </td>' +
                                '<td> {$ pingResult.avgping $} </td>' +
                                '</tr>' +
                                '</tbody>' +
                                '</table>' +
                                '</div>' +
                                '</div>' +
                                '</div>' +
                                '<br/>' +
                                '<hr/>' +
                                '<br/>' +
                                '<div style="clear:both">' +
                                '<a class="btn btn-lg blue " ng-click="getTraceRouteResult()">Trace Route</a>' +
                                '</div>' +
                                '<div style="clear:both"></div>' +
                                '<br/>' +
                                '<div class="portlet light bordered">' +
                                '<div class="portlet-title">' +
                                '<div class="caption">' +
                                '<i class="icon-settings font-red"></i>' +
                                '<span class="caption-subject font-red sbold uppercase">Trace Route Result</span>' +
                                '</div>' +
                                '</div>' +
                                '<div class="portlet-body">' +
                                '<div class="table-scrollable">' +
                                '<div id="trResult' + item.dslam_info.id + '">{$ $scope.traceRouteResult $}</div>' +
                                '</div>' +
                                '</div>' +
                                '</div>' +
                                '</div>';
                    }

                    var compiledContent = $compile(content)($scope);
                    google.maps.event.addListener(marker, 'click', (function (marker, content) {
                        return function () {
                            infoWindow.setContent(content);
                            infoWindow.open($scope.map, marker);
                            $scope.selected_object_id = marker.getTitle();
                        };
                    })(marker, compiledContent[0]));
                });

                $scope.openInfoWindow = function (e, selectedMarker) {
                    e.preventDefault();
                    google.maps.event.trigger(selectedMarker, 'click');
                };
                if ($scope.keep_markers.length > 0) {
                    $scope.map.setCenter(boundbox.getCenter());
                    $scope.map.fitBounds(boundbox);
                    $scope.map.setZoom($scope.map.getZoom() - 1);
                } else {
                    $scope.selected_object_id = '';
                    $scope.getTelecomCenterLocation();
                }
            };

            $scope.loadDSLAMMarker = function () {
                if (fetchResult.checkNullOrEmptyOrUndefined($scope.selected_City)) {
                    $scope.selected_object_id = '';
                }
                else if (fetchResult.checkNullOrEmptyOrUndefined($scope.selected_object_id)) {
                    $scope.selected_City = '';
                }
                //load province
                fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/dslam/location/?city_id=' + $scope.selected_City + '&telecom-center=' + $scope.selected_object_id
                }).then(function (result) {
                    $scope.markers = result.data;
                    $scope.selectedTelecomCenter = '';
                    $scope.loadMap();
                }, function (err) {

                });
            };

            $scope.getPingResult = function () {
                var post_data = {
                    icmp_type: 'ping',
                    dslam_id: $scope.selected_object_id,
                    params: {
                        'count': $scope.pingCount,
                        'timeout': $scope.pingTimeout
                    }
                };
                fetchResult.fetch_result({
                    method: 'POST',
                    url: ip + 'api/v1/dslam/icmp/command/',
                    data: post_data
                }).then(function (result) {
                    $scope.pingResult = result.data.result;
                }, function (err) {

                });
            };

            $scope.getTraceRouteResult = function () {
                var post_data = {
                    icmp_type: 'traceroute',
                    dslam_id: $scope.selected_object_id,
                    params: ''
                };
                fetchResult.fetch_result({
                    method: 'POST',
                    url: ip + 'api/v1/dslam/icmp/command/',
                    data: post_data
                }).then(function (result) {
                    $('#trResult' + $scope.selected_object_id).html('<pre>' + result.data.result + '</pre>');
                    $scope.traceRouteResult = result.data.restult;
                }, function (err) {

                });
            };
            //End Map Block
            $scope.getTelecomCenterLocation();
        });
