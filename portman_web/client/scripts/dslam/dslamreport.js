angular.module('portman.dslamreport', ['myModule','ui.grid', 'ui.grid.pagination', 'ui.grid.edit', 'ui.grid.cellNav', 'ui.grid.resizeColumns', 'ui.grid.autoResize' ,'acute.select'  ])
.config(function ($stateProvider) {
  $stateProvider
  .state('dslam-report', {
    url: '/dslam/:dslam_id/report',
    views: {
      'content': {
        templateUrl: 'templates/dslam/dslam-report.html',

        controller: 'DslamReportController'
      }
    }
  });
})
.controller('DslamReportController', function ($scope, $rootScope, fetchResult, $stateParams, $location ,  ip ,$timeout ,uiGridConstants ,socket_ip  ,ngSocket , $q , $window ) {

  $scope.first_tab = {};
  $scope.first_tab.currentPage = 1 ;
  $scope.first_tab.slot_count = 17 ;
  $scope.first_tab.per_page  = 1;
  $scope.first_tab.maxSize = 15 ;

  $scope.$on('$viewContentLoaded', function(){

    $scope.dslam_id = $stateParams.dslam_id;
    $scope.chart_is_drawed = {} ;
    $scope.chart_is_drawed.chart1 = false ;
    $scope.chart_is_drawed.chart2 = false ;
    $scope.chart_is_drawed.chart3 = false ;
    $timeout(function () {
      fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/dslam/' + $scope.dslam_id + '/dslamreport/'
      }).then(function (result) {

        $scope.dslam = result.data;
        console.log($scope.dslam);
        $scope.dslam.dslam_availability = $scope.dslam.dslam_availability.toFixed(2);
        $scope.first_tab.slot_count = parseInt( $scope.dslam.slot_count );
        if($scope.dslam.down_ports > 0 && $scope.dslam.up_ports){
          $scope.chart_is_drawed.chart1 = true ;
        }
        if($scope.dslam.nosync_ports > 0 && $scope.dslam.sync_ports > 0)
        {
          $scope.chart_is_drawed.chart2 = true ;
        }

        if(angular.fromJson($scope.dslam.line_profile_usage)[0]['name'] != null)
        {
          $scope.chart_is_drawed.chart3 = true ;
        }
        if($scope.dslam.down_ports > 0 && $scope.dslam.up_ports){

          $scope.chart1 = $('#port-admin-status').highcharts({
            chart: {

              plotBackgroundColor: null,
              plotBorderWidth: null,
              plotShadow: false,
              type: 'pie',
              width : 300 ,
            },
            credits: {
              enabled: false
            },
            title: {
              text: 'Ports By Administrative Status'
            },
            tooltip: {
              pointFormat: '{series.line_profile}: <b>{point.percentage:.1f}%</b>'
            }
            ,
            plotOptions: {
              pie: {

                allowPointSelect: true,
                cursor: 'pointer',
                size : 150 ,
                dataLabels: {
                  enabled: true,
                  format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                  style: {
                    color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                  },
                  connectorColor: 'silver'
                },
                showInLegend: true
              }
            },
            series: [{
              name: 'Port Status',
              data: [{name: 'UNLOCK', y: $scope.dslam.up_ports}, {
                name: 'LOCK',
                y: $scope.dslam.down_ports
              }]
            }]
          });
        }


        if($scope.dslam.nosync_ports > 0 && $scope.dslam.sync_ports > 0)
        {

          $scope.chart2 =  $('#port-oper-status').highcharts({
            chart: {

              plotBackgroundColor: null,
              plotBorderWidth: null,
              plotShadow: false,
              type: 'pie',
              width : 300 ,
            },
            credits: {
              enabled: false
            },
            title: {
              text: 'Ports By Operational Status'
            },
            tooltip: {
              pointFormat: '{series.line_profile}: <b>{point.percentage:.1f}%</b>'
            },

            plotOptions: {
              pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                size : 150 ,
                dataLabels: {
                  enabled: true,
                  format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                  style: {
                    color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                  },
                  connectorColor: 'silver'
                },
                showInLegend: true
              }
            },
            series: [{
              name: 'Port Operational Status',
              data: [{name: 'Sync', y: $scope.dslam.sync_ports}, {
                name: 'NO-Sync',
                y: $scope.dslam.nosync_ports
              }]
            }]
          });
        }

        if(angular.fromJson($scope.dslam.line_profile_usage)[0]['name'] != null)
        {
          $scope.chart3 = $('#line-profile-usage').highcharts({
            chart: {
              plotBackgroundColor: null,
              plotBorderWidth: null,
              plotShadow: false,
              type: 'pie'
            },
            credits: {
              enabled: false
            },
            title: {
              text: 'Line Profile Usage'
            },
            tooltip: {
              pointFormat: '{series.line_profile}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
              pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                size : 200 ,
                dataLabels: {
                  enabled: true,
                  format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                  style: {
                    color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                  },
                  connectorColor: 'silver'
                },
                showInLegend: true
              }
            },

            series: [{
              name: 'Line Profiles',
              data: JSON.parse($scope.dslam.line_profile_usage)
            }]
          });
        }



      }, function (err) {
      }
    );

    fetchResult.fetch_result({
      method: 'GET',
      url: ip + 'api/v1/dslam/' + $scope.dslam_id + '/dslam_curr_temperature_report/'
    }).then(function (result) {
      var chart = {
        zoomType: 'xy'
      };
      // var subtitle = {
      //     text: 'Source: veerasystem.com'
      // };
      var title = {
        text: 'Line Cards Current Temperature'
      };
      var xAxis = {
        categories: result.data.names,
        crosshair: true,
        labels: {
          rotation: -70
        }

      };
      var credits = {
        enabled: false
      };
      var perShapeGradient = {
        x1: 0,
        y1: 0,
        x2: 0,
        y2: 1
      };
      var colors = [{
        linearGradient: perShapeGradient,
        stops: [
          [0, 'rgb(247, 111, 111)'],
          [1, 'rgb(255,255,255)']
        ]
      }];
      var yAxis = [{ // Primary yAxis
        labels: {
          format: '{value}\xB0C',
          style: {
            color: Highcharts.getOptions().colors[1]
          }
        }
      }, { // Secondary yAxis
        title: {
          text: 'Temperature',
          style: {
            color: Highcharts.getOptions().colors[0]
          }
        },
        labels: {
          format: '{value}\xB0C',
          style: {
            color: Highcharts.getOptions().colors[0]
          }
        },
        opposite: true
      }];


      var tooltip = {
        shared: true
      };
      var legend = {
        layout: 'vertical',
        align: 'left',
        x: 120,
        verticalAlign: 'top',
        y: 100,
        floating: true,
        backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
      };
      var series = [{
        showInLegend: false,
        name: 'Tempreture',
        type: 'column',
        yAxis: 1,
        data: result.data.values,
        tooltip: {
          valueSuffix: '\xB0C'
        }, cursor: 'pointer',
        point: {

          events: {
            click: function () {
              load_range_tempreture(this.category)
            }
          }
        },
        dataLabels: {
          enabled: true,
          color: '#FFFFFF',
          format: '{point.y}', // one decimal
          style: {
            fontSize: '10px',
            fontFamily: 'Verdana, sans-serif'
          }
        }

      }
    ];

    var json = {};
    json.chart = chart;
    json.title = title;
    // json.subtitle = subtitle;
    json.xAxis = xAxis;
    json.colors = colors;
    json.yAxis = yAxis;
    json.tooltip = tooltip;
    json.legend = legend;
    json.series = series;
    $('#dslamtemp').highcharts(json);

  }, function (err) {

  });


  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam/location/',
    params : {
      dslam_id : $scope.dslam_id
    }
  }).then(function (result) {
    if(result.data.length>0){
      var mapOptions = {
        zoom: 10,
        center: new google.maps.LatLng(result.data[0].dslam_lat, result.data[0].dslam_long),
        scrollwheel: false
      }
      $scope.map = new google.maps.Map(document.getElementById('dslam-map'), mapOptions);
      var marker = new google.maps.Marker({
        map: $scope.map
      });
      position = new google.maps.LatLng(result.data[0].dslam_lat, result.data[0].dslam_long);
      marker.setPosition(position);
      if (result.data[0].dslam_info.status == 'updating') {
        marker.setIcon('http://maps.google.com/mapfiles/ms/icons/yellow-dot.png');
        marker.setAnimation(google.maps.Animation.BOUNCE);
      }
      else if (result.data[0].dslam_info.status == 'ready') {
        marker.setIcon('http://maps.google.com/mapfiles/ms/icons/blue-dot.png');
      }
      else if (result.data[0].dslam_info.status == 'error') {
        marker.setIcon('http://maps.google.com/mapfiles/ms/icons/red-dot.png');
        marker.setAnimation(google.maps.Animation.BOUNCE);
      }
    }
    else{
      var mapOptions = {
        zoom: 10,
        center: new google.maps.LatLng(36.159049, 51.748768),
        scrollwheel: false
      }
      $scope.map = new google.maps.Map(document.getElementById('dslam-map'), mapOptions);
    }

  }, function (err) {
    alert('error');

  });
},3000);



});
$scope.dslam_id = $stateParams.dslam_id;
$scope.limit_row_result_commands = 5;
$scope.selected_command_type = {command:''};
$scope.dslam = [];
$scope.params = '';
$scope.slot_number = '';
$scope.port_number = '';
$scope.profile_name = '';
$scope.us_max_rate = '';
$scope.ds_max_rate = '';
$scope.pingTimeout = 0.2;
$scope.pingCount = 4;

