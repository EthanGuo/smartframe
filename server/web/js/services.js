'use strict';

/* Services */

var smartServices = angular.module('smartServices', []);

smartServices.factory('dialogService',function(){
    return {
	open : function(elementId){
	    $(elementId).dialog('open');
	}
    };
		 
});
