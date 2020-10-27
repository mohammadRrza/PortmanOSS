angular.module('portman.bukht', ['myModule'])
.config(function ($stateProvider) {
    $stateProvider
    .state('bukht', {
        url: '/bukht/:telecom_id',
        views: {
            'content': {
                templateUrl: 'templates/mdf/bukht.html',
                controller: 'BukhtController'
            }
        }
    });
})
.controller('BukhtController', function ($scope, fetchResult, $stateParams, ip , $http) {
    $scope.telecom_id = $stateParams.telecom_id;

   // fetchResult.loadFile('global/plugins/select2/css/select2.min.css');
  //  fetchResult.loadFile('global/plugins/select2/js/select2.full.min.js', function () {

  //  });

    $scope.loadTelecomCenter = function () {
        fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/telecom-center/' + $scope.telecom_id + '/',
        }).then(function (result) {
            $scope.TelecomInfo = result.data;
        }, function (err) {

        });
    };

    $scope.showDSLAM = function (DSLAM_id) {
        var selected = $filter('filter')($scope.DSLAMLists, {id: DSLAM_id}, true);
        return (DSLAM_id !== null && selected.length) ? selected[0] : '';
    };

    $scope.loadDSLAMs = function () {
        fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/dslam/?search_telecom=' + $scope.telecom_id + '&page_size=1000',
        }).then(function (result) {
            $scope.DSLAMLists = result.data.results;
        }, function (err) {

        });
    };

    $scope.loadTerminals = function () {
        fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/terminal/',
        }).then(function (result) {
            $scope.TerminalsList = result.data;
        }, function (err) {

        });
    };

    $scope.loadMDFs = function () {
        fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/telecom-center/mdf/?telecom_id=' + $scope.telecom_id,
        }).then(function (result) {
            console.log(result.data);
            $scope.MDFLists = result.data;

        }, function (err) {

        });
    };
    $scope.TerminalName = function (model)
    {
        if (model)
            return model.name;
        return '';
    };

    $scope.mdf = [];
    $scope.mdf.floor_counting_status = 'STANDARD' ;
    $scope.mdf.connection_counting_status = 'STANDARD' ;
    $scope.mdf.connection_start = 1 ;
    $scope.mdf.status_of_port = 'FREE' ;


//     $scope.loadConfig = function(){

//        fetchResult.fetch_result({
//         method: 'GET',
//         url: ip + 'api/v1/telecom-center/mdf/config/?telecom_id=' + $scope.telecom_id,
//     }).then(function (result) {

//         $scope.config_tab_data = angular.fromJson(result.data) ;

//     }, function (err) {

//     });
// }
// $scope.loadConfig();

$scope.editConfigData = function(id ,index, start , status , port){

   fetchResult.fetch_result({
    method: 'PUT',
    url: ip + 'api/v1/telecom-center/mdf/config/' + id + '/',
    data : {

        start_of_port: start,
        counting_status_port : status,
        status_of_port : port
    }

}).then(function (result) {
 //$scope.loadConfig();
 if(parseInt (result.status) < 400)
 {
    var notification = alertify.notify('Done', 'success', 5, function () {
    });}
    else{
       var notification = alertify.notify(result.statusText, 'error', 5, function () {
       });
   }

}, function (err) {

});
}




$scope.TelecomMDFDSLAM = {
    pageNumber: 1,
    pageSize: 25,
    numPerPageOpt: [25, 50, 100, 500, 1000, 'All']
};



$scope.loadMDFDSLAMs = function (telecom_mdf_id) {
    $scope.TelecomMDFDSLAM.results = [];
    $scope.activeBukhtTab = 0;

    if (telecom_mdf_id === undefined)
        telecom_mdf_id = '';

    fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/mdfdslam/?search_telecom=' + $scope.telecom_id + '&search_telecom_mdf=' + telecom_mdf_id,
        params: {
            page: $scope.TelecomMDFDSLAM.pageNumber,
            page_size: ($scope.TelecomMDFDSLAM.pageSize == 'All' ? 'max' : $scope.TelecomMDFDSLAM.pageSize),
        }
    }).then(function (result) {
        $scope.TelecomMDFDSLAM.totalItems = result.data.count;

        $scope.TelecomMDFDSLAM.results = result.data.results;
        console.log(result.data.results);
    }, function (err) {

    });
};