$scope.ping_loader_show = false;
$scope.trace_loader_show = false;



//     fetchResult.fetch_result({
//         method: 'GET',
//         url: ip + 'api/v1/command/'
//     }).then(function (result) {
//     //$scope.commands = result.data;
//     $(".select-command-type-data-array").select2({
//         data: result.data
//     });
// }, function (err) {
// }
// );


fetchResult.fetch_result({
  method: 'GET',
  url: ip + 'api/v1/command/',
  params :{
    exclude_type : 'port',
    dslam_id : $scope.dslam_id
  }
}).then(function (result) {
  console.log(result);
  $scope.commands = result.data;
}, function (err) {
}
);
// $scope.getCommand = function (callback) {
//     callback($scope.commands);
// };

/*
******************************************************************
*/
$scope.card_port_param = [];
$scope.show_slot_number = false;
$scope.profile_adsl_set = false;
$scope.create_vlan_command = false;
$scope.profile_adsl_delete = false;
$scope.command_params = {};
$scope.search = {search_slot_to:'',search_slot_from:'',search_port_to:'' , search_port_from:''};
$scope.is_change_long_profile = false;
$scope.changing_line_profile_loader = false;
$scope.show_linestat_params = false;
$scope.show_loop_to_wan_vc = false;
$scope.show_uplink_pvc_show_slot = false ;
$scope.show_cart_command_param = false;

$scope.checkCommandType = function () {
  $scope.show_cart_command_param = false;
  $scope.create_vlan_command = false;
  $scope.profile_adsl_delete = false;
  $scope.show_slot_number = false;
  $scope.profile_adsl_set = false;
  $scope.show_linestat_params = false;
  $scope.vlan_show_command = false;
  $scope.show_loop_to_wan_vc = false;
  $scope.show_uplink_pvc_show_slot = false ;
  if( $scope.selected_command_type.command == 'change lineprofile port'){
    $scope.changing_line_profile_loader = true;
    $scope.getPage1();
  }
  if($scope.selected_command_type.command != 'change lineprofile port'){
    $scope.changing_line_profile_loader= false;
    $scope.is_change_long_profile = false;
  }
  if($scope.selected_command_type.command == 'lcman enable slot' ){
    $scope.show_slot_number = true;
  }
  else if( $scope.selected_command_type.command == 'show linestat slot'){
    $scope.show_linestat_params = true;
  }
  else if($scope.selected_command_type.command == 'lcman show slot'){
    $scope.show_slot_number = true;
  }
  else if($scope.selected_command_type.command == 'lcman reset slot'){
    $scope.show_slot_number = true;
  }
  else if($scope.selected_command_type.command == 'lcman disable slot'){
    $scope.show_slot_number = true;
  }
  else if($scope.selected_command_type.command == 'profile adsl set'){
    $scope.profile_adsl_set = true;
  }
  else if($scope.selected_command_type.command == 'profile adsl delete'){
    $scope.profile_adsl_delete = true;
  }
  else if($scope.selected_command_type.command == 'create vlan'){
    $scope.create_vlan_command = true;
  }
  else if($scope.selected_command_type.command == 'vlan show'){
    $scope.vlan_show_command = true;
  }
  else if($scope.selected_command_type.command == 'loop to wan vc'){
    $scope.show_loop_to_wan_vc = true;
  }
  else if($scope.selected_command_type.command == 'uplink pvc show slot'){
    $scope.show_uplink_pvc_show_slot = true ;
  }
  else if ($scope.selected_command_type.command == 'show cart')
  {
    $scope.show_cart_command_param = true;
  }
  $scope.getCommandResult();

}

