angular.module('portman.quickSearch', ['myModule'])
.config(function ($stateProvider, $urlRouterProvider) {
  $stateProvider
  .state('quick-search', {
    url: '/quick-search',
    views: {
      'content': {
        templateUrl: 'templates/quickSearch/quick-search.html',

        controller: 'QuickSearchController'
      }
    },
  });
})
.controller('QuickSearchController', function ($scope , $rootScope, fetchResult
  , $stateParams, ip , $http  , $interval , $timeout , $location ,ngSocket ) {
    $scope.quick_access = {} ;
    $scope.quick_access.telecom_center = [];
    $scope.quick_access.city = [];
    $scope.quick_access.dslam_name = [];
    $scope.is_port_selected = false;
    $scope.port_data = {};
    $scope.searchMac = function(query){
      if(query != undefined){
      fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/quick-search/',
        params : {
          value : query
        }
      }).then(function (result) {
        if(result.data.result.ports){
          $scope.quick_access_data = result.data.result.ports[0] ;
          $scope.dslam_id = $scope.quick_access_data.dslam_id;
          $scope.quick_access.slot = $scope.quick_access_data.slot_number;
          $scope.quick_access.port = $scope.quick_access_data.port_number;
          $scope.quick_access.dslam_name = $scope.quick_access_data.dslam_name ;
          $scope.port_data.port_name = $scope.quick_access_data.port_name ;
          $scope.port_data.id = $scope.quick_access_data.id ;
          $scope.get_command_list();
          $scope.getCommandResult();
          $scope.load_dslam_report();
          $scope.get5LastPortCommandResult();
          load_report_chart();
        }
        else {
          $scope.quick_access_data = null;
        }
      }, function (err) {
      }
    );
  }
}
  $scope.searchPort = function(){
    if($scope.quick_access.port !== undefined && $scope.quick_access.port != '' &&
    $scope.quick_access.slot !== undefined && $scope.quick_access.slot != ''
    && $scope.quick_access.dslam_name != undefined && $scope.quick_access.dslam_name != '')
    {

      fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/dslam-port/',
        params: {
          search_username : $scope.quick_access.number,
          search_mac_address : $scope.quick_access.mac,
          search_identifiyer_key : $scope.quick_access.identifier,
          search_dslam_id: $scope.quick_access.dslam_name.id ,
          search_telecom: ($scope.quick_access.telecom_center.id) ? $scope.quick_access.telecom_center.id : $scope.quick_access.telecom_center,
          search_port_number: $scope.quick_access.port,
          search_slot_number: $scope.quick_access.slot,
          search_city: ($scope.quick_access.city.id) ? $scope.quick_access.city.id : $scope.quick_access.city,
          // search_line_profile: $scope.selected_line_profile,
        }
      }).then(function (result) {
        $scope.null_data = false
        $scope.port_data = result.data.results[0];
        console.log($scope.port_data);
        $scope.is_port_selected = true;

        load_report_chart();

        if(result.data.results[0] == undefined || result.data.results[0] == 'undefined')
        {
          var notification = alertify.notify('Undefined', 'error', 5, function () {
          });
        }
        else{

          if(result.data.results[0].length < 1){
            $scope.null_data = true;
          }
          else{

            $scope.dslam_id = angular.fromJson($scope.port_data).dslam;

            $scope.load_report();
            $scope.getCommandResult();


          }
        }



      }, function (err) {
      }
    );
  }
  else{
    // $scope.is_port_selected = false;
    // $scope.get_command_list('dslam');
    var notification = alertify.notify('Complete needed fields', 'error', 5, function () {
    });

  }

}




var getPingResult = function(){
  fetchResult.fetch_result({
    method: 'POST',
    url: ip + 'api/v1/dslam/icmp/command/',
    data : {
      dslam_id: $scope.dslam_id,
      icmp_type:"ping" ,
      params:{count: 4, timeout: 0.2} ,
      count:4 ,
      timeout:0.2 ,
    }
  }).then(function (result) {
    $scope.has_command_result = true ;
    $scope.ping_result = result.data.result ;



  }, function (err) {
  }
);
}
$scope.getProveList = function(query){
  return fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/city/?parent=all',
    params : {
      city_name : query
    }
  }).then(function (result) {
    if(result.data.results){
      return result.data.results ;}
      return [];
      //  $scope.cities = result.data.results;

    }, function (err) {
    }
  );
}
$scope.getProveList() ;

