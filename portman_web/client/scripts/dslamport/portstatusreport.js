angular.module('portman.portstatusreport', ['myModule'])
.config(function ($stateProvider, $urlRouterProvider) {
$stateProvider
.state('dslamport-report', {
    url: '/dslamport/:dslam_id/:port_id/status-report',
    views: {
        'content': {
            templateUrl: 'templates/dslamport/port_status_report.html',

            controller: 'PortStatusReportController'
        }
    },
});
})
.controller('PortStatusReportController', function ($scope,$rootScope, fetchResult, $stateParams, ip , ngSocket , $location ,  $timeout , $window ) {


$scope.dslam_id = $stateParams.dslam_id;
$scope.port_id = $stateParams.port_id;
$scope.port_id = '';
$scope.limit_row_result_commands = 5;
$scope.selected_command_type = '';
$scope.dslamport = [];
$scope.dslam = ''
$scope.start_date = '';
$scope.end_date = '';


fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/command/',
    params  : {
        type : 'port',
        dslam_id : $scope.dslam_id
    }
}).then(function (result) {
    $scope.commands = result.data;

}, function (err) {
}
);

fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/vlan/'
}).then(function (result) {

    $scope.vlans = result.data.results;

}, function (err) {
}
);


var load_report = function () {
    fetchResult.fetch_result({
        method: 'GET',
        url : ip +  'api/v1/dslam-port/'+ $stateParams.port_id + '/report/'
//  url: ip + 'api/v1/dslamport/port-status-report/?dslam_id=' + $scope.dslam_id + '&slot_number=' + $scope.slot_number + '&port_number=' + $scope.port_number + '&start_date=' + $scope.start_date + '&end_date=' + $scope.end_date
}).then(function (result) {
console.log('load_report' , result.data);
$scope.chart_data = angular.fromJson(result.data);

$scope.chart_data.snr_data = angular.fromJson($scope.chart_data.snr_data);
$scope.chart_data.tx_data = angular.fromJson($scope.chart_data.tx_data);
$scope.chart_data.attenuation_data = angular.fromJson($scope.chart_data.attenuation_data);
$scope.chart_data.attainable_rate_data = angular.fromJson($scope.chart_data.attainable_rate_data);
$scope.chart_data.dates = angular.fromJson($scope.chart_data.dates);
$scope.chart_data.oper_status = angular.fromJson( $scope.chart_data.oper_status);
$scope.chart_data.oper_status.data = angular.fromJson( $scope.chart_data.oper_status.data);
$scope.draw_port_operational_status();
// fetchResult.fetch_result({
//     method: 'GET',
// url: ip + 'api/v1/dslam-port/'+ $stateParams.port_id +'/mac_address/' //?dslam_id=' + $scope.dslam_id //+ '&slot_number=' + $scope.slot_number + '&port_number=' + $scope.port_number
// }).then(function (result) {
// $scope.mac_addres = result.data.mac ;

// });


if (fetchResult.checkNullOrEmptyOrUndefined($scope.dslamport.port_vlan)) {
$scope.port_vlan = JSON.parse($scope.dslamport.port_vlan)[0].fields.vlan_id;
}
});
}


load_report();