$scope.lineProfileId = function () {

  if($scope.search.search_line_profile !== undefined || $scope.search.search_line_profile != '')
  $scope.search.search_line_profile_id = $scope.search.search_line_profile.text;
  else
  $scope.search.search.search_line_profile_id = '';

}
$scope.optionsRadios = {};
$scope.optionsRadios.line = "three";
$scope.change_one_slot = false;
$scope.change_mulotiple_slot = false;
$scope.change_by_line_profile = true;
$scope.ChangeRadioButton = function(){
  $scope.search.search_slot_number ='';
  $scope.search.search_port_number ='';
  $scope.search.search_slot_to = '';
  $scope.search.search_slot_from ='';
  $scope.search.search_port_from ='';
  $scope.search.search_port_to='';
  $scope.search.search_line_profile ='';
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
  else{
    $scope.change_one_slot = false;
    $scope.change_multiple_slot = false;
    $scope.change_by_line_profile = true;

  }
}
$scope.statoptions = {};
$scope.show_range_slot_stat = false;
$scope.show_single_slot_stat  = false;
$scope.statoptions.line = 'all';
$scope.Changestat = function(){
  $scope.search.stat_slot = '';
  $scope.search.stat_slot_from = '';
  $scope.search.stat_slot_to = '';
  $scope.show_range_slot_stat = false;
  $scope.show_single_slot_stat  = false;
  if($scope.statoptions.line == 'range'){
    $scope.show_range_slot_stat = true;
    $scope.show_single_slot_stat  = false;
  }
  else if($scope.statoptions.line == 'slot'){
    $scope.show_range_slot_stat = false;
    $scope.show_single_slot_stat  = true;
  }
  else
  {
    $scope.show_range_slot_stat = false;
    $scope.show_single_slot_stat  = false;
  }
}
$scope.totalServerItems = 0;
$scope.dslam_id = $stateParams.dslam_id;
var paginationOptions2 = {
  pageNumber: 1,
  pageSize: 10,
  sort: null
};
$scope.gridOptions2 = {
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

  columnDefs: [
    {
      field: 'port_name',
      displayName: 'Port Name',
      width: 200,
      cellTemplate: '<div><span><a href="#/dslamport/{$ dslam_id $}/status-report/{$row.entity.slot_number$}/{$row.entity.port_number$}">{$row.entity.port_name$}</a></span></div>',
      suppressSizeToFit: true,
      enableSorting: false
    },
    {
      field: 'slot_number',
      displayName: 'Slot Number',
      width: 200,
      enableSorting: true,

    },
    {
      field: 'port_number',
      displayName: 'Port Number',
      width: 200,
      enableSorting: true,

    },


    {
      field: 'line_profile',
      displayName: 'Line Profile',
      width: 200,
      enableSorting: true,
    },


  ],
  onRegisterApi: function (gridApi) {
    $scope.gridApi2 = gridApi;
    $scope.gridApi2.core.on.sortChanged($scope, function (grid, sortColumns) {
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
        paginationOptions2.sort = null;
      }
      else {
        paginationOptions2.sort = sortColumns[0];
      }
      $scope.getPage1();
    });
    gridApi.pagination.on.paginationChanged($scope, function (newPage, pageSize) {
      $timeout(function () {
        paginationOptions2.pageNumber = newPage;
        paginationOptions2.pageSize = pageSize;
        $scope.getPage1();});
      });
    }
  };
  $scope.gridOptions
  = {
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
        field: 'port_name',
        displayName: 'Port Name',
        width: 200,
        suppressSizeToFit: true,
        enableSorting: false
      },
      {
        field: 'slot_number',
        displayName: 'Slot Number',
        width: 200,
        enableSorting: true,

      },
      {
        field: 'port_number',
        displayName: 'Port Number',
        width: 200,
        enableSorting: true,

      },


      {
        field: 'line_profile',
        displayName: 'Line Profile',
        width: 200,
        enableSorting: true,
      },


    ],
    //declare api
    onRegisterApi: function (gridApi) {
      $scope.gridApi2 = gridApi;
      //fire sortchanged function
      $scope.gridApi2.core.on.sortChanged($scope, function (grid, sortColumns) {
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
          paginationOptions2.sort = null;
        }
        else {
          paginationOptions2.sort = sortColumns[0];
        }
        $scope.getPage1();
      });

    }
  };
  $scope.getPage1 = function () {
    $scope.changing_line_profile_loader = true;

    if (paginationOptions2.sort) {
      if (paginationOptions2.sort.sort.direction === 'desc') {
        sort_field = '-' + paginationOptions2.sort.name;
      }
      else {
        sort_field = paginationOptions2.sort.name;
      }
    }

    fetchResult.fetch_result({
      method: 'GET',
      url: ip + 'api/v1/dslam-port/',
      params : {
        page: paginationOptions2.pageNumber ,
        page_size : paginationOptions2.pageSize,
        search_dslam_id : $scope.dslam_id,
        search_slot_number: $scope.search.search_slot_number,
        search_port_number: $scope.search.search_port_number,
        search_slot_to: $scope.search.search_slot_to,
        search_slot_from: $scope.search.search_slot_from,
        search_port_from: $scope.search.search_port_from,
        search_port_to: $scope.search.search_port_to,
        search_line_profile : $scope.search.search_line_profile_id
      }
    }).then(function (result) {
      $scope.card_port_param = [];
      $scope.is_change_long_profile = true;
      $scope.changing_line_profile_loader = false;
      $scope.dslam_port_table = result.data.results;

      $timeout(function () {
        $scope.gridOptions2.totalItems = result.data.count;
        $scope.gridOptions2.data = result.data.results;
      });



    }).then(function () {

    });
  }

  ////////////////////////////////////////////////////////
  //                      Get Linr profile list
  /////////////////////////////////////////////////////////
  $scope.getLineProfileList = function(query){
    //   $scope.line_profile_list = [];
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
  $scope.getNewLineProfileList = function(query){
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

    }); }
    $scope.getNewLineProfileList();

    $scope.update_single_dslam_port = function(){

      fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/dslam/' + $scope.dslam_id + '/scan/',
        params : {
          type : 'port'
        }
      }).then(function (result) {
        if(result.status <400 ){
          var notification = alertify.notify('Dslam Updated', 'success', 5, function () {
          });
        }
        else {
          var notification = alertify.notify(result.statusText, 'error', 5, function () {
          });
        }

      }, function (err) {
        var notification = alertify.notify('error', 'error', 5, function () {
        });
      }
    );

  }
  $scope.update_single_dslam_general = function(){
    fetchResult.fetch_result({
      method: 'GET',
      url: ip + 'api/v1/dslam/' + $scope.dslam_id + '/scan/',
      params : {
        type : 'general'
      }
    }).then(function (result) {
      if(parseInt (result.status) <400 ){
        var notification = alertify.notify('Dslam Updated', 'success', 5, function () {
        });
      }
      else {
        var notification = alertify.notify(result.statusText, 'error', 5, function () {
        });
      }
    }, function (err) {
      var notification = alertify.notify('error', 'error', 5, function () {
      });
    }
  );

}

