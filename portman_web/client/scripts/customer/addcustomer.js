angular.module('portman.addcustomer', ['myModule'])
.config(function ($stateProvider) {
$stateProvider
.state('add-subscriber', {
    url: '/add-subscriber/:customer_id?',
    views: {
        'content': {
            templateUrl: 'templates/customer/add-customer.html',
            
            controller: 'AddCustomerController'
        }
    },
});
})
.controller('AddCustomerController', function ($scope, fetchResult, $stateParams, ip , $http , $timeout ) {
$('#form-customer').hide();

$scope.btn_text = "Submit";
$scope.city = '';
$scope.new_customer = {};

$scope.getProvince = function(query){
 
    return fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/city/',
        params : {
            city_name : query
        }
    }).then(function (result) {
        if(result.data.results){
            return result.data.results ;}
            return [];
            
        }, function (err) {
        }
        );
}
$scope.getProvince();

fetchResult.loadFile('global/plugins/select2/css/select2.min.css');
fetchResult.loadFile('global/plugins/select2/js/select2.full.min.js', function () {
    fetchResult.fetch_result({
        method: 'GET',
        url: ip  + 'api/v1/city/?parent=all'
    }).then(function (result) {
        $scope.ProvinceList = result.data.results;
        $(".select-province-array").select2({
            data: $scope.ProvinceList
        });
    }, function (err) {
    }
    );
});
$scope.selectPro = function (pro_id) {

    $('#form-customer').show();
    $scope.fetchChildParent(pro_id);
    fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/city/?parent=' + pro_id
    }).then(function (result) {
        $('#form-customer').hide();
        $scope.city =result.data
        $(".show-city").select2({
            data: result.data.results 
        }, function (err) {
        });
    },function () {
        $('#form-customer').hide();
    });}

    // $scope.selectCity = function (city_id) {
    //     $('#form-customer').show();
    //     fetchResult.fetch_result({
    //         method: 'GET',
    //         url: ip + 'api/v1/telecom-center/get_without_paging/?city_id=' + city_id
    //     }).then(function (result) {
    //         $('#form-customer').hide();
    //         $scope.tele = result.data.results
    //         $(".show-tele").select2({
    //             data: result.data
    //         }, function (err) {
    //         });
    //     },function () {
    //         $('#form-customer').hide();
    //     });
    // }
            $scope.selectCity = function (city_id) {
       
      //  $scope.fetchChildParent( $scope.selectedCity0.id);
      console.log(city_id , 'dfgdfgfd');
        return fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/telecom-center/?search_city_id=' + $scope.selectedCity.id,
            params : {
                search_name : $scope.new_customer.telecom_center_id
            }

        }).then(function (result) {
            console.log(result);
            if(result.data.results)
            {
                return result.data.results ;
            }
            return [];
            
           // $scope.tele = result.data
            
        },function () {
           
        });
    }
    $scope.fetchChildParent = function (parent_id) {
      
       return fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/city/?parent=' + parent_id,
            params : {
                city_name : $scope.selectedCity
            }
        }).then(function (result) {
            $scope.show_city = true;
            $scope.loaded_city = result.data.results;
            if(result.data.results)
            {
                return result.data.results
            }
            return [];
            
        }, function (err) {
        }
        );

    };

    

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
                
            }, function (err) {
            }
            );
    }
    $scope.selectPro = function (pro_id) {
        
     return fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/city/?parent=' + pro_id,
        params : {
            city_name : $scope.new_customer.province_id
        }

    }).then(function (result) {
      
      if(result.data){
        return result.data
        
    }
    return [];
    

},function () {
    $('#form-customer').hide();
});}





    $scope.active_port_select = {reseller:'' , vlan:'' , customer:''};
    $scope.port_pvc = {
        'vpi' : 0,
        'vci' : 35,
        'profile' : 'DEFVAL',
        'mux' : 'llc',
        'vlan_id': 1,
        'priority' : 0
    };
    fetchResult.fetch_result({
        url: ip + 'api/v1/reseller/',
    }).then(function (result) {
                $scope.reseller_active_port = result.data.results;//.data;
                
            }, function (err) {
            }
            );
    $scope.SelectReseller= function () {
        url = ip +  'api/v1/vlan/';
        fetchResult.loadFile('global/plugins/select2/js/select2.full.min.js', function () {
            fetchResult.fetch_result({
                url: ip + 'api/v1/reseller/',
            }).then(function (result) {
                    $scope.reseller_active_port = result.data.results;//.data;
                    
                }, function (err) {
                }
                );
            fetchResult.fetch_result({
                method: 'GET',
                url: ip + 'api/v1/vlan/',
                params: {reseller_id: $scope.active_port_select.reseller.id}
            }).then(function (result) {
                $scope.vlan_list = result.data.results ;

            }, function (err) {
            }
            );
        });
        $http.get(ip , $scope.active_port_select.reseller);
    }

    $scope.show_wizard_1 = true;
    $scope.show_wizard_2 = false;
    $scope.step = 1;
    $scope.percent = 25 ;
    $scope.GoToFirstWizard = function () {

        
        $scope.step = 1;
        $scope.percent = 25;
        $scope.show_wizard_1 = true;
        $scope.show_wizard_2 = false;
        
        
    }
    $scope.GoToSecondWizard = function () {

        if($scope.show_wizard_1 === true){
         
            $scope.show_wizard_1 = false;
            $scope.show_wizard_2 = true;
            $scope.step = 2;
            $scope.percent = 50;
            
        };

    };
    

    $scope.showWizard = function(){
      if($scope.new_customer.port_pvc_option){

      }
      else{

      }
  }

  $scope.selectTele = function (tele_id) {
    
   return fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/mdfdslam/get_free_identifier/',
        params:{
            telecom_id: tele_id.id,
            identifier_key : $scope.new_customer.identifier_key
        }

    }).then(function (result) {
        if(result.data)
        {
            return result.data
        }
        return [] ;
        $scope.identifier = result.data
        // $(".show-ide").select2({
        //     data: result.data
        // }, function (err) {

        // });
    },function () {
        
    });
}