$scope.updateBukht = function(id , status){

    fetchResult.fetch_result({
        method: 'PUT',
        url: ip + 'api/v1/mdfdslam/' + id + '/',
        data: {
            status : status
        }
    }).then(function (result) {
        $scope.loadMDFDSLAMs();
        if(parseInt(result.status) < 400 )
        {
          var notification = alertify.notify('Done', 'success', 5, function () {

          }); }
          else{
           var notification = alertify.notify(result.statusText, 'error', 5, function () {

           });
       }
   }, function (err) {

   });
}
$scope.show_mdf_tab = false;
$scope.createMDFDSLAM = function (wasted)
{
    if(wasted == 'y'){
        $scope.recal_waste = true ;
    }
    else{
        $scope.recal_waste = false ;
    }
    console.log( $scope.telecom_id);
    $scope.show_mdf_tab = true;
    fetchResult.fetch_result({
        method: 'POST',
        url: ip + 'api/v1/mdfdslam/ ',
        data: {
            "telecom_center_id": $scope.telecom_id,
            "calc_faulty_port" :  $scope.recal_waste
        }
    }).then(function (result) {
        $scope.show_mdf_tab = false;
        $scope.loadMDFDSLAMs();
        $scope.activeTab = 0;
        if(parseInt(result.status) < 400 )
        {
          var notification = alertify.notify('Done', 'success', 5, function () {

          }); }
          else{
           var notification = alertify.notify(result.statusText, 'error', 5, function () {

           });
       }
                //         var notification = alertify.notify('Done', 'success', 5, function () {
                // });
            }, function (err) {
               var notification = alertify.notify('Error', 'error', 5, function () {
               });
           });
};


$scope.addMDF = function ()
{
    if ($scope.mdf.id)
    {
        fetchResult.fetch_result({
            method: 'PUT',
            url: ip + 'api/v1/telecom-center/mdf/' + $scope.mdf.id + '/',
            data: {
                "id": $scope.mdf.id,
                "telecom_center": $scope.telecom_id,
                "row_number": $scope.mdf.row_number,
                "terminal": $scope.mdf.terminal.id,
                "floor_count": $scope.mdf.floor_count,
                "floor_start": $scope.mdf.floor_start,
                "connection_count": $scope.mdf.connection_count,
                "connection_start": $scope.mdf.connection_start,
                "floor_counting_status" : $scope.mdf.floor_counting_status,
                'priority' : $scope.mdf.priority ,
                'connection_counting_status' : $scope.mdf.connection_counting_status ,
                'status_of_port' : $scope.mdf.status_of_port,
                'reseller' : $scope.mdf.reseller_detail ? $scope.mdf.reseller_detail.id : $scope.mdf.reseller_detail
            }
        }).then(function (result) {
            $scope.loadMDFs();

          //  $scope.loadConfig();
            if(parseInt(result.status) < 400 )
            {
                $scope.activeTab = 1;
                var notification = alertify.notify('Done', 'success', 5, function () {
                });

            }
            else{
                var notification = alertify.notify(result.statusText, 'error', 5, function () {
                });
            }

        }, function (err) {
           var notification = alertify.notify('Error', 'error', 5, function () {
           });
       });
    }
    else
    {
        fetchResult.fetch_result({
            method: 'POST',
            url: ip + 'api/v1/telecom-center/mdf/',
            data: {
                "telecom_center": $scope.telecom_id,
                "row_number": $scope.mdf.row_number,
                "terminal": $scope.mdf.terminal.id,
                "floor_count": $scope.mdf.floor_count,
                "floor_start": $scope.mdf.floor_start,
                "connection_count": $scope.mdf.connection_count,
                "connection_start": $scope.mdf.connection_start,
                "floor_counting_status" : $scope.mdf.floor_counting_status,
                'priority' : $scope.mdf.priority ,
                'port_counting_status' : $scope.mdf.port_counting_status ,
                'status_of_port' : $scope.mdf.status_of_port,
                'reseller' : $scope.mdf.reseller_detail ? $scope.mdf.reseller_detail.id : $scope.mdf.reseller_detail
            }
        }).then(function (result) {
            $scope.loadMDFs();

          //  $scope.loadConfig();
            if(parseInt(result.status) < 400 ){
                $scope.activeTab = 1;
                var notification = alertify.notify('Done', 'success', 5, function () {
                });
            }
            else{
                var notification = alertify.notify(result.statusText, 'error', 5, function () {
                });
            }
        }, function (err) {
           var notification = alertify.notify('Error', 'error', 5, function () {
           });

       });
    }
    $scope.mdf = [];
};

$scope.editMDF = function (mdf)
{
    $scope.activeTab = 2;
    console.log(mdf);
    $scope.mdf = mdf;
    $scope.mdf.terminal = mdf.terminal_info;
};
$scope.cancelBukhtEdit = function(){
    $scope.mdf = [];
    $scope.mdf.terminal = null;
}