$scope.colours = [
  { name: 'black', id: 0 },
  { name: 'white', id: 1 },
  { name: 'red', id: 2 }];

  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam/' + $scope.dslam_id + '/dslam_current_icmp_result/'
  }).then(function (result) {
    res = JSON.parse(result.data.result)[0];
    $scope.icmpResult = res.fields;
    $scope.tracerouteResult = res.fields.trace_route;
  }, function (err) {

  });

  $scope.run_command = function () {
    var params_isvalid = $scope.getParams();
    if ($scope.selected_command_type.command != '' && params_isvalid) {
      $scope.changing_line_profile_loader = true ;


      fetchResult.fetch_result({
        method: 'post',
        data: {
          "dslam_id": $scope.dslam_id,
          "params": $scope.params,
          "command": $scope.selected_command_type.command
        },
        url: ip + 'api/v1/dslamport/command/'
      }).then(function (result) {
        $scope.changing_line_profile_loader = false ;

        if(result.status <400){
          var notification = alertify.notify("Done", 'success', 5, function () {

          });
        }
        else{
          var notification = alertify.notify(result.statusText, 'error', 5, function () {

          });


        }
        if( $scope.i === undefined)
        {
          $scope.i = 20;

        }
        else if($scope.i <20 ){
          $scope.i = 20;
          clearInterval($scope.resultIntervel)
        }


        $scope.resultIntervel = setInterval(function () {
          $scope.i -= 4;
          $scope.getCommandResult();
          if ($scope.i < 8) {

            // $scope.getCommandResult();
            clearInterval($scope.resultIntervel);
          }

        }, 3000);

      }, function (err) {
        var notification = alertify.notify(err, 'error', 5, function () {
        });
      });
    }
    else {
      var notification = alertify.notify('Command Type is empty', 'error', 5, function () {
      });
    }
  };


  // $scope.startsWith = function(state, viewValue) {
  //     return state.toString().substr(0, viewValue.length).toLowerCase() == viewValue.toLowerCase();
  // }

  $scope.showParams = function () {
    var commandType = $scope.selected_command_type.command;
    if (commandType === 'lcman show' ||
    commandType === 'profile adsl show') {
      $('.slot_number').addClass('hide');
      $('.us_max_rate').addClass('hide');
      $('.ds_max_rate').addClass('hide');
      $('.profile_name').addClass('hide');
    }
    else if (commandType === 'lcman show slot' ||
    commandType === 'lcman enable slot' ||
    commandType === 'lcman disable slot' ||
    commandType === 'lcman reset slot') {
      $('.slot_number').removeClass('hide');
      $('.us_max_rate').addClass('hide');
      $('.ds_max_rate').addClass('hide');
      $('.profile_name').addClass('hide');
    }
    else if (commandType === 'profile adsl set') {
      if ($scope.profile_name === '' ||
      $scope.us_max_rate === '' ||
      $scope.ds_max_rate === '') {
      }
      $('.profile_name').removeClass('hide');
      $('.us_max_rate').removeClass('hide');
      $('.ds_max_rate').removeClass('hide');
      $('.slot_number').addClass('hide');
    }
    else if (commandType === 'profile adsl delete') {
      $('.profile_name').removeClass('hide');
      $('.us_max_rate').addClass('hide');
      $('.ds_max_rate').addClass('hide');
      $('.slot_number').addClass('hide');
    }
  };

  $scope.getParams = function () {

    var commandType = $scope.selected_command_type.command;
    if (commandType === 'lcman show' ||
    commandType === 'profile adsl show' || commandType === 'show mac') {
      $scope.params = {
        "type": "dslam",
        'dslam_id' : $scope.dslam_id ,
        "is_queue" :false,

      }
    }
    else if (commandType === 'lcman show slot' ||
    commandType === 'lcman enable slot' ||
    commandType === 'lcman disable slot' ||
    commandType === 'lcman reset slot'
  ) {
    if ($scope.command_params.slot_number === '') {
      return false;
    }
    $scope.params = {
      "type": "dslam",
      'dslam_id' : $scope.dslam_id ,
      "slot": $scope.command_params.slot_number
    };
  }
  else if(commandType === 'show cart'){
    $scope.params = {
      "type": "dslam",
      'dslam_id' : $scope.dslam_id ,
      "slot": $scope.command_params.show_cart_5006
    };
  }
  else if(commandType === 'show temperature' || commandType === 'show shelf'){
    $scope.params = {
      "type": "dslam",
      'dslam_id' : $scope.dslam_id ,
    };
  }

  else if(commandType === 'show linestat slot'){
    $scope.slot_linestat = [];
    if($scope.statoptions.line == 'all'){

      for(i=1 ; i<=$scope.slot_count ;i++)
      {
        $scope.slot_linestat.push(i);
      }

    }
    else if($scope.statoptions.line == 'range'){
      for(i= parseInt($scope.search.stat_slot_from) ; i<= parseInt($scope.search.stat_slot_to) ; i++)
      {
        $scope.slot_linestat.push(i);
      }
    }
    else if($scope.statoptions.line == 'slot'){
      $scope.slot_linestat.push($scope.search.stat_slot);
    }
    $scope.params = {
      "type": "dslam",
      'dslam_id' : $scope.dslam_id ,
      "slot":  $scope.slot_linestat
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
      'dslam_id' : $scope.dslam_id ,
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
      'dslam_id' : $scope.dslam_id ,
      "profile": $scope.command_params.profile
    }
  }
  else if (commandType === 'change lineprofile port') {
    if($scope.search.lineProfile == undefined || $scope.search.lineProfile == '' || $scope.search.lineProfile == null)
    {
      var notification = alertify.notify('New Line Profile is empty', 'error', 5, function () {
      });
      return false ;
    }

    else if($scope.change_one_slot){
      $scope.params = {
        "is_queue" :false,
        "type": "dslamport",
        'dslam_id' : $scope.dslam_id ,
        "new_lineprofile": $scope.search.lineProfile,
        "port_conditions" :{
          "slot_number": parseInt($scope.search.search_slot_number),
          "port_number" :  parseInt($scope.search.search_port_number),
        }
      }
    }

    else if($scope.change_multiple_slot){
      $scope.params={
        "is_queue" :false,
        "type": "dslamport",
        'dslam_id' : $scope.dslam_id ,
        "new_lineprofile": $scope.search.lineProfile,
        "port_conditions":{
          "slot_number_from" : $scope.search.search_slot_from,
          "slot_number_to"  : $scope.search.search_slot_to,
          "port_number_from"  : $scope.search.search_port_from,
          "port_number_to" : $scope.search.search_port_to
        }
      }

    }
    else{
      $scope.params = {
        "is_queue" :false,
        "type": "dslamport",
        'dslam_id' : $scope.dslam_id ,
        "new_lineprofile": $scope.search.lineProfile,
        // "card_ports" : $scope.card_port_param,
        "port_conditions" : {
          "lineprofile" : $scope.search.search_line_profile_id
        }

      }
    }

  }
  else if (commandType === 'vlan show')
  { if($scope.command_params.vlan_id != ''){
    $scope.params = {
      "type": "dslam",
      'dslam_id' : $scope.dslam_id ,
      "vlan_id" : $scope.command_params.vlan_id
    }
  }
  else{
    return false ;
  }
}
else if(commandType === 'create vlan'){
  if($scope.command_params.vlan_name != '' && $scope.command_params.vlan_id != '')
  $scope.params = {
    "type": "dslam",
    'dslam_id' : $scope.dslam_id ,
    "vlan_name" : $scope.command_params.vlan_name,
    "vlan_id" : $scope.command_params.vlan_id
  }
  else{
    return false ;
  }
}
else if(commandType === 'loop to wan vc'){
  if ($scope.command_params.port_vpi === '' || $scope.command_params.port_vci === '' ||
  $scope.command_params.start_slot_number === '' || $scope.command_params.start_port_number === '' ||
  $scope.command_params.wan_slot_number === '' || $scope.command_params.wan_port_number === '' ||
  $scope.command_params.wan_vpi === '' || $scope.command_params.wan_vci === '' ||
  $scope.command_params.vc_number === '') {
    return false;
  }
  else {
    $scope.params = {
      "type": "dslam",
      'dslam_id' : $scope.dslam_id ,
      'port_vpi' : $scope.command_params.port_vpi,
      'port_vci' : $scope.command_params.port_vci,
      'start_slot_number' : $scope.command_params.start_slot_number,
      'start_port_number' : $scope.command_params.start_port_number,
      'wan_slot_number' : $scope.command_params.wan_slot_number,
      'wan_port_number' : $scope.command_params.wan_port_number,
      'wan_vpi' : $scope.command_params.wan_vpi,
      'wan_vci' : $scope.command_params.wan_vci,
      'vc_number' : $scope.command_params.vc_number,
    }
  }
}
else if (commandType === 'uplink pvc show slot') {
  if ($scope.command_params.slotnumberss == '') {
    return false;
  }
  $scope.params = {
    "type": "dslam",
    'dslam_id' : $scope.dslam_id ,
    "slot_number": $scope.command_params.slotnumberss
  };
}
return true;
};
$scope.vlan_show_command_result = [];
$scope.show_all_mac_command_result = [];
$scope.getCommandResult = function () {
  $scope.showParams();
  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam/command/result/?' +
    'dslam=' + $scope.dslam_id + '&' +
    'limit_row=' + $scope.limit_row_result_commands + '&' +
    'command_type=' + $scope.selected_command_type.command
  }).then(function (result) {
    $scope.result_commands = result.data;
    angular.forEach($scope.result_commands , function(value,key){

      if(value.command.text ==='vlan show' && value.value.result != 'No results was returned.'){
        angular.forEach(value.value.result , function(v,k){
          $scope.vlan_show_command_result.push({'vlan_name':v,'vlan_id':k});
        });
      }
    });
  }, function (err) {
  }
);
};
$scope.Showmodal = function(data){
  $scope.TotalItems = data.length;
  $scope.row_data = data;
  $scope.currentPage= 1;
  $scope.itemsPerPage = 50 ;
  $scope.modal_data = [];
  $scope.modal_data = data;
  console.log($scope.result_commands);

  $('#showAboutBox').show('slow');
}
$scope.checkMacData = function(data){
  $scope.mac_list = data ;
}
// function load_range_tempreture(lc_name) {
//     fetchResult.fetch_result({
//         method: 'GET',
//         url: ip + 'api/v1/dslam/' + $scope.dslam_id +
//         '/dslam_range_temperature_report/?lc_name=' + lc_name
//     }).then(function (result) {
//         var chart = {
//             zoomType: 'xy'
//         };
// // var subtitle = {
// //     text: 'Source: veerasystem.com'
// // };
// var title = {
//     text: 'Temperature ' + lc_name
// };
// var xAxis = {
//     categories: result.data.names,
//     crosshair: true,
//     minTickInterval: 140,
//     labels: {
//         rotation: -70,
//         style: {
//             fontSize: '13px',
//             fontFamily: 'tahoma,Verdana, sans-serif'
//         }
//     }

