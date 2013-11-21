'use strict';

/* Filters */

var smartFilters = angular.module('smartFilters', [])
smartFilters.filter('checkmark', function() {
  return function(input) {
    
    if(input == 10){
    	return 'delete';
    }else{
    	return 'detail';
    }
  };
});
smartFilters.filter('btntype', function() {
  return function(input) {
    
    if(input == 10){
    	return 'btn-danger';
    }else{
    	return 'btn-info';
    }
  };
});

smartFilters.filter('more', function(){
  return function(count){
    if(count > 0){
	return '+';
    }else{
	return '';
    }
  }

});
smartFilters.filter('role', function(){
  return function(rolenumber){
    if(rolenumber ==10){
	return '(Owner)';
    }else if(rolenumber ==9){
	return '(Admin)';
    }else{
	return '';
    }
  }

});
smartFilters.filter('endsession', function(){
  return function(input){
    if(input ==1){
	return '(session ends here)';
    }else{
	return '';
    }
  }

});