$scope.getProvince = function (query) {
    if (query != undefined && query != '') {
        query = query.trim();
        fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/city/?parent=all/&city_name=' + query
        }).then(function (result) {

            return result.data;
        }, function (err) {
        }
        );
    }
};
$scope.getLocation = function(val) {
    return $http.get('//maps.googleapis.com/maps/api/geocode/json', {
        params: {
            address: val,
            sensor: false
        }
    }).then(function(response){
        return response.data.results.map(function(item){
            return item.formatted_address;
        });
    });
};

$scope.NewCustomerFormatLabel = function ($data) {
    if ($data !== undefined) {
        return $data.name;
    }
};

fetchResult.loadFile('global/plugins/select2/css/select2.min.css');
fetchResult.loadFile('global/plugins/select2/js/select2.full.min.js', function () {
    fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/dslam/'
    }).then(function (result) {
        $scope.dslams = result.data.results;
        $(".select-dslam-array").select2({
            data: $scope.dslams
        });
    }, function (err) {
    }
    );
});
$scope.selectDSLAM = function (dslam_id) {
    $scope.dslam_id = dslam_id;
    $scope.fetchPortname(dslam_id);
}
$scope.selectPortname = function (port_id) {
    $scope.portname = $('.select-portname-array').select2('data')[0]['text'];
}