// };
// var credits = {
//     enabled: false
// };
// var yAxis = [{ // Primary yAxis
//     labels: {
//         format: '{value}\xB0C',
//         style: {
//             color: Highcharts.getOptions().colors[1]
//         }
//     },
//     title: {
//         text: 'Temperature',
//         style: {
//             color: Highcharts.getOptions().colors[1]
//         }
//     }
// }];
// var tooltip = {
//     shared: true
// };
// var legend = {
//     layout: 'vertical',
//     align: 'left',
//     x: 120,
//     verticalAlign: 'top',
//     y: 100,
//     floating: true,
//     backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
// };
// var series = [{
//     showInLegend: false,
//     name: 'Temperature',
//     type: 'spline',
//     data: result.data.values,
//     tooltip: {
//         valueSuffix: '\xB0C'
//     }
// }
// ];

// var json = {};
// json.chart = chart;
// json.title = title;
// json.subtitle = subtitle;
// json.xAxis = xAxis;
// json.yAxis = yAxis;
// json.tooltip = tooltip;
// json.legend = legend;
// json.series = series;
// $('#range_dslsm_temp').highcharts(json);
// }, function (err) {

// });
// }

$scope.dslamICMPValues = '';
//$scope.width=$('#pingresultcontent').css('width');
// show range ping dslam
fetchResult.fetch_result({
  method: 'GET',
  url: ip + 'api/v1/dslam/dslam_range_ping_report/',
  params: {
    dslam_id: $scope.dslam_id
  }
}).then(function (result) {

  $scope.dslamICMPValues = result.data;
  var chart = {
    zoomType: 'xy',
    // width:$scope.width
  };
  //    var subtitle = {
  //     text: 'Source: veerasystem.com'
  // };
  var title = {
    text: 'Ping DSLAM'
  };
  var xAxis = {
    categories: $scope.dslamICMPValues.names,
    minTickInterval: 20,
    crosshair: true,
    labels: {
      rotation: -70
    }

  };
  var perShapeGradient = {
    x1: 0,
    y1: 0,
    x2: 0,
    y2: 1
  };
  var colors = [{
    linearGradient: perShapeGradient,
    stops: [
      [0, 'rgb(247, 111, 111)'],
      [1, 'rgb(255,255,255)']
    ]
  }];
  var credits = {
    enabled: false
  }
  var yAxis = [{ // Primary yAxis
    labels: {
      format: '{value} milisecond',
      style: {
        color: Highcharts.getOptions().colors[1]
      }
    }
  }, { // Secondary yAxis
    title: {
      text: 'Ping',
      style: {
        color: Highcharts.getOptions().colors[0]
      }
    },
    labels: {
      format: '{value} milisecond',
      style: {
        color: Highcharts.getOptions().colors[0]
      }
    },
    opposite: true
  }];

  var tooltip = {
    shared: true,
    useHTML: true,
    formatter: function () {
      obj_icmp = $scope.dslamICMPValues.dslamicmp_values[this.x];
      var show_date = '<table style="width:300px" class="dslamport-info-report">' +
      '<tbody><tr>' +
      '<th>avg ping</th>' +
      '<td>' + obj_icmp.avgping + '</td>' +
      '</tr>' +
      '<tr>' +
      '<th>max ping</th>' +
      '<td>' + obj_icmp.maxping + '</td>' +
      '</tr>' +
      '<tr>' +
      '<th>min ping</th>' +
      '<td>' + obj_icmp.minping + '</td>' +
      '</tr>' +
      '<tr>' +
      '<th>jitter</th>' +
      '<td>' + obj_icmp.jitter + '</td>' +
      '</tr>' +
      '<tr>' +
      '<th>sent</th>' +
      '<td>' + obj_icmp.sent + '</td>' +
      '</tr>' +
      '<tr>' +
      '<th>received</th>' +
      '<td>' + obj_icmp.received + '</td>' +
      '</tr>' +
      '<tr>' +
      '<th>packet loss</th>' +
      '<td>' + obj_icmp.packet_loss + '</td>' +
      '</tr>' +
      '</tbody></table>';
      return show_date;

    }
  };
  var legend = {
    layout: 'vertical',
    align: 'left',
    x: 120,
    verticalAlign: 'top',
    y: 100,
    floating: true,
    backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
  };
  var credits = {
    enabled: false
  };
  var series = [{
    showInLegend: false,
    name: 'Ping',
    type: 'column',
    yAxis: 1,
    data: $scope.dslamICMPValues.values,
    tooltip: {
      valueSuffix: '\xB0C'
    }, cursor: 'pointer',
    point: {

      events: {
        click: function () {
          //nge_tempreture(this.category)
        }
      }
    },
    dataLabels: {
      enabled: true,
      color: '#FFFFFF',
      format: '{point.y}', // one decimal
      style: {
        fontSize: '10px',
        fontFamily: 'Verdana, sans-serif'
      }
    }

  }
];

var json = {};
json.chart = chart;
json.title = title;
json.credits = credits ;
// json.subtitle = subtitle;
json.xAxis = xAxis;
json.colors = colors;
json.yAxis = yAxis;
json.tooltip = tooltip;
json.legend = legend;
json.series = series;
$('#dslamavgping').highcharts(json);
}, function (err) {

});


$scope.getPingResult = function () {
  //  $('#pingLoading').show();
  $scope.ping_loader_show = true;
  var post_data = {
    icmp_type: 'ping',
    dslam_id: $scope.dslam_id,
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
    $scope.icmpResult = result.data.result;

    $scope.ping_loader_show = false ;
  }, function () {
    $scope.ping_loader_show = false ;

  });
};

$scope.getTraceRouteResult = function () {
  //$('#trLoading').show();
  $scope.trace_loader_show = true ;
  var post_data = {
    icmp_type: 'traceroute',
    dslam_id: $scope.dslam_id,
    params: ''
  };
  fetchResult.fetch_result({
    method: 'POST',
    url: ip + 'api/v1/dslam/icmp/command/',
    data: post_data
  }).then(function (result) {
    $scope.tracerouteResult = result.data.result;
    $scope.trace_loader_show = false ;
  }, function () {
    $scope.trace_loader_show = false ;
  });
};

