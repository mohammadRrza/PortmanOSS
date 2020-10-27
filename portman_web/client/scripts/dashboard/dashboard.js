angular.module('portman.dashboard', ['myModule'])
        .config(function ($stateProvider) {
            $stateProvider
                    .state('dashboard', {
                        url: '/dashboard',
                        views: {
                            'content': {
                                templateUrl: 'templates/dashboard/dashboard.html',
                                 controller: 'DashboardController',
                            }
                        }
                    });
        })
        .filter('mapDslamStatus', function () {
            var dslamStatusHash = {
                1: 'read',
                2: 'unread',
                3: 'resolve'
            };

            return function (input) {
                if (!input) {
                    return '';
                } else {
                    return dslamStatusHash[input];
                }
            };
        })
        .controller('DashboardController', function ($scope, $rootScope, $location, fetchResult, $compile, $q, ip, uiGridConstants , $timeout , $window) {

            if($rootScope.user_access_admin )
                    {
                        $location.path("/dashboard");
                    }
                    
                    else {
                        $location.path("/quick-search");
                    }

            $scope.showDslamEventsDeleteBox = function (id) {
                $scope.dslam_id = id;
                $('.dslam_events_delete_box').show('fast');
            };
            $scope.dslam_events = '';
            $scope.dslamport_events = '';

            var dslam_events_paginationOptions = {
                pageNumber: 1,
                pageSize: 10,
                sort: null,
                dslam_events_sort_field: null,
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
                    {
                        field: 'id',
                        displayName: '#',
                        width: 30,
                        suppressSizeToFit: true,
                        enableSorting: false,
                        enableFiltering: false,
                    },
                    {
                        field: 'dslam_info.name',
                        displayName: 'DSLAM',
                        searchName: 'search_dslam_name',
                        suppressSizeToFit: true,
                        enableSorting: true,
                        width: 120,

                    },
                    {
                        field: 'type',
                        displayName: 'Event Type',
                        searchName: 'search_event_type',
                        width: 160,
                        enableSorting: true,
                    },
                    {
                        field: 'message',
                        displayName: 'Message',
                        width: 280,
                        enableSorting: true,
                        enableFiltering: false,
                    },
                    {
                        field: 'status',
                        displayName: 'Status',
                        searchName: 'search_status',
                        width: 60,
                        enableSorting: true,
                        cellTemplate: '<div ng-switch on="row.entity.status" id="status_led" style="float:left;margin:10px 15px;"><span ng-switch-when="new" class="badge badge-success" title="new"> &nbsp;&nbsp;</span><span ng-switch-when="ready" class="badge badge-info" title="ready"> &nbsp;&nbsp;</span><span ng-switch-default class="badge badge-danger" title="updating">&nbsp;&nbsp;</span><label style="margin-left:2px;">{$ row.entity.status $}</label></div>',
                        filter: {
                            term: '',
                            type: uiGridConstants.filter.SELECT,
                            selectOptions: [
                                {value: '', label: 'All'},
                                {value: 'read', label: 'Read'},
                                {value: 'unread', label: 'Unread'},
                                {value: 'resolve', label: 'Resolve'},
                            ]
                        },
                        cellFilter: '',
                        headerCellClass: $scope.highlightFilteredHeader
                    },
                    {
                        field: 'action',
                        displayName: 'Action',
                        width: 60,
                        cellTemplate: '<div class="actions" style="margin:5px !important;"><button ng-click="grid.appScope.show_delete_box({$ row.entity.id $})" class="btn btn-circle btn-icon-only btn-default red" title="delete dslam" style="margin-right:2px;"><i class="icon-trash"></i></button></div>',
                        enableSorting: false,
                        enableFiltering: false,
                        allowCellFocus: false,
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
                            dslam_events_paginationOptions.sort = null;
                        }
                        else {
                            dslam_events_paginationOptions.sort = sortColumns[0];
                        }
                        $scope.getDslamEventsPage();
                    });
                    $scope.gridApi.core.on.filterChanged($scope, function () {
                        var grid = this.grid;

                        angular.forEach(grid.columns, function (object, index) {
                            if (object.enableFiltering == true && object.filters[0].term !== '')
                            {
                            }
                        });
                        $scope.getDslamEventsPage();

                    });
                    $scope.gridApi.pagination.on.paginationChanged($scope, function (newPage, pageSize) {
                        dslam_events_paginationOptions.pageNumber = newPage;
                        dslam_events_paginationOptions.pageSize = pageSize;
                        $scope.getDslamEventsPage();
                    });
                }
            };
            $scope.dslamEvents = {
                pageNumber: 1,
                pageSize: 10,
            };
            $scope.getDslamEventsPage = function () {

                fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/dslam/events/',
                    params: {
                        page: $scope.dslamEvents.pageNumber,
                        page_size: $scope.dslamEvents.pageSize,
                        sort_field: '-created_at',
                    }
                }).then(function (response) {
                    $scope.dslamEvents.totalItems = response.data.count;
                    $scope.dslamEvents.results = response.data.results;
                }, function (err) {

                });
            };
            $scope.getDslamEventsPage();

            $scope.dslamPortEvents = {
                pageNumber: 1,
                pageSize: 10,
            };
            $scope.getDslamPortEventsPage = function () {
                fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/dslamport/events/',
                    params: {
                        page: $scope.dslamPortEvents.pageNumber,
                        page_size: $scope.dslamPortEvents.pageSize,
                        sort_field: '-created_at',
                    }
                }).then(function (response) {
                    $scope.dslamPortEvents.totalItems = response.data.count;
                    $scope.dslamPortEvents.results = response.data.results;
                }, function (err) {

                });
            };
            $scope.getDslamPortEventsPage();

            $scope.map = {center: {latitude: 45, longitude: -73}, zoom: 8};
            $scope.selected_object_id = '';
            $scope.selected_City = '';
            $scope.dictICMPResult = {};

            $scope.lat = 32;
            $scope.long = 53;

            $scope.traceRouteResult = '';
            $scope.pingTimeout = 0.2;
            $scope.pingCount = 4;
            $('.loader').hide();


            //load province
            $scope.loadProvince = function(query){
            return fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/city/?parent=all',
                params : {
                    city_name : query
                }
            }).then(function (result) {
                if(result.data.results){
                    return result.data.results
                }
                return [];
               
            }, function (err) {

            });
        }

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
                                '</tbody></table>' +
                                '<div class="text-center"><a class="btn btn-lg blue" ng-click="loadDSLAMMarker()">Show DSLAM</a></div>' +
                                '<div class="loader" style="display:none">Loading...</div>' +
                                '' +
                                '';
                    } else {
                        var icmpResult = $scope.dictICMPResult[item.dslam];
                        var tracerouteResult = $scope.dictICMPResult[item.dslam].trace_route;
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
                        content = ''+
                                '<div class="infoWindowContent">' +
                                '<h3>' + item.dslam_info.name + '</h3><hr/>' +
                                '   <table class="dslamport-info-report" style="width:500px">' +
                                '   <tbody>' +
                                '   <tr>' +
                                '       <th class="text-center">ID</th>' +
                                '       <th class="text-center">Name</th>' +
                                '       <th class="text-center">IP</th>' +
                                '   </tr>' +
                                '   <tr>' +
                                '       <td class="text-center">' + item.dslam_info.id + '</td>' +
                                '       <td class="text-center"><a class="btn btn-lg blue" href="#/dslam/' + item.dslam_info.id + '/report">' + item.dslam_info.name + '</a></td>' +
                                '       <td class="text-center">' + item.dslam_info.ip + '</td>' +
                                '   </tr>' +
                                '   <tr>' +
                                '       <th class="text-center">Status</th>' +
                                '       <th class="text-center">Telecom Center</th>' +
                                '       <th class="text-center">Port Count | Up | Down</th>' +
                                '   </tr>' +
                                '   </tr>' +
                                '       <td class="text-center">' + item.dslam_info.status + '</td>' +
                                '       <td class="text-center">' + item.dslam_info.telecom_center_info.name + '</td>' +
                                '       <td class="text-center">' + item.dslam_info.total_ports_count + ' | ' + item.dslam_info.up_ports_count + ' | ' + item.dslam_info.down_ports_count + '</td>' +
                                '   </tr>' +
                                '   </tbody>' +
                                '   </table>' +
                                '<br/>' +
                                '<div style="clear:both"></div>' +
                                
                                '           <div class="table-scrollable">' +
                                '               <table class="table table-hover table-light">' +
                                '                   <thead>' +
                                '                       <tr>' +
                                '                           <th>Sent</th>' +
                                '                           <th>Received</th>' +
                                '                           <th>Packet Loss</th>' +
                                '                           <th>Jitter</th>' +
                                '                           <th>Max Ping</th>' +
                                '                           <th>Min Ping</th>' +
                                '                           <th>Avg Ping</th>' +
                                '                       </tr>' +
                                '                   </thead>' +
                                '                   <tbody>' +
                                '                       <tr>' +
                                '                           <td> ' + icmpResult.sent + '</td>' +
                                '                           <td> ' + icmpResult.received + '</td>' +
                                '                           <td> ' + icmpResult.packet_loss + ' </td>' +
                                '                           <td> ' + icmpResult.jitter + '</td>' +
                                '                           <td> ' + icmpResult.maxping + '</td>' +
                                '                           <td> ' + icmpResult.minping + '</td>' +
                                '                           <td> ' + icmpResult.avgping + '</td>' +
                                '                       </tr>' +
                                '                   </tbody>' +
                                '               </table>' +
                                '           </div>' +
                                "      </div>" +
                                
                                "<div class='panel-group' id='accordion' role='tablist' aria-multiselectable='true'>" +
                                "  <div class='panel panel-default'>" +
                                "    <div class='panel-heading' role='tab' id='headingOne'>" +
                                "      <h4 class='panel-title'>" +
                                "        <a role='button' data-toggle='#collapse' data-parent='#accordion' href='collapseOne' aria-expanded='true' aria-controls='collapseOne'>" +
                                "          Last Ping Result" +
                                "        </a>" +
                                "      </h4>" +
                                "    </div>" +
                                "    <div id='collapseOne' class='panel-collapse collapse' role='tabpanel' aria-labelledby='headingOne'>" +
                                "      <div class='panel-body'>" +
                                '           <div class="table-scrollable">' +
                                '               <table class="table table-hover table-light">' +
                                '                   <thead>' +
                                '                       <tr>' +
                                '                           <th>Sent</th>' +
                                '                           <th>Received</th>' +
                                '                           <th>Packet Loss</th>' +
                                '                           <th>Jitter</th>' +
                                '                           <th>Max Ping</th>' +
                                '                           <th>Min Ping</th>' +
                                '                           <th>Avg Ping</th>' +
                                '                       </tr>' +
                                '                   </thead>' +
                                '                   <tbody>' +
                                '                       <tr>' +
                                '                           <td> ' + icmpResult.sent + '</td>' +
                                '                           <td> ' + icmpResult.received + '</td>' +
                                '                           <td> ' + icmpResult.packet_loss + ' </td>' +
                                '                           <td> ' + icmpResult.jitter + '</td>' +
                                '                           <td> ' + icmpResult.maxping + '</td>' +
                                '                           <td> ' + icmpResult.minping + '</td>' +
                                '                           <td> ' + icmpResult.avgping + '</td>' +
                                '                       </tr>' +
                                '                   </tbody>' +
                                '               </table>' +
                                '           </div>' +
                                "      </div>" +
                                "    </div>" +
                                "  </div>" +
                                "  <div class='panel panel-default'>" +
                                "    <div class='panel-heading' role='tab' id='headingTwo'>" +
                                "      <h4 class='panel-title'>" +
                                "        <a class='collapsed' role='button' data-toggle='collapse' data-parent='#accordion' href='#collapseTwo' aria-expanded='false' aria-controls='collapseTwo'>" +
                                "          Last Trace Route Result" +
                                "        </a>" +
                                "      </h4>" +
                                "    </div>" +
                                "    <div id='collapseTwo' class='panel-collapse collapse' role='tabpanel' aria-labelledby='headingTwo'>" +
                                "      <div class='panel-bodyss'>" +
                                '           <div class="table-scrollable">' +
                                '               <div id="trResult' + item.dslam_info.id + '"><pre>' + tracerouteResult + '</pre></div>' +
                                '           </div>' +
                                "      </div>" +
                                "    </div>" +
                                "  </div>" +
                                "</div>" +
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
                $('.loader').show();
                var requests = [];

                if (fetchResult.checkNullOrEmptyOrUndefined($scope.selected_City)) {
                    $scope.selected_object_id = '';
                }
                else if (fetchResult.checkNullOrEmptyOrUndefined($scope.selected_object_id)) {
                    $scope.selected_City = '';
                }
                //load province
                fetchResult.fetch_result({
                    method: 'GET',
                    url: ip + 'api/v1/dslam/location/?city_id=' + $scope.selected_City.id + '&telecom-center=' + $scope.selected_object_id
                }).then(function (result) {
                    $scope.markers = result.data;
                    $scope.selectedTelecomCenter = '';

                    angular.forEach($scope.markers, function (item) {
                        var deferred = $q.defer();
                        requests.push(deferred);
                        fetchResult.fetch_result({
                            method: 'GET',
                            url: ip + 'api/v1/dslam/' + item.dslam + '/dslam_current_icmp_result/'
                        }).then(function (res) {
                            result = JSON.parse(res.data.result)[0].fields;
                            $scope.dictICMPResult[result.dslam] = result;
                        }, function (err) {

                        });
                    });

                    $q.all(requests).then(function () {
                        setTimeout(function () {
                            $scope.loadMap();
                            $('.loader').hide();
                        }, 1000);
                    });

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

            $scope.draw_tehran_colors_on_map = function(){
                var center_lat = 35.707427;
                var center_long =  51.384085;
                var north_east_lat = 35.784304; 
                var north_east_long =  51.518001;
                var north_west_lat = 35.764429;
                var north_west_long = 51.237920;
                var south_east_lat = 35.628806;
                var south_east_long =  51.467373;
                var south_west_lat = 35.658004;
                var south_west_long = 51.242087;
                var google_objects = [];
                  var triangleCoords_north = [
                        {lat: 35.707427, lng:  51.384085},
                        {lat: 35.784304, lng: 51.518001},
                        {lat: 35.764429, lng: 51.237920}
                        //{lat: 25.774, lng: -80.190}
                        ];
                  var triangleCoords_east = [
                      {lat: 35.707427, lng:  51.384085},
                      {lat: 35.784304, lng:  51.518001},
                      {lat: 35.628806, lng:  51.467373},

                  ];
                  var triangleCoords_west = [
                      {lat:35.707427, lng:  51.384085},
                      {lat: 35.764429, lng:  51.237920},
                      {lat: 35.658004, lng:  51.242087},

                  ];
                   var triangleCoords_south = [
                      {lat:35.707427, lng:  51.384085},
                      {lat:35.628806 , lng:51.467373 },
                      {lat:35.658004 , lng: 51.242087 },

                  ];

                var network_area = new google.maps.Polygon({
                    path: triangleCoords_north,
                    strokeColor: 'red',//#' + red,
                    strokeOpacity: 0.5,
                    strokeWeight: 2,
                    fillColor: 'red',//'#' + blue,
                    fillOpacity: 0.2
                });
                 var network_area2 = new google.maps.Polygon({
                    path: triangleCoords_east,
                    strokeColor: 'blue',//#' + red,
                    strokeOpacity: 0.5,
                    strokeWeight: 2,
                    fillColor: 'blue',//'#' + blue,
                    fillOpacity: 0.2
                });
                 var network_area3 = new google.maps.Polygon({
                    path: triangleCoords_west,
                    strokeColor: 'pink',//#' + red,
                    strokeOpacity: 0.5,
                    strokeWeight: 2,
                    fillColor: 'pink',//'#' + blue,
                    fillOpacity: 0.2
                });
                 var network_area4 = new google.maps.Polygon({
                    path: triangleCoords_south,
                    strokeColor: 'yellow',//#' + red,
                    strokeOpacity: 0.5,
                    strokeWeight: 2,
                    fillColor: 'yellow',//'#' + blue,
                    fillOpacity: 0.2
                });
                $timeout(function(){
                    if($window.sessionStorage.user_type == 'ADMIN'){
                     network_area.setMap($scope.map);
                     network_area2.setMap($scope.map);
                     network_area3.setMap($scope.map);
                     network_area4.setMap($scope.map);}
                },4000);
               



            }
            $scope.draw_tehran_colors_on_map();

        });
