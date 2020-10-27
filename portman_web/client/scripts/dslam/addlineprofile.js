angular.module('portman.addlineprofile', ['myModule'])
.config(function ($stateProvider, $urlRouterProvider) {
    $stateProvider
    .state('add-lineprofile', {
        url: '/dslam/add-lineprofile/:dslam_id',
        views: {
            'content': {
                templateUrl: 'templates/dslam/add-lineprofile.html',
                
                controller: 'AddLineProfileController'
            }
        },

    });
})
.controller('AddLineProfileController', function ($scope, fetchResult, $stateParams, ip) {
    $('#secess_alert').hide('fast');
    $('#error_alert').hide('fast');

    $scope.dslam_id = $stateParams.dslam_id;
    $scope.search_profile_name = "";

    fetchResult.fetch_result({
        method: 'GET',
        url: ip + 'api/v1/dslam/' + $scope.dslam_id+'/'
    }).then(function (result) {
        $scope.dslam_info = result.data;
    }, function (err) {
    });

    var loadData = function () {
        fetchResult.fetch_result({
            method: 'GET',
            url: ip + 'api/v1/dslam/lineprofile/?dslam_id=' + $scope.dslam_id + '&profile_name=' + $scope.search_profile_name
        }).then(function (result) {
            $scope.dslamProfiles = result.data;
        }, function (err) {
        });
    };

    $scope.deleting_profile = function (item) {
        $scope.del_dslam_profiles_item = item;
        $('.delete_box').show('slow');

    };

    $scope.delete_profile = function () {
        fetchResult.fetch_result({
            method: 'delete',
            url: ip + 'api/v1/dslam/lineprofile/' + $scope.del_dslam_profiles_item.id+'/'
        }).then(function (result) {
            var index = $scope.dslamProfiles.indexOf($scope.dslamProfiles);
            $scope.dslamProfiles.splice(index, 1);
            $('.delete_box').hide('slow');
        }, function (err) {
        }
        );
    };

    $scope.add_profile = function () {
        var post_data = {
            "dslam": $scope.dslam_id,
            "command": "profilt adsl set",
            "params": {
                "name": $scope.profile_name,
                "us_max_rate": $scope.us_max_rate,
                "ds_max_rate": $scope.ds_max_rate,
                "is_queue": false
            }
        };
        fetchResult.fetch_result({
            method: 'POST',
            url: ip + 'api/v1/dslam/lineprofile/',
            data: post_data
        }).then(function (result) {
            $('#secess_alert').show('fast');
            setTimeout(function () {
                $('#secess_alert').hide('fast');
            }, 3000);
            $scope.dslamProfiles.push(result.data);
        }, function (err) {
            $('#error_alert').show('fast');
            setTimeout(function () {
                $('#error_alert').hide('fast');
            }, 3000);
        });
    };
    $scope.searchData = function () {
        loadData();
    };
    loadData();
});