$scope.selected = {vlan1:'' , vlan2:'' , reseller:''};
$scope.getCommandResult();
fetchResult.fetch_result({
  method: 'GET',
  url: ip + 'api/v1/vlan/'
}).then(function (result) {
  $scope.vlan_list = result.data.results;
}, function (err) {
}
);
fetchResult.fetch_result({
  method: 'GET',
  url: ip + 'api/v1/reseller/'
}).then(function (result) {

  $scope.reseller_list = result.data.results;


}, function (err) {
}
);
$scope.ChangeSelectedVlan = function () {
  $scope.selected.vlan2 = $scope.selected.vlan1 ;

}
$scope.SetVlan = function (){
  fetchResult.fetch_result({
    method: 'POST',
    url: ip + 'api/v1/vlan/',
    data : {
      dslam_id : $scope.dslam_id,
      reseller:$scope.selected.reseller.id,
      vlan_name:$scope.selected.vlan2,
      vlan_id:$scope.selected.vlan1.vlan_id,
      params :{
        type: "dslam",
        vlan_name:$scope.selected.vlan2,
        vlan_id:$scope.selected.vlan1
      }

    }
  }).then(function (result) {
    if(result.status < 400){
      $scope.selected = '';
      var notification = alertify.notify('Vlan Created', 'success', 5, function () {
      });

    }
    else{
      var notification = alertify.notify(result.statusText, 'error', 5, function () {
      });
    }

  }, function (result) {
    var notification = alertify.notify('Error', 'error', 5, function () {
    });
  }
);

}
fetchResult.fetch_result({
  method: 'GET',
  url: ip + 'api/v1/dslam/'+ $scope.dslam_id +'/getvlan/'
}).then(function (result) {
  $scope.dslam_vlan = angular.fromJson(result.data.vlans);
}, function (err) {
}
);

/******************************************************************
*
******************************************************************/
$scope.vlan_m = {};
$scope.vlan_m.currentPage = 1;
$scope.vlan_m.maxSize= 3;

$scope.dslam_port_req = {vid:'',dslam_id:''};
$scope.show_dslam_port_table= false ;
$scope.vlan_percentage = [];
fetchResult.fetch_result({
  method: 'GET',
  url: ip + 'api/v1/dslam/'+ $scope.dslam_id +'/vlan_usage_percentage/'
}).then(function (result) {
  angular.forEach(result.data.values,function (key,value) {

    $scope.vlan_percentage.push({y:key.percentage,name:key.vlan_name,id:key.id,total:key.total});
  });

  $scope.dslamVlanValues = result.data.values;

  $scope.chart4 = $('#dslam-vlan-value').highcharts({
    chart: {
      width: 350,
      height: 400,
      plotBackgroundColor: null,
      plotBorderWidth: null,
      plotShadow: false,
      type: 'pie'
    },
    credits: {
      enabled: false
    },
    title: {
      text: 'Vlan Usage'
    },
    tooltip: {
      pointFormat: '{series.line_profile}: <b>{point.percentage:.1f}%</b>'
    },
    plotOptions: {
      pie: {
        size: 110,
        allowPointSelect: true,
        cursor: 'pointer',
        dataLabels: {
          enabled: true,
          format: '<b>{point.name}</b>: {point.percentage:.1f} %',
          style: {
            color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
          },
          connectorColor: 'silver'
        },
        showInLegend: true
      }
    },

    series: [{
      name: 'Line Profiles',
      data:  $scope.vlan_percentage,
      point:{
        events:{
          click: function (event) {
            $scope.dslam_port_req.vid = this.id;
            $scope.dslam_port_req.dslam_id = $scope.dslam_id;

            fetchResult.fetch_result({
              method: 'GET',
              url: ip + 'api/v1/dslam-port/?page_size=10&page=' + $scope.vlan_m.currentPage,
              params : {
                search_vid : this.id,
                search_dslam_id : $scope.dslam_id
              }
            }).then(function (result) {

              $scope.show_dslam_port_table = true;

              $scope.dslam_port_table = result.data.results;
              $scope.vlan_m.totalItems = result.data.count;

              $timeout(function(){
                $scope.gridOptions.totalItems = result.data.count;
                $scope.gridOptions.data = result.data.results;

              });
            }).then(function () {

            });
          }
        }
      }
    }]
  });

}, function (err) {

});

// $scope.secondRequest = function(){
//     fetchResult.fetch_result({
//         method: 'GET',
//         url: ip + 'api/v1/dslam-port/?page_size=10&page=' + $scope.vlan_m.currentPage,
//         params : {
//             search_vid : $scope.dslam_port_req.vid,
//             search_dslam_id : $scope.dslam_id
//         }
//     }).then(function (result) {

//         $scope.dslam_port_table = result.data.results;
//         $scope.vlan_m.totalItems = result.data.count;

//     }).then(function () {

//     });
// }

$scope.totalItems = 10;
$scope.pagination = {
  currentPage:  1
};

$scope.setPage = function (pageNo) {
  $scope.currentPage = pageNo;
};

$scope.maxSize = 5;
$scope.bigCurrentPage = 1;

fetchResult.fetch_result({
  method: 'GET',
  url: ip + 'api/v1/dslam/'+ $scope.dslam_id + '/',

}).then(function (result) {
  $scope.slot_count = result.data.slot_count;
  $scope.slot_list  = result.data.slots ;
  $scope.port_list = result.data.ports ;
}, function (err) {
});

