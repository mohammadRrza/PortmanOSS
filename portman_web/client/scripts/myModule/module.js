angular.module('myModule',[])
.service('fetchResult',function($http){
    this.fetch_result = function(config){
        //config sample
        //http://5.202.129.160/api/v1/telecom-center/
        
        //{method :'GET' , params:{JSON.stringify() | data:,
        return $http(config)
        .success(function(result){
            return result;
            })
        .error(function(err){
            return err;
            })
        };
    this.checkNullOrEmptyOrUndefined = function (value) {
        return !!value;
    };

    
    this.loadFile = function(url, next){
        var type = url.slice(url.length - 3);
        var head = document.getElementsByTagName('head')[0];
        if (type=='css') {
            var href = document.createElement('link');
            href.href = url;
            href.rel="stylesheet";
            head.appendChild(href);
               
        } else if(type=='.js'){
            var script = document.createElement('script');
            script.src = url;
            script.type="text/javascript";
            head.appendChild(script);

            script.onload = function (){
                next();    
            }
        }
    }
});
