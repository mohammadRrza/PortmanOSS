angular.module('portman.resellerreport', ['myModule'])
.config(function ($stateProvider) {
  $stateProvider
  .state('reseller-report', {
    url: '/reseller/:reseller_id/report',
    views: {
      'content': {
        templateUrl: 'templates/reseller/reseller-report.html',

        controller: 'ResellerReportController'
      }
    }
  });
}).controller('ResellerReportController', ['$scope', 'fetchResult', '$state', 'ip' , '$stateParams' , function ($scope, fetchResult, $state,ip , $stateParams)
{
  $scope.reseller_id = $stateParams.reseller_id ;
  $scope.reseller_detail = {};
  $scope.getResellerDetail = function(){
    fetchResult.fetch_result({
      method: 'GET',
      url: ip + 'api/v1/reseller/' + $scope.reseller_id  + '/report/',

    }).then(function (result) {

      $scope.up_ports_count = result.data.up_ports_count;
      $scope.down_ports_count = result.data.down_ports_count;
      $scope.total_ports_count = result.data.total_ports_count;
      $scope.telecom_list = result.data.data;
      console.log(result.data.data[0]);
      $scope.draw_chart(result.data.data[0]);
      $scope.getPortDetaile($scope.telecom_list[0].telecom_center.id , $scope.telecom_list[0].telecom_center.name);
    }, function (err) {
    });

  }
  $scope.getResellerDetail();

  $scope.draw_chart = function(){
    Highcharts.chart('up-down', {
      chart: {
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'pie'
      },
      title: {
        text: 'Up Down Ports'
      },
      tooltip: {
        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
      },
      plotOptions: {
        pie: {
          allowPointSelect: true,
          cursor: 'pointer',
          dataLabels: {
            enabled: true,
            format: '<b>{point.name}</b>: {point.percentage:.1f} %',
            style: {
              color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
            }
          }
        }
      },
      credits: {
        enabled: false
      },
      exporting: {
        enabled: false
      },
      series: [{
        name: 'Reseller Port',
        colorByPoint: true,
        data: [{
          name: 'Up',
          y: (($scope.up_ports_count / $scope.total_ports_count)*100)
        }, {
          name: 'Down',
          y: (($scope.down_ports_count / $scope.total_ports_count) *100 ),

        } ]
      }]
    });
  }
 $scope.pagination_port_list = {};
 $scope.pagination_port_list.page = 1;
  $scope.getPortDetaile = function (tele_id , tele_name) {
    $scope.tele_name = tele_name ;
    $scope.tele_id = tele_id ;
    console.log(tele_id , tele_name);
    fetchResult.fetch_result({
      method: 'GET',
      url: ip + 'api/v1/dslam-port/' ,
      params :{
        page : $scope.pagination_port_list.page,
        page_size : '10',
        search_telecom: tele_id,
      }
    }).then(function (result) {
        $scope.pagination_port_list.count = result.data.count ;
        $scope.port_list = result.data.results ;
      console.log(result);
    }, function (err) {
    });
  }


}]);
