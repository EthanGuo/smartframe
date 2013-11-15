'use strict';

/* App Module */

var smartServer = angular.module('smartServer', [
  'ngRoute',
  // 'phonecatAnimations',
  'smartControllers',
   'smartFilters',
   'smartDirectives',
  'smartServices'
]);

smartServer.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/smartserver/index', {
        templateUrl: 'partials/index.html',
        controller: 'IndexCtrl'
      }).
      when('/smartserver/index/:username', {
        templateUrl: 'partials/index.html',
        controller: 'IndexCtrl'
      }).
      when('/smartserver/login', {
        templateUrl: 'partials/login.html',
        controller: 'LoginCtrl'
      }).
      when('/smartserver/signup', {
        templateUrl: 'partials/signup.html',
        controller: 'SignUpCtrl'
      }).
      when('/smartserver/forgetpwd', {
        templateUrl: 'partials/forgetpwd.html',
        controller: 'ForgetPwdCtrl'
      }).
      when('/smartserver/setting/:username', {
        templateUrl: 'partials/setting.html',
        controller: 'SetingCtrl'
      }).
      when('/smartserver/group/:groupid',{
        templateUrl:'partials/group.html',
        controller:'GroupCtrl'
      }).
      when('/smartserver/group/:groupid/:sessionid',{
        templateUrl:'partials/session.html',
        controller:'SessionCtrl'
      }).
      when('/smartserver/group/:groupid/cycle/:cid',{
        templateUrl:'partials/report.html',
        controller:'ReportCtrl'
      }).
      otherwise({
        redirectTo: '/smartserver/index'
      });
  }]);

var host = 'localhost';