$scope.fetchPortname = function (dslam_id) {

    fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/dslam-port/?dslam=' + dslam_id
    }).then(function (result) {
        if (result.data.results.length > 0) {

            $(".select-portname-array").select2({
                data: result.data.results
            });
        }

    }, function (err) {
    }
    );

}
$scope.fillcustomerInfo = function (id) {
    fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/customer-port/' + id
    }).then(function (result) {
        customer_info = result.data;
        $scope.name = customer_info.name;
        $scope.username = customer_info.user_name;
        $scope.family = customer_info.family;
        $scope.email = customer_info.email;
        $scope.tel = customer_info.tel;
        $scope.mobile = customer_info.mobile;
        $scope.national_code = customer_info.national_code;
        $scope.btn_text = 'Edit';
    }, function (err) {
    });
}
$scope.add_customer = function () {
    if ($scope.dslam != '') {

        $('#selectCommandErr').addClass('hide');
        $scope.use_method = '';
        $scope.post_url = '';
        if (!fetchResult.checkNullOrEmptyOrUndefined($stateParams.customer_id)) {
            $scope.use_method = 'POST';
            $scope.post_url = ip + 'api/v1/customer-port/';
        }
        else {
            $scope.use_method = 'PUT';
            $scope.post_url = ip + 'api/v1/customer-port/' + $stateParams.customer_id + '/';
        }
        var the_vlan_id = null ;
        if($scope.active_port_select.vlan_id)
        {
            the_vlan_id = $scope.active_port_select.vlan_id.id ;
        }
        
        if($scope.active_port_select.reseller !== undefined && $scope.active_port_select.reseller !==''){
            $scope.data_param = {
                province_id: $scope.new_customer.province_id , 
                city_id: $scope.new_customer.city_id , 
                telecom_center_id: $scope.new_customer.telecom_center_id.id ,
                identifier_key: $scope.new_customer.identifier_key ,
                username: $scope.new_customer.username ,
                firstname: $scope.new_customer.family ,
                lastname: $scope.new_customer.name ,
                tel: $scope.new_customer.tel ,
                email: $scope.new_customer.email ,
                national_code: $scope.new_customer.national_code ,
                mobile: $scope.new_customer.mobile ,
                reseller: $scope.active_port_select.reseller.id ,
                    vid_id: the_vlan_id  , //.id ,
                    
                    params : {
                        "type": "dslamport",
                        "is_queue": false,
                        'vpi' : $scope.port_pvc.vpi,
                        'vci' : $scope.port_pvc.vci,
                        'profile' : $scope.port_pvc.profile,
                        'mux' : $scope.port_pvc.mux,
                        'priority' : $scope.port_pvc.priority,
                        
                    }
                    
                }
                send_customer_request();
                
            }
            else{
               $scope.data_param = {
                province_id: $scope.new_customer.province_id , 
                city_id: $scope.new_customer.city_id , 
                telecom_center_id: $scope.new_customer.telecom_center_id.id ,
                identifier_key: $scope.new_customer.identifier_key ,
                username: $scope.new_customer.username ,
                lastname: $scope.new_customer.family ,
                firstname: $scope.new_customer.name ,
                tel: $scope.new_customer.tel ,
                email: $scope.new_customer.email ,
                national_code: $scope.new_customer.national_code ,
                mobile: $scope.new_customer.mobile ,
                reseller: $scope.active_port_select.reseller.id ,
                params : {
                    // "vlan_id": 1 ,
                    "type": "dslamport",
                    "is_queue": false,
                    'vpi' : $scope.port_pvc.vpi,
                    'vci' : $scope.port_pvc.vci,
                    'profile' : $scope.port_pvc.profile,
                    'mux' : $scope.port_pvc.mux,
                    'priority' : $scope.port_pvc.priority,
                }
            }
            send_customer_request();
        }
        
        
    }
   
}
$scope.change_wizard_state= false;
var send_customer_request = function(){
   fetchResult.fetch_result({
    method: $scope.use_method,
    url: $scope.post_url,
    data: $scope.data_param
    
}).then(function (result) {
    $scope.percent = 100 ;

    if(result.status < 400 ){
        $scope.new_customer = '';
        var notification = alertify.notify('Customer Created', 'success', 5, function () {
        });
        $scope.change_wizard_state= true;

        $timeout (function(){
           $scope.new_customer.province_id = '' ;
           $scope.new_customer.city_id = '';
           $scope.new_customer.telecom_center_id ='' ;
           $scope.new_customer.identifier_key = '' ;
           $scope.new_customer.username =  '';
           $scope.new_customer.family = '' ;
           $scope.new_customer.name = '' ;
           $scope.new_customer.tel = '' ;
           $scope.new_customer.email = '' ;
           $scope.new_customer.national_code = '' ;
           $scope.new_customer.mobile = '' ;
           $scope.active_port_select.reseller.id = '';
           $scope.active_port_select.reseller = '' ;
           $scope.show_wizard_1 = true ;
           $scope.show_wizard_2 = false ;       
           $scope.change_wizard_state= false;   
           $scope.percent = 25 ; 
           $scope.step = 1;            

       },3000);

    }
    else{
         angular.forEach(result.data , function(key,value){
             var notification = alertify.notify(key[0], 'error', 5, function () {
        });
        })

        
    }

}, function (err) {
   var notification = alertify.notify('Error', 'error', 5, function () {
   });
});
}

if (fetchResult.checkNullOrEmptyOrUndefined($stateParams.customer_id)) {
$scope.fillcustomerInfo($stateParams.customer_id);
}

$scope.run_port_pvc = function(){

if($scope.active_port_select.vlan_id === undefined){
  var params = {
    "type": "dslamport",
    "is_queue": false,
    'vpi' : $scope.port_pvc.vpi,
    'vci' : $scope.port_pvc.vci,
    'profile' : $scope.port_pvc.profile,
    'mux' : $scope.port_pvc.mux,
    'priority' : $scope.port_pvc.priority,
    "command": 'port pvc set',
    vlan_id : 1,
};
var posted_data = {
    identifier_key : $scope.active_port_select.identifier_key.identifier_key,
    "params": params,
    
};
}
else{
var params = {
    "type": "dslamport",
    "is_queue": false,
    'vpi' : $scope.port_pvc.vpi,
    'vci' : $scope.port_pvc.vci,
    'profile' : $scope.port_pvc.profile,
    'mux' : $scope.port_pvc.mux,
    'priority' : $scope.port_pvc.priority,
    "command": 'port pvc set',
    vlan_id : $scope.active_port_select.vlan_id.vlan_id,
};
var posted_data = {
    identifier_key : $scope.active_port_select.identifier_key.identifier_key,
    vid_id : $scope.active_port_select.vlan_id.id,
    "params": params,
    
};
}
fetchResult.fetch_result({
method: 'post',
url : ip + 'api/v1/customer-port/activeport/',
data: posted_data 

}).then(function (result) {
if(parseInt (result.status) <400 ){
            var notification = alertify.notify('Done', 'success', 5, function () {
     });
        }
     else {
        var notification = alertify.notify(result.statusText, 'error', 5, function () {
     });
     }


}, function (err) {
var notification = alertify.notify('Error', 'error', 5, function () {
});
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
        
        else if ((charCode < 48 || charCode > 57) &&  (charCode < 96 || charCode > 105) && 
    charCode !== 46 &&
    charCode !== 8 &&
    charCode !== 37 &&
    charCode !== 39 && charCode !== 09)
    keyEvent.preventDefault();
    }

});