$scope.DrawLiveChart = function(){

  Highcharts.setOptions({
    // This is for all plots, change Date axis to local timezone
    global: {
      useUTC: false
    }
  });

  $timeout(function () {

    $scope.livechart = Highcharts.chart('liveping', {
      chart: {
        zoomType: 'x',
        height: 300,
        type: 'area',
        marginRight: 0,
        spacingLeft: 20,
        spacingRight: 0,
        reflow: true
      },
      global: {
        useUTC: false
      },
      title: {
        style: {
          color: '#27a4b0',
        },
        text: 'Live Ping',
        align: 'left'
      },

      xAxis: {
        type: 'datetime' //,

      },

      yAxis: [{
        title: {
          enabled: true,
          text: 'Click and drag to zoom in',
          color: '#b4b6ba'
        },
        plotLines: [{
          width: 1,
          value: 3
        }
      ],
      labels: {
        format: '{value} milisecond',
        style: {
          color: Highcharts.getOptions().colors[0]
        }
      },
    }, { // Secondary yAxis
      title: {
        text: 'Ping',
        style: {
          color: Highcharts.getOptions().colors[0]
        }
      },
      labels: {
        format: '{value} milisecond',
        style: {
          color: Highcharts.getOptions().colors[0]
        }
      },
      opposite: true
    }],
    tooltip: {
      shared: true,
      crosshairs: true,

      formatter: function () {

        return '<b>' + ' Time: ' + Highcharts.dateFormat('%H:%M:%S', this.x) + '</b>' + '<br>' +
        '<b>' + 'received:'  + this.points[0].point.received  + '</b><br/>' +
        '<b>' + 'jitter' + ': ' + this.points[0].point.jitter + '</b><br/>' +
        '<b>' + 'packet loss' + ': ' + this.points[0].point.packet_loss + '</b><br/>'
        +'<b>' + 'avgping' + ': ' + this.y + '</b><br/>'
        +'<b>' + 'minping' + ': ' + this.points[0].point.minping + '</b><br/>'
        +'<b>' + 'sent' + ': ' + this.points[0].point.sent + '</b><br/>'
        +'<b>' + 'maxping' + ': ' + this.points[0].point.maxping + '</b>'

        ;
      }
    },
    legend: {
      enabled: true,
      colors: ['#058DC7', '#ED561B']

    },
    exporting: {
      enabled: false
    },
    plotOptions: {
      colors: ['#ED561B', '#058DC7', '#50B432', '#DDDF00', '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4'],
      series: {
        type: 'area',
        marker: {
          enabled: false
        }

      },
      area: {
        marker: {
          radius: 2
        },
        lineWidth: 1,
        states: {
          hover: {
            lineWidth: 1
          }
        }
        ,
      }

    },
    marker: {
      radius: 2
    },
    credits: {
      enabled: false
    },
    series: [{
      name: 'AVG Ping', //$scope.names[i] + ' ' + 'tx',
      fillColor: {
        linearGradient: {
          x1: 0,
          y1: 0,
          x2: 0,
          y2: 1
        },
        stops: [

          [0, Highcharts.getOptions().colors[0]],
          [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
        ]
      },
      dataLabels: {
        format: function () {
          //return  formatBytes(this.y) ;
          return '123123123'
        }
      },
      data: (function () {

        time = new Date().getTime();

        var data = [],
        i;

        for (i = -20; i <= 0; i += 1) {
          data.push({
            x: time + i * 5000,
            y: null
          });
        }
        return data;
      }())
    },



  ],
  func: function (chart) {
    $timeout(function () {
      chart.reflow();
    }, 1000);
  }
});

}, 1000);

setTimeout(function () {
  angular.element(window).triggerHandler('resize');
}, 900);
}

$scope.show_chart = false;
$scope.socket_count = 0;
$scope.first_time = true;
$scope.changeShowState = function () {
  $scope.show_chart = !$scope.show_chart ;
  if($scope.first_time && $scope.show_chart){
    $scope.DrawLiveChart();

    $scope.first_time = false;
  }
  if($scope.show_chart){

    $timeout(function(){
      $scope.rout_location = $location.path();

      $scope.ws = ngSocket('ws://5.202.129.160:2083/ws/');
      $scope.ws.send('{"action":"ping", "dslam_id":' + $scope.dslam_id  +' }');
      $scope.$on('$routeChangeStart', function() {
        if($scope.ws)
        $scope.ws.close();
      });
      $scope.ws.onMessage(function (message) {
        if($location.path() == $scope.rout_location){

          $scope.socket_count = $scope.socket_count +1;
          var data = angular.fromJson(message.data);
          var x = (new Date().getTime());  // current time

          var y = angular.fromJson(data);
          x = new Date().getTime();

          var y2 = parseInt( y.avgping );

          if($scope.livechart){
            $scope.livechart.series[0].addPoint([x, y2], true, true);
            var count = ($scope.livechart.series[0].points.length)-1 ;
            $scope.livechart.series[0].points[count].jitter = parseInt( y.jitter );
            $scope.livechart.series[0].points[count].packet_loss = parseInt( y.packet_loss );
            $scope.livechart.series[0].points[count].minping = parseInt( y.minping );
            $scope.livechart.series[0].points[count].received = parseInt( y.received );
            $scope.livechart.series[0].points[count].sent = parseInt( y.sent );
            $scope.livechart.series[0].points[count].maxping = parseInt( y.maxping );
            if(data['PORT_ADMIN_STATUS'] == 'Lock'){
              $scope.port_status_data = 'lock'
            }
            else{
              $scope.port_status_data = 'unlock'
            }

            if(data['PORT_OPER_STATUS'] == 'SYNC'){
              $scope.oper_status_data = 'sync';

            }
            else{
              $scope.oper_status_data = 'no sync';
            }

          }

        }
        else{

          $scope.ws.close();
        }
      });
    },2000);
  }

  else{
    $scope.ws.close();
  }
}

var callbacks = [];

$scope.current_cart_number = 0;
$scope.show_cart_dslam_detail = true;
$scope.chart_show_per_slot = false;
$scope.getSlotDetailes = function(ind){
  $('#sec-per-slot-chart').value = [];
  $scope.current_cart_number = ind;
  $scope.chart_show_per_slot = false;
  $scope.temp_data_per_slot =  $scope.card_data_in_dslam[ind].temperature ;

  angular.forEach($scope.temp_data_per_slot , function(value , key)
  {
    console.log(key);
    $scope.drawGauge(key);
  })

}

$scope.cart_detailes_in_dslam_face = function(){

  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam/' + $scope.dslam_id + '/board/'

  }).then(function (result) {
    console.log(result.data);

    $scope.card_data_in_dslam =  result.data ;
    angular.forEach($scope.card_data_in_dslam , function(value,key){
      $scope.last_true_item = 10;
      $scope.first_true_item = 0;
      if(key<11){
        $scope.card_data_in_dslam[key].show = true;
      }
      else{
        $scope.card_data_in_dslam[key].show = false;
      }
    });
    //$scope.pie_chart_in_dslam_slot();

    $scope.temp_data_per_slot =  $scope.card_data_in_dslam[$scope.first_tab.currentPage-1].temperature ;
    angular.forEach($scope.temp_data_per_slot , function(value , key)
    {
      console.log(key);
      $scope.drawGauge(key);
    });

  }).then(function () {

  });
}
$rootScope.$on('$viewContentLoaded', function(event) {
  $scope.cart_detailes_in_dslam_face();
});

// $scope.callGauge = function(){
//  angular.forEach($scope.temp_data_per_slot , function(value , key)
// {
//     console.log(key);
//     $scope.drawGauge(key);
// });
// }










// $scope.pie_chart_in_dslam_slot = function(){
//     var down = $scope.card_data_in_dslam[$scope.current_cart_number].down_ports_count ;
//     var up = $scope.card_data_in_dslam[$scope.current_cart_number].up_ports_count;
//     var total = $scope.card_data_in_dslam[$scope.current_cart_number].total_ports_count ;
//     down = ($scope.card_data_in_dslam[$scope.current_cart_number].down_ports_count / $scope.card_data_in_dslam[$scope.first_tab.currentPage-1].total_ports_count);
//     up = ($scope.card_data_in_dslam[$scope.current_cart_number].up_ports_count / $scope.card_data_in_dslam[$scope.first_tab.currentPage-1].total_ports_count);
//     Highcharts.chart('pie-slot', {
//         chart: {
//             plotBackgroundColor: null,
//             plotBorderWidth: null,
//             plotShadow: false,
//             type: 'pie',
//             width : 300 ,


//         },
//         title: {
//             text: 'Up/Down Ports'
//         },
//         tooltip: {
//             pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
//         },
//         plotOptions: {
//             pie: {
//                size: 200,
//                allowPointSelect: true,
//                cursor: 'pointer',
//                dataLabels: {
//                 enabled: true,
//                 format: '<b>{point.name}</b>: {point.percentage:.1f} %',
//                 style: {
//                     color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
//                 }
//             }
//         }
//     },
//     exporting: {
//         enabled: false
//     },
//     credits: {
//         enabled: false
//     },
//     series: [{
//         name: 'Brands',
//         colorByPoint: true,
//         data: [
//         {
//             name: 'Up',
//             y: up
//         }, {
//             name: 'Down',
//             y: down,

