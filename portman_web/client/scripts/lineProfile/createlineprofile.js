angular.module('portman.addlineprofile', ['myModule','ui.grid', 'ui.grid.pagination', 'ui.grid.edit', 'ui.grid.cellNav', 'ui.grid.resizeColumns', 'ui.grid.autoResize'  ])
.config(function ($stateProvider) {
	$stateProvider
	.state('addlineprofile', {
		url: '/addlineprofile',
		views: {
			'content': {
				templateUrl: 'templates/lineProfile/create-line-profile.html',
        
				controller: 'addLineProfileController'
			}
		}
	});
})
.controller('addLineProfileController', function ($scope, fetchResult ,$http, ip , $timeout ){
 $scope.new_line_profile = {};
 $scope.new_line_profile.set_snr_margin = 'false' ;
 $scope.new_line_profile.set_parameters_rate = 'true';
 $scope.new_line_profile.set_interleaved_delay =  'false' ;
 $scope.new_line_profile.channel_mode = 'interleaved';
 $scope.new_line_profile.type = 'zyxel';
 $scope.new_line_profile.ds_transmit_rate_adaptation = 'startup';
 $scope.createLineProfile = function(){
  console.log($scope.new_line_profile);
  console.log($scope.new_line_profile.template_type);
  if($scope.new_line_profile.template_type === undefined || $scope.new_line_profile.template_type== 'undefined')
  {
    $scope.new_line_profile.template_type = 'adsl 2+';
  }
   fetchResult.fetch_result({
    method: "POST",
    url: ip + 'api/v1/lineprofile/',
    data:{
    
     
     "ds_max_rate": $scope.new_line_profile.ds_max_rate,
     "name": $scope.new_line_profile.name,
     "channel_mode" : $scope.new_line_profile.channel_mode,
     "ds_snr_margin" : $scope.new_line_profile.ds_snr_margin,
     "max_ds_interleaved" : $scope.new_line_profile.max_ds_interleaved,
     "max_us_interleaved" : $scope.new_line_profile.max_us_interleaved,
     "max_us_transmit_rate" : $scope.new_line_profile.max_us_transmit_rate,
     "max_ds_transmit_rate" : $scope.new_line_profile.max_ds_transmit_rate,
     "min_ds_transmit_rate" : $scope.new_line_profile.min_ds_transmit_rate,
     "min_us_transmit_rate" : $scope.new_line_profile.min_us_transmit_rate,
     "us_snr_margin" : $scope.new_line_profile.us_snr_margin,
     'dslam_type' : $scope.new_line_profile.type ,
     "template_type": $scope.new_line_profile.template_type ,

      //"us_max_rate": $scope.new_line_profile.us_max_rate ,
      "extra_settings_info" : [
        {'key':'max_us_snr_margin' ,  'value' : $scope.new_line_profile.max_us_snr_margin
               }  ,
             {'key' :'min_us_snr_margin' , 'value' : $scope.new_line_profile.min_us_snr_margin },
              { 'key' : 'max_ds_snr_margin' , 'value' : $scope.new_line_profile.max_ds_snr_margin},
             { 'key' :  'min_ds_snr_margin' , 'value' : $scope.new_line_profile.min_ds_snr_margin},
             { 'key' : 'dsra' ,'value' : $scope.new_line_profile.dsra} , 
              { 'key' :'dsra_us_margin' ,'value' : $scope.new_line_profile.dsra_us_margin} ,
             { 'key' : 'dsra_ds_margin' ,'value' : $scope.new_line_profile.dsra_ds_margin },
             { 'key' : 'usra' ,'value' : $scope.new_line_profile.usra} , 
              { 'key' :'usra_us_margin' , 'value' : $scope.new_line_profile.usra_us_margin },
             { 'key' : 'usra_ds_margin' , 'value' : $scope.new_line_profile.usra_ds_margin },
              { 'key' :'ds_transmit_rate_adaptation' , 'value' : $scope.new_line_profile.ds_transmit_rate_adaptation },
             { 'key' : 'adapt_mode' ,'value' : $scope.new_line_profile.adapt_mode }, 


        ]
  
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

      $scope.logkon = function(){
       console.log($scope.new_line_profile.template_type);
     }

     fetchResult.fetch_result({
      method: 'GET',
      url: ip + 'api/v1/dslam/dslam-type/'
    }).then(function (result) {
      console.log(result.data);
      $scope.vendor_list = result.data;
    }, function (err) {
    }
    );

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


  })