$scope.fetchChildParent = function () {

  return fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/city/?parent=' + $scope.quick_access.prove.id,
    params : {
      city_name : $scope.quick_access.city
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

};

$scope.selectCity = function (query) {

  if($scope.quick_access.city.id || $scope.quick_access.prove.id)
  {
    if($scope.quick_access.city.id)
    {
      var city_ids = $scope.quick_access.city.id;
    }
    else
    {
      var  city_ids= $scope.quick_access.prove.id;
    }
  }


  return  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/telecom-center/',
    params : {
      search_city_id : city_ids ,
      search_name : query
    }
  }).then(function (result) {
    if(result.data.results){
      return result.data.results;
    }
    return [];

    //  $scope.tele = result.data

  },function () {

  });
}

$scope.searchDslamName = function(query){
  return $http({
    method: "GET",
    url: ip + 'api/v1/dslam/',
    params: {
      page_size: 20,
      search_city : ($scope.quick_access.city.id) ? $scope.quick_access.city.id : $scope.quick_access.city,
      search_dslam: query,
      search_telecom : ($scope.quick_access.telecom_center.id) ? $scope.quick_access.telecom_center.id : $scope.quick_access.telecom_center

    }
  }).then(function mySucces(data) {
    if(data.data.results){

      return data.data.results;
    }
    return [];

  });
}
$scope.quickSearch = function(){
  return fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/quick-search/',
    params : {
      value : $scope.quicksearch.data
    }
  }).then(function (result) {

    $scope.commands = [];
    $scope.quick_access_data = result.data.result ;
    if(result.data.result.ports.length > 0 )
    {
      $scope.port_data = result.data.result.ports[0] ;


      $scope.dslam_id = angular.fromJson($scope.port_data).dslam_id;
      $scope.get_command_list();
      $interval(function() {
        $scope.load_report();
        $scope.getCommandResult();
      }, 2000 , 3);
    }

    else{

      $scope.null_data = true;
    }

  }, function (err) {
  }
);

}
$scope.get_command_list = function(){

  $scope.is_port_selected = false;


  var params = {
    exclude_type : 'slot',
    dslam_id : $scope.dslam_id
  }

  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/command/',
    params  : params
  }).then(function (result) {

    $scope.commands = result.data;

  }, function (err) {
  }
);
}
$scope.checkMacData = function(data){
  $scope.mac_list = data ;
}
$scope.Showmodal = function(data){

  $scope.modal_data = [];

  $scope.modal_data = data;


}
$scope.has_command_result = false ;
$scope.is_loading = false;
$scope.run_command = function(){


  if($scope.quick_access.commant_type === 'undefined' || $scope.quick_access.commant_type === undefined)
  {

    var notification = alertify.notify('Command type is empty', 'error', 5, function () {

    });
    return ;
  }
  $scope.is_loading = true;
  if($scope.quick_access.commant_type == 'change admin status'){


    if(angular.fromJson($scope.quick_access.port_number).admin_status == 'UNLOCK')
    {
      var lock_status = 'LOCK';
    }
    else {
      var lock_status = 'LOCK';
    }
    $scope.params = {
      "type": "dslamport",
      "is_queue": false,
      'dslam_id' : $scope.dslam_id,
      "admin_status": lock_status,
      "port_conditions" :{
        "slot_number": $scope.quick_access.slot,
        "port_number" : $scope.quick_access.port,
      }


    }
  }
  else if($scope.quick_access.commant_type === 'lcman show' ||
  $scope.quick_access.commant_type === 'show mac' || $scope.quick_access.commant_type === 'profile adsl show'){
    $scope.params = {
      "type": "dslam",
      'dslam_id' : $scope.dslam_id ,
      "is_queue" : false,

    }
  }
  else if( $scope.quick_access.commant_type == 'show linerate' || $scope.quick_access.commant_type == 'show linestat port'){

    $scope.params = {
      "type": "dslamport",
      "is_queue": false,
      'dslam_id' : $scope.dslam_id ,
      "port_conditions" :{
        "slot_number": $scope.quick_access.slot,
        "port_number" : $scope.quick_access.port,
      }
    }
  }

  else{
    $scope.params = {
      "type": "dslamport",
      "is_queue": false,
      'dslam_id' : $scope.dslam_id ,
      "port_conditions" :{
        "slot_number": $scope.quick_access.slot,
        "port_number" : $scope.quick_access.port,
      }
    }
  }


  fetchResult.fetch_result({
    method: 'post',
    data: {
      "dslam_id": $scope.dslam_id,
      "params": $scope.params,
      "command": $scope.quick_access.commant_type
    },
    url: ip + 'api/v1/dslamport/command/'
  }).then(function (result) {
    $scope.is_loading = false;


    if(result.status <400){
      var notification = alertify.notify("Done", 'success', 5, function () {

      });
      $scope.has_command_result = true ;

      if(result.data.result.result){
        $scope.command_result = result.data.result.result ;
      }
      else{
        $scope.command_result = result.data.result[0] ;
      }
      $interval(function(){
        if($scope.quick_access.port!== undefined && $scope.quick_access.port != '' &&
        $scope.quick_access.slot !== undefined && $scope.quick_access.slot != '')
        {
          $scope.load_report();

          $scope.get5LastPortCommandResult()
        }

        $scope.getCommandResult();
        $scope.load_dslam_report();
      },3000,2);

    }
    else{
      var notification = alertify.notify(result.statusText, 'error', 5, function () {

      });


    }


  }, function (err) {


  });
}
$scope.selectedPort = function(a){
  $scope.get_command_list();

}