//         }]
//     }]
// });
// }
$scope.run_tempreture_loader   = false;
$scope.drawTempreturePerSlotINDslam = function(name){

  $scope.run_tempreture_loader   = true;
  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam/' + $scope.dslam_id + '/dslam_range_temperature_report/',
    params:{
      card_number : $scope.current_cart_number + 1,
      temp_name : name
    }
  }).then(function (result) {
    $scope.chart_show_per_slot = true;
    $scope.run_tempreture_loader   = false;
    console.log(result);
    var chart = {
      zoomType: 'xy',

      height : 400,

    };

    var title = {
      text: 'Temperature ' + name
    };
    var xAxis = {
      categories: result.data.names,
      crosshair: true,
      // minTickInterval: 140,
      labels: {
        // enabled: false
        // rotation: -70,
        style: {
          fontSize: '13px',
          fontFamily: 'tahoma,Verdana, sans-serif'
        }
      }

    };
    var plotOptions =  {

      size: 100,
    };
    var credits = {
      enabled: false
    };
    var yAxis = [{ // Primary yAxis
      labels: {
        format: '{value}\xB0C',
        style: {
          color: Highcharts.getOptions().colors[1]
        }
      },
      title: {
        text: 'Temperature',
        style: {
          color: Highcharts.getOptions().colors[1]
        }
      }
    }];
    var tooltip = {
      shared: true
    };
    var legend = {
      layout: 'vertical',
      align: 'left',
      x: 120,
      verticalAlign: 'top',
      y: 100,
      floating: true,
      backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
    };
    var series = [{
      showInLegend: false,
      name: 'Temperature',
      type: 'spline',
      data: result.data.values,
      tooltip: {
        valueSuffix: '\xB0C'
      }
    }
  ];
  var json = {};
  json.chart = chart;
  json.plotOptions = plotOptions;
  json.title = title;
  //json.subtitle = subtitle;
  json.xAxis = xAxis;
  json.yAxis = yAxis;
  json.tooltip = tooltip;
  json.credits= credits;
  json.legend = legend;
  json.series = series;
  $('#sec-per-slot-chart').highcharts(json);

}, function (err) {

});
}

$scope.changeDslamShow = function(dir ){
  if(dir == 'prev'){
    if($scope.first_true_item>0){
      $scope.first_true_item -= 1 ;
      $scope.card_data_in_dslam[$scope.last_true_item].show = false;

      $scope.card_data_in_dslam[$scope.first_true_item].show = true;
      $scope.last_true_item -=1;

    }

  }
  else{

    if($scope.last_true_item < $scope.card_data_in_dslam.length-1){
      $scope.card_data_in_dslam[$scope.first_true_item].show = false;
      $scope.first_true_item+= 1 ;

      $scope.last_true_item+=1;

      $scope.card_data_in_dslam[$scope.last_true_item].show = true;
    }

  }
}

$scope.waste = {};
$scope.addWastedConfig = function(){
  fetchResult.fetch_result({
    method: 'POST',
    url: ip + 'api/v1/dslam/faulty-config/',
    data : {
      dslam_id : $scope.dslam_id ,
      slot_number_from : $scope.waste.slot_number_from,
      slot_number_to : $scope.waste.slot_number_to,
      port_number_from : $scope.waste.port_number_from,
      port_number_to : $scope.waste.port_number_to
    }
  }).then(function (result) {

    $scope.getWastedList();
    $scope.getWastedPortList();
    if(parseInt (result.status) < 400)
    {
      var notification = alertify.notify('Done', 'success', 5, function () {
      });}

      else{
        var notification = alertify.notify(result.statusText, 'error', 5, function () {
        });
      }

    }).then(function () {

    });
  }
  $scope.wasted = {};
  $scope.wasted.page = 1;
  $scope.wasted.max_size = 10 ;
  $scope.getWastedList = function(){
    fetchResult.fetch_result({
      method: 'GET',
      url: ip + 'api/v1/dslam/faulty-config/?dslam_id=' +  $scope.dslam_id + '&page=' + $scope.wasted.page + '&page_size=10',

    }).then(function (result) {
      $scope.wasted_list = result.data.results ;
      $scope.wasted.TotalItems = parseInt(result.data.count) ;

    }).then(function () {

    });
  }
  $scope.UpdateFaultyPorts = function(data , id ){
    fetchResult.fetch_result({
      method: 'PUT',
      url: ip + 'api/v1/dslam/faulty-config/' + id + '/',
      data : {
        dslam_id : $scope.dslam_id ,
        slot_number_from : data.slot_number_from,
        slot_number_to : data.slot_number_to,
        port_number_from : data.port_number_from,
        port_number_to : data.port_number_to
      }
    }).then(function (result) {
      if(parseInt (result.status) < 400)
      {
        var notification = alertify.notify('Done', 'success', 5, function () {
        });}
        else{
          var notification = alertify.notify(result.statusText, 'error', 5, function () {
          });
        }

        $scope.getWastedList();
        $scope.getWastedPortList();

      }).then(function () {

      });
    }
    $scope.DeleteFaultyPorts = function(data){

      fetchResult.fetch_result({
        method: 'DELETE',
        url: ip + 'api/v1/dslam/faulty-config/' + data.id + '/',

      }).then(function (result) {
        if(parseInt (result.status) < 400)
        {
          var notification = alertify.notify('Done', 'success', 5, function () {
          });}
          else{
            var notification = alertify.notify(result.statusText, 'error', 5, function () {
            });
          }
          $scope.getWastedList();
          $scope.getWastedPortList();

        }).then(function () {

        });
      }
      $scope.wasted_port = {};
      $scope.wasted_port.page = 1;
      $scope.wasted_port.max_size = 10 ;
      $scope.getWastedPortList = function(){
        fetchResult.fetch_result({
          method: 'GET',
          url: ip + 'api/v1/dslamport/faulty/?dslam_id=' +  $scope.dslam_id + '&page=' + $scope.wasted_port.page + '&page_size=10',

        }).then(function (result) {
          $scope.wasted_list_port = result.data.results ;
          $scope.wasted_port.TotalItems = parseInt(result.data.count) ;

        }).then(function () {

        });
      }
      $scope.getWastedList();
      $scope.getWastedPortList();

      $scope.port_list = {};
      $scope.port_list.page = 1 ;
      $scope.getPortList = function(){
        fetchResult.fetch_result({
          method: 'GET',
          url: ip + 'api/v1/dslam-port/' ,
          params : {
            page : $scope.port_list.page ,
            page_size : 10 ,
            search_dslam_id : $scope.dslam_id,
            search_slot_number : $scope.port_list.slot ,
            search_port_number : $scope.port_list.port
          }

        }).then(function (result) {
          $scope.port_list.count = result.data.count;
          $scope.port_list.data = result.data.results ;

        }).then(function () {

        });
      }
      $scope.getPortList();


      $scope.drawGauge = function(index){
        console.log($scope.temp_data_per_slot[index]);
        console.log('container-temp-' + index);
        console.log(parseInt($scope.temp_data_per_slot[index].value));
        $scope.ChartObj = Highcharts.chart('container-temp-' + index, {
          chart : {
            type: 'solidgauge'
          },
          title : null,
          pane : {
            center: ['50%', '85%'],
            size: '100%',
            startAngle: -90,
            endAngle: 90,
            background: {
              backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || '#EEE',
              innerRadius: '60%',
              outerRadius: '100%',
              shape: 'arc'
            }
          },

          tooltip : {
            enabled: false
          },

          // the value axis
          yAxis : {
            stops: [
              [0.1, '#55BF3B'], // green
              [0.5, '#DDDF0D'], // yellow
              [0.9, '#DF5353'] // red
            ],
            lineWidth: 0,
            minorTickInterval: null,
            tickPixelInterval: 400,
            tickWidth: 0,
            title: {
              y: -70
            },
            labels: {
              y: 16
            },
            min: 0,
            max: 100,
            title: {
              text: 'C'
            }
          },
          plotOptions : {
            solidgauge: {
              dataLabels: {
                y: 5,
                borderWidth: 0,
                useHTML: true
              }
            }
          },
          exporting: {
            enabled: false
          },

          credits: {
            enabled: false
          },

          series : [{
            name: $scope.temp_data_per_slot[index].name,
            data: [parseInt($scope.temp_data_per_slot[index].value)],
            tooltip: {
              valueSuffix: 'C'
            }
          }]

        });
      }




    });