$scope.draw_port_operational_status = function(){
console.log('draw_port_operational_status');
$scope.pie_data_chart = [];
angular.forEach($scope.chart_data.oper_status.data , function(value , key)
{
    $scope.pie_data_chart.push({name:value.name , y :value.y});
})
$scope.test_chart = $('#oper-status').highcharts({
    chart: {
    // width: 300,
     height: 370,
     plotBackgroundColor: null,
     plotBorderWidth: null,
     plotShadow: false,
     type: 'pie'
 },
 title: {
    text: 'Port Operational Status'
},
tooltip: {
    pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
},
credits: {
    enabled: false
},
plotOptions: {

    pie: {
        size : 150,
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
series :
[{
    data :  $scope.pie_data_chart
}]


});


$timeout(function() {
    $scope.draw_port_snr_change();
}, 100);

}
$scope.draw_port_snr_change = function(){
console.log('draw_port_snr_change');

$('#port-snr').highcharts({
    chart: {

       height: 400,
      // width : 300 ,
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
$timeout(function() {
    $scope.draw_port_tx_rate();
}, 200);

}

$scope.draw_port_tx_rate = function(){
console.log('draw_port_tx_rate');
$('#port-tx').highcharts({
    chart: {
      //  width: 300,
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

$timeout(function() {
    $scope.draw_port_Attenuation_change ()
}, 300);
}
$scope.draw_port_Attenuation_change = function(){
console.log('draw_port_Attenuation_change');
$('#port-attenuation').highcharts({
    chart: {
      //  width: 300,
        height: 370,
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'spline'
    },
    title: {
        text: 'Port Attenuation Change'
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
            text: 'Attenuation'
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
    series:
    [{
        data : $scope.chart_data.attenuation_data[0].data,
        name : $scope.chart_data.attenuation_data[0].name,
    },
    {
        data : $scope.chart_data.attenuation_data[1].data,
        name : $scope.chart_data.attenuation_data[1].name,
    },
    ]
});
$timeout(function() {
    $scope.draw_port_Attenuation_rate ()
}, 300);

}
$scope.draw_port_Attenuation_rate = function(){
console.log('draw_port_Attenuation_rate');
$('#port-attainable-rate').highcharts({
    chart: {
      //  width: 300,
        height: 370,
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'area'
    },
    title: {
        text: 'Port Attainable Rate Change'
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
    credits: {
        enabled: false
    },
    yAxis: {
        title: {
            text: 'Attainable Rate (kps)'
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
        data : $scope.chart_data.attainable_rate_data[0].data,
        name : $scope.chart_data.attainable_rate_data[0].name,
    },
    {
        data : $scope.chart_data.attainable_rate_data[1].data,
        name : $scope.chart_data.attainable_rate_data[1].name,
    },
    ]
});


}



$scope.getDslamDetaile = function(){
    console.log('getDslamDetaile');
fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam-port/' + $stateParams.port_id +'/',
}).then(function (result) {
    console.log(result.data);
    $scope.dslamport = result.data ;
    $scope.slot_number = $scope.dslamport.slot_number ;
    $scope.port_number = $scope.dslamport.port_number

//     fetchResult.fetch_result({
//         method: 'GET',
// //  url : ip +  'api/v1/dslam-port/'+ $stateParams.port_id + '/report'
// url: ip + 'api/v1/dslamport/port-status-report/?dslam_id=' + $scope.dslam_id + '&slot_number=' + $scope.slot_number + '&port_number=' + $scope.port_number + '&start_date=' + $scope.start_date + '&end_date=' + $scope.end_date
// }).then(function (result) {


// });
// }, function (err) {
 });
}

$scope.getDslamDetaile ();


var subscriberData = function(){
    console.log('subscriberData');
fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/customer-port/?dslamport_id=' + $stateParams.port_id ,

}).then(function (result) {
    console.log('///////////////');
    console.log(result.data.results);
    $scope.subscriber_detaile = result.data.results[0];
}, function (err) {
});
}

subscriberData();


var resellerData = function(){
    console.log('resellerData');
fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/reseller-port/?dslamport_id=' + $stateParams.port_id ,

}).then(function (result) {
    console.log('==============');
    console.log(result.data.results);
    $scope.reseller_detaile = result.data.results[0];

}, function (err) {
});

}

resellerData();


// fetchResult.fetch_result({
//         method: 'GET',
//         url: ip + 'api/v1/lineprofile/?dslam_id=' + $scope.dslam_id
//     }).then(function (result) {
//         $scope.line_profile = result.data;
//         $(".select-line-profile-data-array").select2({
//             data: $scope.line_profile
//         });
//     }, function (err) {
//     }
//     );

fetchResult.fetch_result({
method: 'GET',
url: ip + 'api/v1/dslamport/vlan/?dslamport_id=' + $stateParams.port_id ,

}).then(function (result) {
    console.log('vlam' ,result);
$scope.dslamport_detaile = result.results ;
}, function (err) {
});


$scope.new_line_profile = null;
$scope.new_admin_status = null;
$scope.change_port_line_profile_or_admin_status = function (val, type) {
    console.log('change_port_line_profile_or_admin_status');
if (type === 'line_profile' && $scope.old_line_profile !== val) {
    $scope.new_line_profile = val;
}
else if (type === 'admin_status' && $scope.old_admin_status !== val) {
    $scope.new_admin_status = val;
}
};

$scope.edited = false;
$scope.edit_form = function () {
    console.log('edit_form');
if ($('#btn_edit').text() === 'Save') {
    if (fetchResult.checkNullOrEmptyOrUndefined($scope.new_line_profile)) {
        fetchResult.fetch_result({
            method: 'POST',
            url: ip + 'api/v1/dslamport/port-line-profile/',
            data: {
                "dslam_id": $scope.dslam_id,
                "port_id": $scope.dslamport.port[0].pk,
                "new_line_profile": $scope.new_line_profile
            }
        }).then(function (result) {
            alert('change line profile');
        }, function (err) {
        });
    }

    if (fetchResult.checkNullOrEmptyOrUndefined($scope.new_admin_status)) {
        fetchResult.fetch_result({
            method: 'POST',
            url: ip + 'api/v1/dslamport/port-admin-status/',
            data: {
                "dslam_id": $scope.dslam_id,
                "port_id": $scope.dslamport.port[0].pk,
                "new_status": $scope.new_admin_status
            }
        }).then(function (result) {
            alert('change admin status');
        }, function (err) {
        });
    }
    // setTimeout(function () {
    //     load_report()
    // }, 2000);
}
toggleShow();
};

$scope.cancel_form = function () {
    console.log('cancel_form');
toggleShow();
}

function toggleShow() {
    console.log('toggleShow');
if (!$scope.edited) {
    $scope.edited = true;
    $('#btn_edit').text('Save');
    $('#btn_cancel').show();
    $('#lock_select').show();
    $('#admin_status_led').hide();
    $('#line_profile_label').hide();
    $('#line_profile_select_div').show();
    $('#reset_admin_status_btn').hide();
}
else {
    $scope.edited = false;
    $('#btn_edit').text('Edit');
    $('#lock_select').hide();
    $('#btn_cancel').hide();
    $('#admin_status_led').show();
    $('#line_profile_label').show();
    $('#line_profile_select_div').hide();
    $('#reset_admin_status_btn').show();
}

}

//Create JS Persian Calendar
fetchResult.loadFile('global/plugins/pcal/js-persian-cal.css');
fetchResult.loadFile('global/plugins/pcal/js-persian-cal.min.js', function () {
var objCal2 = new AMIB.persianCalendar('pcal2', {
//initialDate: '1395/5/1',
extraInputID: "pcal2_en", extraInputFormat: "YYYYMMDD"
});

var objCal2 = new AMIB.persianCalendar('pcal1', {
//initialDate: '1395/4/1',
extraInputID: "pcal1_en", extraInputFormat: "YYYYMMDD"
});
});
//End Block JS Persion Calendar
$scope.acl = {};
$scope.acl.vpi = 0;
$scope.acl.vci = 35;
$scope.acl.count = 1;

$scope.show_vlan_box = false;
$scope.port_pvc_set_show = false;
$scope.show_lineprofile_box = false;
$scope.show_performance = false;
$scope.show_profile_adsl_set = false;
$scope.show_profile_adsl_delete = false;
$scope.show_acl_maccount  = false;
$scope.show_uplink_pvc_set  = false;
$scope.selected_command_type= {};
$scope.getCommandResult = function () {
    console.log('getCommandResult');
$scope.show_acl_maccount  = false;
$scope.show_lineprofile_box = false;
$scope.show_vlan_box = false;
$scope.port_pvc_set_show = false;
$scope.show_performance = false;
$scope.show_profile_adsl_set = false;
$scope.show_profile_adsl_delete = false;
$scope.show_uplink_pvc_set  = false;



if($scope.selected_command_type.command !== undefined){
    if($scope.selected_command_type.command.name == 'port pvc set'){
       $scope.port_pvc_set_show = true;

   }
   else if($scope.selected_command_type.command.name == 'add to vlan'){
       $scope.show_vlan_box = true;

   }
   else if($scope.selected_command_type.command.name == 'change lineprofile port'){
     $scope.show_lineprofile_box = true;
 }
 else if($scope.selected_command_type.command.name == 'show performance'){
     $scope.show_performance = true;
 }
 else if($scope.selected_command_type.command.name == 'profile adsl set'){
    $scope.show_profile_adsl_set = true;
}
 else if($scope.selected_command_type.command.name == 'profile adsl change'){
    $scope.show_lineprofile_box = true;
}

else if($scope.selected_command_type.command.name == 'profile adsl delete' ){
    $scope.show_profile_adsl_delete = true;
}
else if($scope.selected_command_type.command.name == 'acl maccount set'){
    $scope.show_acl_maccount  = true;
}
else if($scope.selected_command_type.command.name == 'uplink pvc set'){
    $scope.show_uplink_pvc_set  = true;
}

console.log('getCommandResult' , $scope.selected_command_type.command.name)
fetchResult.fetch_result({
   method: 'GET',
   url: ip + 'api/v1/port-command/?dslam=' + $scope.dslam_id + '&dslamport_id=' + $stateParams.port_id +  '&command_type_id=' + $scope.selected_command_type.command.id +'&limit_row=1'
}).then(function (result) {
    console.log(result.data);
  $scope.result_commands = angular.fromJson(result.data);
}, function (err) {
}
);
}
else{
    console.log('else');
fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/port-command/?dslam=' + $scope.dslam_id + '&dslamport_id=' + $stateParams.port_id + '&limit_row=' + $scope.limit_row_result_commands + '&command_type_id='
}).then(function (result) {
    console.log(result.data);
    $scope.result_commands = angular.fromJson(result.data);
}, function (err) {
}
);
}

};
$scope.getLineProfileList = function(query){
//   $scope.line_profile_list = [];
console.log('getLineProfileList');
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


$scope.filter_report = function () {
$scope.start_date = $('#pcal1_en').val();
$scope.end_date = $('#pcal2_en').val();
load_report();
};

//Start Print Chart Plugin
$scope.create_pdf = function () {
$scope.form = $('#JSFiddle');
$scope.cache_width = $scope.form.width();
$scope.a4 = [900, 3000];  // for a4 size paper width and height
createPDF();
};
//create pdf
function createPDF() {
getCanvas().then(function (canvas) {
    var imgData = canvas.toDataURL("image/png");
    var imgWidth = 210;
    var pageHeight = 295;
    var imgHeight = canvas.height * imgWidth / canvas.width;
    var heightLeft = imgHeight;

    var doc = new jsPDF('p', 'mm');
    var position = 0;

    doc.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        doc.addPage();
        doc.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
    }
    doc.save('file.pdf');
    $scope.form.width($scope.cache_width);
    $('#JSFiddle .dslamport-info-report').remove();
    $('div.tempDiv').remove();
    $('div.col-md-6').removeClass('col-md-offset-1');
    $('.showAboutBox').hide();

});
}

// create canvas object
function getCanvas() {
$('.showAboutBox').show();
$('#JSFiddle').prepend($('div.panel-body .dslamport-info-report').clone());
$('#JSFiddle').prepend('<div class="tempDiv"> <br/> <br/> <h3>DSLAM Port Status Report<span class="showDate pull-right"></span><h3><div>');
$scope.form.find('#oper-status').before('<div class="tempDiv" style="margin-top:80px;"></div>');
$scope.form.find('#port-snr').before('<div class="tempDiv" style="margin-top:340px"></div>')
$scope.form.find('#port-snr').after('<div class="tempDiv" style="clear:both"></div>')
$scope.form.find('#port-snr').addClass('col-md-offset-1');
$scope.form.find('#port-tx').before('<div class="tempDiv" style="margin-top:120px"></div>')
$scope.form.find('#port-tx').after('<div class="tempDiv" style="clear:both"></div>')
$scope.form.find('#port-tx').addClass('col-md-offset-1');
$scope.form.find('#port-attenuation').before('<div class="tempDiv" style="margin-top:260px"></div>')
$scope.form.find('#port-attenuation').after('<div class="tempDiv" style="clear:both"></div>')
$scope.form.find('#port-attenuation').addClass('col-md-offset-1');
$scope.form.find('#port-attainable-rate').before('<div class="tempDiv" style="margin-top:120px"></div>')
$scope.form.find('#port-attainable-rate').after('<div class="tempDiv" style="clear:both"></div>')
$scope.form.find('#port-attainable-rate').addClass('col-md-offset-1');
$('.showDate').text(new Date().toDateString());
$scope.form.width($scope.a4[0]);
return html2canvas($scope.form, {
    imageTimeout: 2000,
    removeContainer: true
});
}

//End Block Print All Chart

$scope.port_pvc = {
'vpi' : 0,
'vci' : 35,
'profile' : 'DEFVAL',
'mux' : 'llc',
'vlan_id': 1,
'priority' : 0
};
$scope.run_command_loader = false;
$scope.show_detail = false ;
$scope.showDetailes = function(){
$scope.show_detail = !$scope.show_detail ;
}
$scope.run_command = function () {
//load_report();

console.log('run_command');
$scope.command = $scope.selected_command_type.command.name ;
console.log($scope.command);
if ($scope.command != '' ) {

    if($scope.command == 'change admin status'){
        $scope.run_command_loader = true;

        var status_admin = $scope.dslamport.admin_status;
        if(status_admin == 'UNLOCK')
        {
            var lock_status = 'LOCK';
        }
        else {
            var lock_status = 'UNLOCK';
        }
        var params = {
           "type": "dslamport",
           "is_queue": false,
           'dslam_id' : $scope.dslam_id ,
           "admin_status": lock_status,
           "port_conditions" :{
              "slot_number": parseInt($scope.slot_number),
              "port_number" :  parseInt($scope.port_number),
          }


      }
  }
  else if($scope.command == 'change lineprofile port'){
    if($scope.selected_command_type.line_profile != undefined && $scope.selected_command_type.line_profile != null)
    {
        $scope.run_command_loader = true;
        var params = {
         "type": "dslamport",
         "is_queue": false,
         'dslam_id' : $scope.dslam_id ,
         "new_lineprofile": $scope.selected_command_type.line_profile.name,
         "port_conditions" :{
          "slot_number": parseInt($scope.slot_number),
          "port_number" :  parseInt($scope.port_number),
      }
  }
}
else {
$scope.run_command_loader = false;
var notification = alertify.notify('line profile isns valid', 'error', 5, function () {
});
return ;
}

}
else if($scope.command == 'port pvc set'){
if($scope.port_pvc.vpi != '' && $scope.port_pvc.vci != '' && $scope.port_pvc.profile != ''
    && $scope.port_pvc.mux != '' && $scope.port_pvc.vlan_id != '' && $scope.port_pvc.priority != '')
{
    $scope.run_command_loader = true;
    var params = {
     "type": "dslamport",
     "is_queue": false,
     'vpi' : $scope.port_pvc.vpi,
     'vci' : $scope.port_pvc.vci,
     'profile' : $scope.port_pvc.profile,
     'mux' : $scope.port_pvc.mux,
     'vlan_id': $scope.port_pvc.vlan_id,
     'dslam_id' : $scope.dslam_id ,
     'priority' : $scope.port_pvc.priority,
     "port_conditions" :{
      "slot_number": parseInt($scope.slot_number),
      "port_number" :  parseInt($scope.port_number),
  }
}
}
else {
$scope.run_command_loader = false;
var notification = alertify.notify('Field isnt Completed', 'error', 5, function () {
});
return ;
}
}
else if($scope.command == 'uplink pvc set'){
$scope.run_command_loader = true;
if($scope.selected_command_type.port_vpi != '' && $scope.selected_command_type.port_vci != '' &&
    $scope.selected_command_type.wan_slot_number != '' && $scope.selected_command_type.wan_port_number != ''
    && $scope.selected_command_type.wan_vpi != '' && $scope.selected_command_type.wan_vci != '')
{
    var params = {
        "type": "dslamport",
        "is_queue": false,
        'port_vpi' : $scope.selected_command_type.port_vpi,
        'port_vci' : $scope.selected_command_type.port_vci,

        'wan_slot_number' : $scope.selected_command_type.wan_slot_number,
        'wan_port_number' : $scope.selected_command_type.wan_port_number,
        'wan_vpi' : $scope.selected_command_type.wan_vpi,
        'wan_vci' : $scope.selected_command_type.wan_vci,
        "port_conditions" :{
          "slot_number": parseInt($scope.slot_number),
          "port_number" :  parseInt($scope.port_number),
      }

  }
}
else {
$scope.run_command_loader = false;
var notification = alertify.notify('Field isnt Completed', 'error', 5, function () {
});
return ;
}
}
else if($scope.command == 'show performance'){
if($scope.selected_command_type.performance_option != '' ){
    $scope.run_command_loader = true;
    var params = {
        "type": "dslamport",
        "is_queue": false,
        'dslam_id' : $scope.dslam_id ,
        'time_elapsed' : $scope.selected_command_type.performance_option,
        "port_conditions" :{
          "slot_number": parseInt($scope.slot_number),
          "port_number" :  parseInt($scope.port_number),
      }
  }
}
else {
$scope.run_command_loader = false;
var notification = alertify.notify('Field isnt Completed', 'error', 5, function () {
});
return ;
}
}
else if($scope.command == 'profile adsl set'){
if($scope.selected_command_type.profile_name && $scope.selected_command_type.us_mx_rate && $scope.selected_command_type.ds_mx_rate){
    $scope.run_command_loader = true;
    var params = {
        "type": "dslamport",
        "is_queue": false,
        'dslam_id' : $scope.dslam_id ,
        'profile' : $scope.selected_command_type.profile_name ,
        'us-max-rate' : $scope.selected_command_type.us_mx_rate ,
        'ds-max-rate' : $scope.selected_command_type.ds_mx_rate ,
        "port_conditions" :{
            "slot_number": parseInt($scope.slot_number),
            "port_number" :  parseInt($scope.port_number),
        }
    }
}
else{
    $scope.run_command_loader = false;
    var notification = alertify.notify('Fields isnt Completed', 'error', 5, function () {
    });
    return ;
}
}




else if($scope.command == 'uplink pvc set'){
if($scope.selected_command_type.uplink_vpi != '' && $scope.selected_command_type.uplink_vci != '' ){
    $scope.run_command_loader = true;
    var params = {
        "type": "dslamport",
        "is_queue": false,
        'dslam_id' : $scope.dslam_id ,

        'uplink_vci' : $scope.selected_command_type.uplink_vci ,
        'uplink_vpi' : $scope.selected_command_type.uplink_vpi,
        "port_conditions" :{
          "slot_number": parseInt($scope.slot_number),
          "port_number" :  parseInt($scope.port_number),
      }
  }
}
else{
$scope.run_command_loader = false;
var notification = alertify.notify('Fields isnt Completed', 'error', 5, function () {
});
return ;
}
}



else if($scope.command == 'profile adsl delete'){
if($scope.selected_command_type.profile_name_delete ){
    $scope.run_command_loader = true;
    var params = {
        "type": "dslamport",
        "is_queue": false,
        'profile' : $scope.selected_command_type.profile_name_delete ,
        'dslam_id' : $scope.dslam_id ,
        "port_conditions" :{
          "slot_number": parseInt($scope.slot_number),
          "port_number" :  parseInt($scope.port_number),
      }
  }
}
else{
$scope.run_command_loader = false;
var notification = alertify.notify('Fields isnt Completed', 'error', 5, function () {
});
return;
}
}
else if($scope.command == 'acl maccount set'){
console.log($scope.acl.vpi  , $scope.acl.vci , $scope.acl.count);

if( $scope.acl.vpi === ''  || $scope.acl.vci === ''  ||
    $scope.acl.count ===  ''    ){
    console.log($scope.acl.vpi  , $scope.acl.vci , $scope.acl.count);
$scope.run_command_loader = false;
var notification = alertify.notify('Fields isnt Completed', 'error', 5, function () {
});
return;
}

else{

$scope.run_command_loader = true;
var params = {
    "type": "dslamport",
    "is_queue": false,
    'vpi' : $scope.acl.vpi ,
    'vci' : $scope.acl.vci ,
    'count' : $scope.acl.count ,
    'dslam_id' : $scope.dslam_id ,
    "port_conditions" :{
        "slot_number": parseInt($scope.slot_number),
        "port_number" :  parseInt($scope.port_number),
    }
}
}

}
else if( $scope.command == 'add to vlan' ) {

if( $scope.selected_vlan != '' && $scope.selected_vlan !== 'undefined' && $scope.selected_vlan !== undefined
    && $scope.selected_vlan.text != '' && $scope.selected_vlan.id != '')
{
    $scope.run_command_loader = true;
    var params = {

        "type": "dslamport",
        "is_queue": false,
        "vlan_id": $scope.selected_vlan.text,
        "vid": $scope.selected_vlan.id,
        'dslam_id' : $scope.dslam_id ,
        "port_conditions" :{
          "slot_number": parseInt($scope.slot_number),
          "port_number" :  parseInt($scope.port_number),
      }
  }
}
else{
$scope.run_command_loader = false;
var notification = alertify.notify('Fields isnt Completed', 'error', 5, function () {
});
return;
}
}
else if( ($scope.command != 'delete from vlan' &&  $scope.command != 'add to vlan') || $scope.command == 'uplink pvc delete' || $scope.command == 'uplink pvc show')
{
$scope.run_command_loader = true;
var params = {
    "type": "dslamport",
    "is_queue": false,
    'dslam_id' : $scope.dslam_id ,
    "port_conditions" :{
        "slot_number": parseInt($scope.slot_number),
        "port_number" :  parseInt($scope.port_number),
    }
}
}




fetchResult.fetch_result({
method: 'post',
data: {
    "dslam_id": $scope.dslam.id,
    "params": params,
    "command": $scope.command
},
url: ip + 'api/v1/dslamport/command/'
}).then(function (result) {
$scope.run_command_loader = false;
$scope.getCommandResult();
if(result.status <400){
    var notification = alertify.notify("Done", 'success', 5, function () {

    });
}
else{
    var notification = alertify.notify(result.statusText, 'error', 5, function () {

    });


}
//load_report();
//$scope.getDslamDetaile();

}, function (err) {
$scope.run_command_loader = false;
//$scope.getCommandResult();

});
}
else {
var notification = alertify.notify('Command Type is empty', 'error', 5, function () {
});
}
};


// $scope.findCommand = function (selectedCommandId) {
// $scope.command = '';
// angular.forEach($scope.commands, function (item) {
//     if (item.id == selectedCommandId) {
//         $scope.command = item.text;
//     }
// });
// };

fetchResult.fetch_result({
method: 'GET',
url: ip + 'api/v1/dslam/' + $scope.dslam_id+'/'
}).then(function (result) {
$scope.dslam = result.data;
}, function (err) {
});

$(".popovers").popover({
html: true
});

$scope.reset_admin_status = function () {
fetchResult.fetch_result({
    method: 'POST',
    url: ip + 'api/v1/dslamport/reset-admin-status/',
    data: {"dslam_id": $scope.dslam_id, "port_id": $scope.port_id}
}).then(function (result) {
    console.log('reset_admin_status' , result);
}, function (err) {
});
}

// $scope.showDSLAMReport = function () {
//     window.location = "#/dslam/" + $scope.dslam_id + "/report"
// }
$scope.getCommandResult();



$scope.DrawLiveChart = function(){
Highcharts.setOptions({
                        // This is for all plots, change Date axis to local timezone
                        global: {
                            useUTC: false
                        }
                    });

$timeout(function () {

    $scope.atten_change = Highcharts.chart('atten-change', {
        chart: {
            zoomType: 'x',
            height: 370,
          //  width : 300 ,
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
            text: 'Port Attenuation Change',
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
        format: '{value} dB',
        style: {
            color: Highcharts.getOptions().colors[0]
        }
    },
},
       { // Secondary yAxis
           title: {
            text: 'Port Attenuation Change',
            style: {
                color: Highcharts.getOptions().colors[0]
            }
        },
        labels: {
            format: '{value} dB',
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
      name: 'Upstream', //$scope.names[i] + ' ' + 'tx',
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
        var d = new Date();//Date.parse("Month day, year");
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
    name: 'DownStream', //$scope.names[i] + ' ' + 'rx',
    color:'red' ,
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
}



],
func: function (chart) {
    $timeout(function () {
        chart.reflow();
    }, 1000);
}
});
}, 1000);
$scope.DrawRateChangeChart = function(){
Highcharts.setOptions({
                        // This is for all plots, change Date axis to local timezone
                        global: {
                            useUTC: false
                        }
                    });

$timeout(function () {

    $scope.rate_change = Highcharts.chart('rate-change', {
        chart: {
            zoomType: 'x',
            height: 370,
          //  width : 300 ,
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
            text: 'Port Attainable Rate Change',
            align: 'left'
        },

        xAxis: {
            type: 'datetime' //,
        },yAxis: [{
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
            format: '{value} KB/s',
            style: {
                color: Highcharts.getOptions().colors[0]
            }
        },
    },
             { // Secondary yAxis
                 title: {
                     text: 'Port Attainable Rate Change',
                     style: {
                         color: Highcharts.getOptions().colors[0]
                     }
                 },
                 labels: {
                    format: '{value} KB/s',
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
              name: 'Upstream', //$scope.names[i] + ' ' + 'tx',
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
                                var d = new Date();//Date.parse("Month day, year");
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
                        name: 'DownStream', //$scope.names[i] + ' ' + 'rx',
                        color:'red',
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
$scope.PortSnrChange = function(){
Highcharts.setOptions({
                        // This is for all plots, change Date axis to local timezone
                        global: {
                            useUTC: false
                        }
                    });

$timeout(function () {

    $scope.snr_change = Highcharts.chart('snr-change', {
        chart: {
            zoomType: 'x',
            height: 370,
          //  width : 300 ,
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
            text: 'Port Snr Change',
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
                format: '{value} dB',
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
        },
               { // Secondary yAxis
                   title: {
                    text: 'Port SNR Change',
                    style: {
                        color: Highcharts.getOptions().colors[0]
                    }
                },
                labels: {
                    format: '{value} KB/s',
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
                name: 'Upstream', //$scope.names[i] + ' ' + 'tx',
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
                            var d = new Date();//Date.parse("Month day, year");
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
                    name: 'DownStream', //$scope.names[i] + ' ' + 'rx',
                    color:'red',
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
$scope.PortTxRate = function(){
Highcharts.setOptions({
                        // This is for all plots, change Date axis to local timezone
                        global: {
                            useUTC: false
                        }
                    });

$timeout(function () {

    $scope.tx_rate = Highcharts.chart('tx-rate', {
        chart: {
            zoomType: 'x',
            height: 370,
          //  width : 300 ,
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
            text: 'Port Tx Rate',
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
                format: '{value} KB/s',
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
        },
                { // Secondary yAxis
                  title: {
                    text: 'Port Tx Rate',
                    style: {
                        color: Highcharts.getOptions().colors[0]
                    }
                },
                labels: {
                    format: '{value} KB/s',
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
                name: 'Upstream', //$scope.names[i] + ' ' + 'tx',
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
                             var d = new Date();//Date.parse("Month day, year");
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
                    name: 'DownStream', //$scope.names[i] + ' ' + 'rx',
                    color:'red',
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
$scope.AveTraffic = function(){
Highcharts.setOptions({
                        // This is for all plots, change Date axis to local timezone
                        global: {
                            useUTC: false
                        }
                    });

$timeout(function () {

    $scope.ave_traffic = Highcharts.chart('ave-traffic', {
        chart: {
            zoomType: 'x',
          //  height: 300,
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
                         //return  formatBytes(this.y) ;
                         return '123123123'
                     }
                 },
                 data: (function () {
                        //  var d = new Date();//Date.parse("Month day, year");
                        var time = new Date().getTime();
                        var data = [],i;
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
                    var data = [], i;
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
    $scope.DrawRateChangeChart();
    $scope.PortSnrChange();
    $scope.PortTxRate();
    $scope.AveTraffic();

    $scope.first_time = false;
}
if($scope.show_chart ){



    $timeout(function(){
        $scope.rout_location = $location.path();
        $scope.ws = ngSocket('ws://5.202.129.160:2083/ws/');
        $scope.ws.send('{"action": "port_status", "params": {"port":{"port_index":' + $scope.dslamport.port_index + ',"port_number":' + $scope.port_number + ',"slot_number":' + $scope.slot_number + ' }}, "dslam_id":'+ $scope.dslam_id + '}')

        $scope.ws.onMessage(function (message) {
         if($location.path() == $scope.rout_location){
            $scope.socket_count = $scope.socket_count+1;
            var data = angular.fromJson(message.data);
            data = angular.fromJson(data);
            console.log(data);


            var d = new Date();
            var year = d.getFullYear();
            var month = d.getMonth();
            var day = d.getDay();

            var x2 = data.time;

            var time = x2.split(':');

            var date = new Date(year,month,day,time[0],time[1],time[2]);
var x = d.getTime(); //date.getTime();


var y = parseInt(data['ADSL_UPSTREAM_ATTEN']);
$scope.atten_change.series[0].addPoint([x, y], false, true);
var y1 = parseInt(data['ADSL_DOWNSTREAM_ATTEN']);


$scope.atten_change.series[1].addPoint([x, y1], true, true);
$scope.rate_change.series[0].addPoint([x, parseInt(data['ADSL_UPSTREAM_ATT_RATE']) ], false, true);
$scope.rate_change.series[1].addPoint([x, parseInt(data['ADSL_DOWNSTREAM_ATT_RATE']) ], true, true);

$scope.snr_change.series[0].addPoint([x, parseInt(data['ADSL_UPSTREAM_SNR']) ], false, true);
$scope.snr_change.series[1].addPoint([x, parseInt(data['ADSL_DOWNSTREAM_SNR']) ], true, true);

$scope.tx_rate.series[0].addPoint([x, parseInt(data['ADSL_CURR_UPSTREAM_RATE']) ], false, true);
$scope.tx_rate.series[1].addPoint([x, parseInt(data['ADSL_CURR_DOWNSTREAM_RATE']) ], true, true);

$scope.ave_traffic.series[0].addPoint([x, parseInt(data['INCOMING_TRAFFIC_AVERAGE_RATE']) ], false, true);
$scope.ave_traffic.series[1].addPoint([x, parseInt(data['OUTGOING_TRAFFIC_AVERAGE_RATE']) ], true, true);

$scope.dslamport.admin_status  = data['PORT_ADMIN_STATUS'] ;
$scope.dslamport.oper_status = data['PORT_OPER_STATUS'];


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

$scope.getPortswithSameLineProfile = function(){
   fetchResult.fetch_result({
    method: 'GET',
    url: ip + 'api/v1/dslam-port/' ,
    params :{
        page : 1,
        page_size : 25,
        search_line_profile: $scope.dslamport.line_profile
    }
}).then(function (result) {
    console.log(result);
    $scope.same_line_profile = result.data.results;
    console.log($scope.same_line_profile);
}, function (err) {
}
);


}





});
