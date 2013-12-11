'use strict';

/* Directives */
var smartDirectives = angular.module('smartDirectives', []);
smartDirectives.directive('fileUpload', function () {
    return {
        scope: true,        //create a new scope
        link: function (scope, el, attrs) {
            el.bind('change', function (event) {
                var files = event.target.files;
                //iterate files since 'multiple' may be specified on the element
                for (var i = 0;i<files.length;i++) {
                    //emit event upward
                    scope.$emit("fileSelected", { file: files[i] });
                }                                       
            });
        }
    };
});
smartDirectives.directive('openDialog', function(){
    return {
	restrict : 'A',
        link: function(scope, elem, attr, ctrl){
	    var dialogId = '#' + attr.openDialog;
	    elem.bind('click', function(e){
		$(dialogId).dialog('open');
	    });
        }
    };

});

smartDirectives.directive('fixhead', function($window){
    return {
	link : function(scope, elem, attr){
	    angular.element($window).bind('scroll',function(){
		if($('#fixHead').offset()){
		var scrollHeight = $("#fixHead").offset().top;
		var thwid = [];
		var ths1 = $('#fixHead').children().children();
		$.each(ths1, function(i, o){
		    thwid[i] = $(this).width();
		});
		var ths2 = $(elem).children().children();
		$.each(ths2, function(i, o){
		    $(this).css('width',thwid[i]+'px');
		    $(this).css('padding','8px');
		});
		if(this.pageYOffset > scrollHeight){
		   $(elem).css('display','block');
		   $(elem).css('background-color','#f9f9f9');
		   $(elem).css('position','fixed');
		   $(elem).css('top','0');
		   $(elem).css('left','40px');
		   $(elem).css('width','975px');
		   $(elem).css('border-bottom','1px solid #DDDDDD');
		}else{
		   $(elem).css('display','none');
		   $(elem).css('position','');
		}
		}
	    });
	}
    }
});