$scope.removeMDF = function (mdf_id)
{
    fetchResult.fetch_result({
        method: 'DELETE',
        url: ip + 'api/v1/telecom-center/mdf/' + mdf_id + '/',
    }).then(function (result) {
        $scope.loadMDFs();
        //$scope.loadConfig();
        if(parseInt (result.status) < 400)
       {
        var notification = alertify.notify('Done', 'success', 5, function () {
        });}
        else{
         var notification = alertify.notify(result.statusText, 'error', 5, function () {
         });
     }


    }, function (err) {
        var notification = alertify.notify('Error', 'error', 5, function () {
        });

    });


};
 $scope.searchDslamName = function(query){
          return $http({
            method: "GET",
            url: ip + 'api/v1/dslam/',
            params: {
              search_telecom : $scope.telecom_id,
              search_dslam: query,

            }
          }).then(function mySucces(data) {
            if(data.data.results){

              return data.data.results;
            }
            return [];

          });
        }
        $scope.cart_dslam = {};
$scope.AddDslam = function ()
{
    if($scope.cart_dslam.id){
         fetchResult.fetch_result({
        method: 'PUT',
        url: ip + 'api/v1/dslam/cart/' + $scope.cart_dslam.id +'/' ,
        data :{
            'telecom_center' : $scope.telecom_id,
                "dslam": $scope.cart_dslam.dslam.id,
                "priority": $scope.cart_dslam.priority,
                "cart_count": $scope.cart_dslam.cart_count,
                "cart_start": $scope.cart_dslam.cart_start,
                "port_count": $scope.cart_dslam.port_count,
                "port_start": $scope.cart_dslam.port_start,
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
     $scope.getDslam();


    }, function (err) {
        var notification = alertify.notify('Error', 'error', 5, function () {
        });

    });
    }

    else {


    fetchResult.fetch_result({
        method: 'POST',
        url: ip + 'api/v1/dslam/cart/'  ,
        data :{
            'telecom_center' : $scope.telecom_id,
                "dslam": $scope.cart_dslam.dslam.id,
                "priority": $scope.cart_dslam.priority,
                "cart_count": $scope.cart_dslam.cart_count,
                "cart_start": $scope.cart_dslam.cart_start,
                "port_count": $scope.cart_dslam.port_count,
                "port_start": $scope.cart_dslam.port_start,
        }
    }).then(function (result) {

      $scope.cart_dslam.dslam = null
      $scope.cart_dslam.priority = null;
      $scope.cart_dslam.cart_count = null;
      $scope.cart_dslam.cart_start = null ;
      $scope.cart_dslam.port_count = null ;
      $scope.cart_dslam.port_start = null ;
        if(parseInt (result.status) < 400)
       {
        var notification = alertify.notify('Done', 'success', 5, function () {
        });
        $scope.activeTab = 4;
      }
        else{
         var notification = alertify.notify(result.statusText, 'error', 5, function () {
         });
     }
     $scope.getDslam();


    }, function (err) {
        var notification = alertify.notify('Error', 'error', 5, function () {
        });

    });
}


};
$scope.CancelCartEdit =function(){
    $scope.cart_dslam = [];
    $scope.cart_dslam.dslam_info = null;
}
$scope.removeDslamCart = function(id){
    fetchResult.fetch_result({
        method: 'DELETE',
        url: ip + 'api/v1/dslam/cart/' + id ,
    }).then(function (result) {

        if(parseInt (result.status) < 400)
       {
        var notification = alertify.notify('Done', 'success', 5, function () {
        });}
        else{
         var notification = alertify.notify(result.statusText, 'error', 5, function () {
         });
     }
     $scope.getDslam();


    }, function (err) {
        var notification = alertify.notify('Error', 'error', 5, function () {
        });

    });
}

$scope.getDslam = function(){
  console.log($scope.telecom_id);
    fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/dslam/cart/' ,
        params:{
            telecom_center_id : $scope.telecom_id
        }

    }).then(function (result) {

        console.log(result);
        $scope.dslam_port_list = result.data.results ;

    }, function (err) {

    });

}

$scope.getDslam();
$scope.editDslamCart = function(port){
    $scope.activeTab = 3;
    $scope.cart_dslam = [];
    $scope.cart_dslam = port;
    $scope.cart_dslam.dslam = port.dslam_info;
   // $scope.mdf.terminal = mdf.terminal_info;

}


$scope.getReseller = function(query){

    return fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/reseller/',
           params: {
             name : query
           }
    }).then(function (result) {

         if(result.data.results){
            return result.data.results
         }
         return [];

        }, function (err) {
        }
    );

}
$scope.getReseller();
 $scope.loadMDFs();
        $scope.loadDSLAMs();
        $scope.loadTerminals();
        $scope.loadTelecomCenter();
        $scope.loadMDFDSLAMs();



$scope.download_url = ip + 'api/v1/mdfdslam/download/?telecom_center_id=' + $scope.telecom_id ;


});