$scope.load_report = function () {

  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/port-command/?dslam=' + $scope.dslam_id + '&slot_number=' + $scope.quick_access.slot +  '&port_number=' + $scope.quick_access.port + '&command_type_name=' + $scope.quick_access.commant_type + '&limit_row=2'
  }).then(function (result) {

    if(result.data.length > 0 ){
      $scope.has_command_result = true ;
    }
    $scope.result_commands = angular.fromJson(result.data);
  }, function (err) {
  }
);
}
$scope.get5LastPortCommandResult = function () {

  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/port-command/?dslam=' + $scope.dslam_id + '&slot_number=' + $scope.quick_access.slot +  '&port_number=' + $scope.quick_access.port + '&limit_row=' + 5
  }).then(function (result) {
    $scope.last_5_port_command_result = angular.fromJson(result.data);
  }, function (err) {
  }
);
}
$scope.getCommandResult = function () {

  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam/command/result/?' +
    'dslam=' + $scope.dslam_id +  '&' +
    'command_type=' + $scope.quick_access.commant_type +
    '&limit_row=2'
  }).then(function (result) {
    $scope.result_commands2 = result.data;
    if(result.data.length > 0)
    {
      $scope.has_command_result = true ;
    }

  }, function (err) {
  }
);
};


$scope.load_dslam_report = function () {

  fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam/command/result/?' +
    'dslam=' + $scope.dslam_id + '&' +
    'limit_row=' + 5
  }).then(function (result) {
    $scope.dslam_result_commands= result.data;

  }, function (err) {
  }
);
};
$scope.checkRes = function(){

  $scope.getCommandResult();
  console.log($scope.quick_access.port, $scope.quick_access.slot);
  if($scope.quick_access.port!== undefined && $scope.quick_access.port != '' && $scope.quick_access.port != null&&
  $scope.quick_access.slot !== undefined && $scope.quick_access.slot != '' && $scope.quick_access.slot != null)
  {
    $scope.load_report();
    //$scope.searchPort();
  }
}
$scope.checkCommandResult = function(){
  if($scope.quick_access.port!== undefined && $scope.quick_access.port !== '' && $scope.quick_access.port != null&&
  $scope.quick_access.slot !== undefined && $scope.quick_access.slot !== '' && $scope.quick_access.slot != null)
  {
    $scope.load_report();
    $scope.get5LastPortCommandResult();
    //$scope.searchPort();
  }
}
$scope.AveTraffic = function(){
  Highcharts.setOptions({
    global: {
      useUTC: false
    }
  });

  $timeout(function () {

    $scope.ave_traffic = Highcharts.chart('ave-traffic', {
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
        text: 'Port Traffic',
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
        format: '{value} KB/Sec',
        style: {
          color: Highcharts.getOptions().colors[0]
        }
      },
    },
    { // Secondary yAxis
      title: {
        text: 'Average Traffic',
        style: {
          color: Highcharts.getOptions().colors[0]
        }
      },
      labels: {
        format: '{value} KB/Sec',
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
        return '<b>' + ' Time: ' + Highcharts.dateFormat('%H:%M:%S', this.x) + '</b>' + '<br>'
        +

        '<b>' + "Upstream"+ ': ' + this.points[0].y + '</b><br/>' +
        '<b>' + "DownStream" + ': ' + this.points[1].y + '</b>'
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
      name: 'Send', //$scope.names[i] + ' ' + 'tx',
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
          return '123123123'
        }
      },
      data: (function () {
        var time = new Date().getTime();


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
    {
      name: 'Receive', //$scope.names[i] + ' ' + 'rx',
      color: 'red',
      fillColor: {
        linearGradient: {
          x1: 0,
          y1: 0,
          x2: 0,
          y2: 1
        },
        stops: [
          [0, Highcharts.getOptions().colors[5]],
          [1, Highcharts.Color(Highcharts.getOptions().colors[5]).setOpacity(0).get('rgba')]
        ]
      },
      data: (function () {
        var d = new Date();//Date.parse("Month day, year");
        var time = d.getTime();

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
    }



  ],
  func: function (chart) {
    $timeout(function () {
      chart.reflow();
    }, 1000);
  }
});
}, 1000);
}

$scope.show_chart = false;
$scope.socket_count = 0;
$scope.first_time = true;
$scope.changeShowState = function () {

  $scope.show_chart = !$scope.show_chart ;
  if( $scope.show_chart){
    $scope.AveTraffic();
    $scope.socket_count = 0;
    //  $scope.first_time = false;
  }
  if($scope.show_chart ){


    $timeout(function(){

      $scope.rout_location = $location.path();
      $scope.ws = ngSocket('ws://5.202.129.160:2083/ws/');
      $scope.ws.send('{"action": "port_status", "params": {"port":{"port_index":' + $scope.port_data.port_index + ',"port_number":' + $scope.quick_access.port + ',"slot_number":' + $scope.quick_access.slot + ' }}, "dslam_id":'+ $scope.dslam_id + '}')

      $scope.ws.onMessage(function (message) {
        if($location.path() == $scope.rout_location){
          $scope.socket_count = $scope.socket_count+1;
          var data = angular.fromJson(message.data);
          data = angular.fromJson(data);



          var d = new Date();
          var year = d.getFullYear();
          var month = d.getMonth();
          var day = d.getDay();

          var x2 = data.time;

          var time = x2.split(':');

          var date = new Date(year,month,day,time[0],time[1],time[2]);
          var x = d.getTime(); //date.getTime();


          var y = parseInt(data['ADSL_UPSTREAM_ATTEN']);

          var y1 = parseInt(data['ADSL_DOWNSTREAM_ATTEN']);


          $scope.ave_traffic.series[0].addPoint([x, parseInt(data['INCOMING_TRAFFIC_AVERAGE_RATE']) ], false, true);
          $scope.ave_traffic.series[1].addPoint([x, parseInt(data['OUTGOING_TRAFFIC_AVERAGE_RATE']) ], true, true);

          $scope.admin_status  = data['PORT_ADMIN_STATUS'] ;
          $scope.oper_status = data['PORT_OPER_STATUS'];


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
var load_report_chart = function () {
  fetchResult.fetch_result({
    method: 'GET',
    url : ip +  'api/v1/dslam-port/'+ $scope.port_data.id + '/report/'
  }).then(function (result) {

    $scope.chart_data = angular.fromJson(result.data);

    $scope.chart_data.snr_data = angular.fromJson($scope.chart_data.snr_data);
    $scope.chart_data.tx_data = angular.fromJson($scope.chart_data.tx_data);
    $scope.chart_data.attenuation_data = angular.fromJson($scope.chart_data.attenuation_data);
    $scope.chart_data.attainable_rate_data = angular.fromJson($scope.chart_data.attainable_rate_data);
    $scope.chart_data.dates = angular.fromJson($scope.chart_data.dates);
    $scope.chart_data.oper_status = angular.fromJson( $scope.chart_data.oper_status);
    $scope.chart_data.oper_status.data = angular.fromJson( $scope.chart_data.oper_status.data);
    $scope.draw_port_snr_change();
    $scope.draw_port_tx_rate();




  });
}




$scope.draw_port_snr_change = function(){

  $('#port-snr').highcharts({
    chart: {

      height: 400,
      plotBackgroundColor: null,
      plotBorderWidth: null,
      plotShadow: false,
      type: 'spline'
    },
    title: {
      text: 'Port SNR Change'
    },
    credits: {
      enabled: false
    },
    xAxis: {
      categories: $scope.chart_data.dates,
      labels: {

        rotation: -70,
        style: {
          fontSize: '13px',
          fontFamily: 'tahoma,Verdana, sans-serif',
        }
      },
      title: {
        text: 'Date'
      }
    },
    yAxis: {
      tickInterval: 100,
      title: {
        text: 'SNR (db)'
      },
      min: 0
    },
    tooltip: {
      shared: true,
      crosshairs: true,

    },
    plotOptions: {
      spline: {
        marker: {
          enabled: true
        }
      }
    },
    series:[
      {
        data : angular.fromJson($scope.chart_data.snr_data[0].data),
        name : $scope.chart_data.snr_data[0].name,
      },
      {
        data : angular.fromJson($scope.chart_data.snr_data[1].data),
        name : $scope.chart_data.snr_data[1].name,
      },
    ]

  });


}

$scope.draw_port_tx_rate = function(){
  console.log('222222222222');
  $('#port-tx').highcharts({
    chart: {
      // width: 500,
      height: 400,
      plotBackgroundColor: null,
      plotBorderWidth: null,
      plotShadow: false,
      type: 'area'
    },
    credits: {
      enabled: false
    },
    title: {
      text: 'Port TX Rate'
    },
    xAxis: {
      categories: $scope.chart_data.dates,
      labels: {

        rotation: -70,
        style: {
          fontSize: '13px',
          fontFamily: 'tahoma,Verdana, sans-serif',
        }
      },
      title: {
        text: 'Date'
      }
    },
    yAxis: {
      title: {
        text: 'TX Rate (kps)'
      },
      min: 0
    },
    tooltip: {
      headerFormat: '<b>{series.name}</b><br>',
      pointFormat: '{point.x}: {point.y} kps'
    },
    plotOptions: {
      area: {
        marker: {
          enabled: false,
          symbol: 'circle',
          radius: 2,
          states: {
            hover: {
              enabled: true
            }
          }
        }
      }
    },
    series:
    [{
      data : $scope.chart_data.tx_data[0].data,
      name : $scope.chart_data.tx_data[0].name,
    },
    {
      data : $scope.chart_data.tx_data[1].data,
      name : $scope.chart_data.tx_data[1].name,
    },
  ]
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
$scope.searchChanged = function(){
  $scope.quick_access.city = null ;
  $scope.quick_access.telecom_center = null ;
  $scope.quick_access.dslam_name = null;
  $scope.quick_access.commant_type = null;
  $scope.commands = [];
  $scope.quick_access.slot = null ;
  $scope.quick_access.port = null ;
  $scope.quick_access.mac_address = null;
}
$scope.provinceChanged = function(){
  $scope.quick_access.city = null ;
  $scope.quick_access.telecom_center = null ;
  $scope.quick_access.dslam_name = null;
  $scope.quick_access.commant_type = null;
  $scope.commands = [];
  $scope.quick_access.slot = null ;
  $scope.quick_access.port = null ;
}
$scope.cityChanged = function(){
  $scope.quick_access.telecom_center = null ;
  $scope.quick_access.dslam_name = null;
  $scope.quick_access.commant_type = null;
  $scope.commands = [];
  $scope.quick_access.slot = null ;
  $scope.quick_access.port = null ;
}
$scope.teleChanged = function(){
  $scope.quick_access.dslam_name = null;
  $scope.quick_access.commant_type = null;
  $scope.commands = [];
  $scope.quick_access.slot = null ;
  $scope.quick_access.port = null ;
}
$scope.dslamChanged = function(){
  $scope.quick_access.commant_type = null;
  $scope.commands = [];
  $scope.quick_access.slot = null ;
  $scope.quick_access.port = null ;
}
$scope.seletedDslam = function () {
    $scope.dslam_id =  $scope.quick_access.dslam_name.id ;
    if($scope.quick_access.search_by == 'Province')
    {
      $scope.quick_access.dslam_name = $scope.quick_access.dslam_name.name ;
    }
    console.log($scope.quick_access.dslam_name);
}

});
