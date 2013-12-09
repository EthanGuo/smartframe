'use strict';

/* Controllers */

var smartControllers = angular.module('smartControllers', []);
var apiBaseURL = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ":" + window.location.port : "")+"/smartapi";
//Controller for index

smartControllers.controller('IndexCtrl', ['$scope', '$http','$routeParams',
  function($scope, $http, $routeParams) {

    if(!$.cookie('ticket')){
      window.location = '#/smartserver/login';
    }
    $scope.activeProduct = {}; 
    $("#mytabs a").click(function(e){
        e.preventDefault();
        $(this).tab('show');
        if(e.target.id == 'mysessions'){

  	       $http.get(apiBaseURL+'/account?subc=sessions&appid=02&token='+$.cookie('ticket'))
       	    .success(function(ret){
                if(ret.result == 'ok'){
          	      $scope.sessions = ret.data.usersession;
                }else{
                  alert(ret.msg);
                }
      	   });
        }else if(e.target.id == 'mygroups'){

     	      $http.get(apiBaseURL+'/account?subc=groups&appid=02&token='+$.cookie('ticket'))
      	     .success(function(ret){
                if(ret.result == 'ok'){
                  $scope.groups = ret.data.usergroup;
                }else{
                  alert(ret.msg);
                }
  	        });
        }
    });
 
    $http.get(apiBaseURL+'/account?subc=groups&appid=02&token='+$.cookie('ticket'))
     .success(function(ret){
        if(ret.result == 'ok'){
          $scope.groups = ret.data.usergroup;
        }else{
          window.location = '#/smartserver/login';
        }
        
    });

    $http.get(apiBaseURL+'/account?subc=accountinfo&appid=02&token='+$.cookie('ticket'))
     .success(function(ret){
      if(ret.result == 'ok'){
        $scope.username = ret.data.userinfo.username;
        $scope.isadmin = ret.data.userinfo.admin;
	$.cookie('isadmin', ret.data.userinfo.admin, { expires: 7 });
        if(ret.data.userinfo.avatar.url != undefined){
          $scope.avatar = apiBaseURL + ret.data.userinfo.avatar.url;
        }
        else{
          $scope.avatar = undefined;
        }
      }else{
        window.location = '#/smartserver/login';
      }
    });

    $scope.showProduct = function(index){
	$scope.activeProduct[index] = !$scope.activeProduct[index];
    }

    $scope.productDetail = function(gid, product){
	window.location = '#/smartserver/group/'+gid+'/product/'+product;
    }
    $scope.edit = function(groupid, userrole){
	var r = window.confirm("Are you sure to delete?");
        if(r){
     	   if(userrole == 10){
       	     $http.post(apiBaseURL+'/group/'+groupid,{'subc':'delete','data':{},'token':$.cookie('ticket')}).
       	       success(function(ret){
       	         if(ret.result == 'ok'){
       	             var index;
       	             $.each($scope.groups, function(i, o){
        	       if(o.gid == groupid){
        	         index = i;
        	       }
        	     });
        	     $scope.groups.splice(index, 1); 
        	   }
	       });
	   }else{
	       window.location = '#/smartserver/group/'+groupid;
	     }
	}
    }

    $scope.signout = function(){
      $http.post(apiBaseURL+'/account',{'subc':'logout','data':{},'token':$.cookie('ticket')})
      .success(function(ret){
        $.cookie('ticket', '', { expires: -1 });
	$.cookie('isadmin','', {expires:-1});
        window.location = '#/smartserver/login';
      });
    }

    $scope.create = function(){
      $('.create_group').slideToggle();
    }

    $scope.cancel = function(){
      $('.create_group').slideUp();
    }

    $scope.createGroup = function(){
      var groupname = $scope.newgroup;
      var groupinfo = $scope.groupinfo;
      var data = {'groupname':groupname, 'info':groupinfo,'appid':'02'};
      $http.post(apiBaseURL+'/group',{'subc':'create','data':data, 'token': $.cookie('ticket')})
      .success(function(ret){
        if(ret.result == 'ok'){
	  $scope.newgroup = '';
	  $scope.groupinfo = '';
          var gid = ret.data.gid;
          var newgroup ={"allsession": 0, "groupname": groupname, "gid": gid, 'info':groupinfo, "userrole": 10, "groupowner": $scope.username, "livesession": 0};
          $scope.groups.push(newgroup);
          $('.create_group').slideUp();
        }else{
          alert(ret.msg);
          return;
        }
      });
    }

    $scope.sessionDetail = function(sid, gid, product){
	window.location = "#/smartserver/group/"+gid+'/product/'+product+"/"+sid;
    }

  }]);


//Controller for signup

smartControllers.controller('SignUpCtrl', ['$scope', '$http',
  function($scope, $http) {
    $scope.cancel = function(){
      window.location = '#/smartserver/login';
    }
    $scope.signUp = function(){
      var username = $scope.username;
      var password = $scope.password;
      var email = $scope.email;
      var telephone = $scope.telephone?$scope.telephone:"1";
      var company = $scope.company?$scope.company:"2";
      if(username == undefined || password == undefined || email == undefined){
        alert("Username, Password and Email are required!");
        return false;
      }
      var data = {'username':username,'password':hex_md5(password),'appid':'02',
                  'info':{'email':email,'phonenumber':telephone,'company':company},
                  'baseurl': apiBaseURL};
      $http.post(apiBaseURL+'/accountbasic',{'subc':'register','data':data})
      .success(function(ret){
          if(ret.result == 'ok'){
            alert('Please check your email box to active this account!');
            window.location = '#/smartserver/login';
          }else{
            alert(ret.msg);
          }
      });
    }
  }]);

//Controller for login

smartControllers.controller('LoginCtrl', ['$scope', '$http',
  function($scope, $http) {
    if($.cookie('ticket')){
      window.location = '#/smartserver/index';
    }
    $scope.logIn = function(){

        var username = $scope.username;
        var password = $scope.password; 
        if(username == undefined || password == undefined){
          $('.warnning').show();
          return;
        }
        password = hex_md5(password);
        var data = {'appid':'02', 'username':username, 'password':password};
        $http.post(apiBaseURL+'/accountbasic',{'subc':'login','data':data})
        .success(function(ret){
            if(ret.result == 'ok'){
              $.cookie('ticket', ret.data.token, { expires: 7 });
              window.location = '#/smartserver/index/';
            }else{
              alert(ret.msg);
              return;
            }
        });
    } 

    $scope.checkKeyCode = function($event){
      if($event.keyCode == 13){
        $scope.logIn();
      }
    }

    $scope.signUp = function(){
      window.location = '#/smartserver/signup';
    }

    $scope.forgetPwd = function(){
      window.location = '#/smartserver/forgetpwd';
    }
  }]);

//Controller for forgetpassword

smartControllers.controller('ForgetPwdCtrl', ['$scope', '$http',
  function($scope, $http) {

    $scope.cancel = function(){
      window.location = '#/smartserver/login';
    }

    $scope.checkemail = function(){
      var data = {'email':$scope.email, 'baseurl': apiBaseURL};
      $http.post(apiBaseURL+'/accountbasic',{'subc':'retrievepswd','data':data})
      .success(function(ret){
        if(ret['result'] == 'ok'){
          alert("An email containing the new password has been sent to you, please check it out!");
          window.location = "#/smartserver/login";
        }
        else{
          alert("Invalid mail address!");
        }
      });
    }
  }]);

//Controller for accountSetting

smartControllers.controller('SetingCtrl', ['$scope', '$http','$routeParams',
  function($scope, $http, $routeParams) {
    var username = $routeParams.username;
     if(!$.cookie('ticket')){
      window.location = '#/smartserver/login';
    }   
    $("#mytab a").click(function(e){
      e.preventDefault();
      $(this).tab('show');
    });
    $('.nav-tabs').button();

    $scope.changePwd = function(){
      var oldpwd = $scope.oldpwd;
      var newpwd = $scope.newpwd;
      var confpwd = $scope.confpwd;
      if(oldpwd == undefined || newpwd == undefined || confpwd == undefined){
        $('.inputerror').show();
      }
      if(newpwd !== confpwd){
        alert('Please doulble confirm the new password!');
        return false;
      }

      var data = {'oldpassword':hex_md5(oldpwd), 'newpassword':hex_md5(newpwd)};
      $http.post(apiBaseURL+'/account',{'subc':'changepswd','data':data, 'token': $.cookie('ticket')})
      .success(function(ret){
        if(ret['result'] == 'ok'){
          alert('Update password successfull!');
          window.location = '#smartserver/index';
        }
        else{
          alert(ret['msg']);
        }
      });
    }

    $scope.changeInfo = function(){
      var company = $scope.company;
      var telephone = $scope.telephone;
      if(company == undefined && telephone == undefined){
        alert("Please fill at least one field!")
        return false;
      }
      var data = {'appid': '02', 'telephone':telephone, 'company':company}
      $http.post(apiBaseURL+'/account',{'subc':'update','data':data, 'token': $.cookie('ticket')})
      .success(function(ret){
        if(ret['result'] == 'ok'){
          alert('Update user info successfully!');
          window.location = '#smartserver/index';
        }
        else{
          alert(ret['msg']);
        }
      });
    }

    $scope.changeUsername = function(){
      var username = $scope.username;
      if(username == undefined){
        alert("Please fill the username field!");
        return false;
      }
      var data = {'appid': '02', 'username':username}
      $http.post(apiBaseURL+'/account',{'subc':'update','data':data, 'token': $.cookie('ticket')})
      .success(function(ret){
        if(ret['result'] == 'ok'){
          alert("Update user name successfully!");
          window.location = '#smartserver/index';
        }
        else{
          alert(ret['msg']);
        }
      });
    }
    
   $scope.$on("fileSelected", function (event, args) {
        $scope.$apply(function () {
            $scope.file = args.file;
        });
    });

    $scope.save = function() {
        $http({
            method: 'POST',
            url: apiBaseURL + "/account",
            headers: { 'Content-Type': false },
            transformRequest: function (data) {
                var formData = new FormData();
              formData.append("data", data.file);
                    formData.append("token", data.token);
                return formData;
            },
            data: { 'file': $scope.file,'token':$.cookie('ticket') }
        }).
        success(function (data, status, headers, config) {
            if(data.result == 'ok'){
              $scope.avatar = apiBaseURL + data.data.url;
              alert("success!");
            }
            else{
              alert(data.msg);
            }
        }).
        error(function (data, status, headers, config) {
            alert("failed!");
        });
    };
   
    $scope.cancel = function(){
      window.location = '#/smartserver/index';
    }
  }]);

//Controller for group

smartControllers.controller('GroupCtrl', ['dialogService','$scope', '$http', '$routeParams','$modal','$log', 
  function(dialogService, $scope, $http, $routeParams, $modal, $log) {
    var groupid = $routeParams.groupid;
    var product = $routeParams.product;
    if(groupid == undefined || product == undefined){
      return;
    }
    if(!$.cookie('ticket')){
      window.location = '#/smartserver/login';
    }
    $scope.isadmin = $.cookie('isadmin');
    $http.get(apiBaseURL+'/group/'+groupid+'?subc=members&appid=02&token='+$.cookie('ticket'))
      .success(function(ret){
        if(ret.result == 'ok'){
          $scope.members = ret.data.members; 
          $.each($scope.members, function(i, o){
        	  if(o.avatar.url){
        	    o.avatar.url = apiBaseURL + o.avatar.url;
            }else{
        	    o.avatar.url = "http://storage.aliyun.com/wutong-data/system/1_S.jpg";
            }
          });
        }else{
          alert(ret.msg);
        }
    });

    $http.get(apiBaseURL+'/group/'+groupid+'?subc=cycles&product='+product+'&appid=02&token='+$.cookie('ticket'))
      .success(function(ret){
        if(ret.result == 'ok'){
          $scope.cycles = ret.data.cycles;
        }else{
          alert(ret.msg);
        }
          
    });

    /* $http.get(apiBaseURL+'/group/'+groupid+'?subc=sessions&product='+product+'&appid=02&token='+$.cookie('ticket'))
      .success(function(ret){
        if(ret.result == 'ok'){
          $scope.sessions = ret.data.sessions;
          $.each($scope.sessions, function(i, o){
	     if(o.cid == '' || o.cid == undefined){
		o.sortcid = "-1";
	     }else{
                o.sortcid = o.cid;
	     }
	     if(o.endtime == '' || o.endtime == undefined){
		o.sorttime = "2200-01-01 00:00:00";	
	     }else{
	        o.sorttime = o.endtime;
	     }
          });
        }else{
          alert(ret.msg);
        }
        
    });*/

$http.get(apiBaseURL+'/account?subc=accountlist&appid=02&token='+$.cookie('ticket'))
       .success(function(ret){
          if(ret.result == 'ok'){
            $scope.users = ret.data.users;
	  }
       });

  $scope.addMember = function () {

    var modalInstance = $modal.open({
      templateUrl: 'myModalContent.html',
      controller: ModalInstanceCtrl,
      windowClass : 'addMember',
      resolve: {
        users: function () {
          return $scope.users;
        }
      }
    });

    modalInstance.result.then(function (selected) {
	$scope.selected = selected;
        var uid = '';
        var roleId = 0;
        if($scope.selected.membername  && $scope.selected.rolename){
             $.each($scope.users, function(i, o){
                  if(o.username == $scope.selected.membername){
                       uid = o.uid
                  }
             });
             if($scope.selected.rolename == 'member'){
                  roleId = 8
             }else if($scope.selected.rolename == 'admin'){
                  roleId = 9;
             }
             }
             var data = {'members':[{'uid':uid,'role':roleId}]};
                 $http.post(apiBaseURL+'/group/'+groupid, {'subc':'setmember','data':data,'token':$.cookie('ticket')})
                    .success(function(ret){
                        if(ret.result == 'ok'){
                  	   var flag = false;
                  	   $.each($scope.members, function(i, o){
                           if(o.username == $scope.selected.membername){
                      	      flag = true;
			      o.role = roleId;
                      	    }
                           });
                           if(!flag){
                               $scope.members.push({'username':$scope.selected.membername,'uid':uid,'role':roleId,'avatar':{'url': "http://storage.aliyun.com/wutong-data/system/1_S.jpg"}});
                            }
		        }else{
                            alert(ret.msg);
		        }
                  }); 
    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });
  };

    $scope.signout = function(){
      $http.post(apiBaseURL+'/account',{'subc':'logout','data':{},'token':$.cookie('ticket')})
      .success(function(ret){
        $.cookie('ticket', '', { expires: -1 });
	$.cookie('isadmin','', {expires:-1});
        window.location = '#/smartserver/login';
      });
    }

    $("#mytabs a").click(function(e){
      e.preventDefault();
      $(this).tab('show');
      if(e.target.id == 'groupSessions'){
        $http.get(apiBaseURL+'/group/'+groupid+'?subc=sessions&product='+product+'&appid=02&token='+$.cookie('ticket'))
          .success(function(ret){
            if(ret.result == 'ok'){
              $scope.sessions = ret.data.sessions; 
	      $.each($scope.sessions, function(i, o){
	     if(o.cid == '' || o.cid == undefined){
		o.sortcid = -1;
	     }else{
                o.sortcid = o.cid;
	     }
	     if(o.endtime == '' || o.endtime == undefined){
		o.sorttime = "2200-01-01 00:00:00";	
	     }else{
	        o.sorttime = o.endtime;
	     }
          });
            }else{
              alert(ret.msg);
            }
             
        });
      }
      else if(e.target.id == 'groupCycles'){
        $http.get(apiBaseURL+'/group/'+groupid+'?subc=cycles&product='+product+'&appid=02&token='+$.cookie('ticket'))
          .success(function(ret){
             if(ret.result == 'ok'){
               $scope.cycles = ret.data.cycles;
             }else{
               alert(ret.msg);
             }
        });
      }
    });

    $scope.newcycle = function(session){
  	   var index;
       $.each($scope.sessions, function(i, o){
          if(o.sid == session.sid){
              index = i;
          }
       });
       $http.post(apiBaseURL+'/group/'+groupid+'/session/'+session.sid,{'subc':'cycle','data':{'cid':0,'product':product},'token':$.cookie('ticket')})
         .success(function(ret){
           if(ret.result == 'ok'){
              $scope.sessions[index].cid = ret.data.cid;
	      $scope.sessions[index].sortcid = ret.data.cid;
               $http.get(apiBaseURL+'/group/'+groupid+'?subc=cycles&product='+product+'&appid=02&token='+$.cookie('ticket'))
                .success(function(ret1){
                   if(ret1.result == 'ok'){
                        $scope.cycles = ret1.data.cycles;
                   }else{
                        alert(ret1.msg);
                   }});

           }else{
    	        alert(ret.msg);
           }
       });
    }


   $scope.delcycle = function(session){
	      var index;
        $.each($scope.sessions, function(i, o){
          if(o.sid == session.sid){
      	    index = i;
          }
        });

        $http.post(apiBaseURL+'/group/'+groupid+'/session/'+session.sid,{'subc':'cycle','data':{'cid':-1},'token':$.cookie('ticket')})
          .success(function(ret){
            if(ret.result == 'ok'){
               $scope.sessions[index].cid = "";
	       $scope.sessions[index].sortcid = -1;
	       $http.get(apiBaseURL+'/group/'+groupid+'?subc=cycles&product='+product+'&appid=02&token='+$.cookie('ticket'))
          	.success(function(ret1){
          	   if(ret1.result == 'ok'){
               		$scope.cycles = ret1.data.cycles;
		   }else{
		        alert(ret1.msg);
		   }});
            }else{
    	         alert(ret.msg);
            }
        });
    }


  $scope.setcycle = function(session,cycleid){
      $http.post(apiBaseURL+'/group/'+groupid+'/session/'+session.sid,{'subc':'cycle','data':{'cid':cycleid,'product':product},'token':$.cookie('ticket')})
      .success(function(ret){
          session.cid = cycleid;
	  session.sortcid = cycleid;	  
      });
  }

    $scope.delSession = function(sid){
      var r = window.confirm("Are you sure to delete?");
      if(r){
         $http.post(apiBaseURL+'/group/'+groupid+'/session/'+sid,{'subc':'delete','data':{},'token':$.cookie('ticket')})
          .success(function(ret){
            if(ret.result == 'ok'){
              var delIndex;
              $.each($scope.sessions, function(i, o){
                if(o.sid == sid){
                  delIndex = i;
                }
              });
              $scope.sessions.splice(delIndex, 1);
            }else{
              alert(ret.msg);
            }
          });
        }
    }
    $scope.delMember = function(username){
      var r = window.confirm("Are you sure to delete?");
      if(r){   
          var uid = 0;
          var roleId = 0;
          var delIndex;
          $.each($scope.members, function(i, o){
           if(o.username == username){
              uid = o.uid;
              roleId = o.role;
              delIndex = i;
            }
          });
          var data = {'members':[{'uid':uid,'role':roleId}]};
          $http.post(apiBaseURL+'/group/'+groupid,{'subc':'delmember','data':data,'token':$.cookie('ticket')})
          .success(function(ret){
            if(ret.result == 'ok'){
              $scope.members.splice(delIndex, 1);
            }else{
              alert(ret.msg);
            }
          });
        }
    }
    $scope.report = function(cid, product){
	     window.location = '#/smartserver/group/'+groupid+'/product/'+product+'/cycle/'+cid;
    } 
}]);

//Controller for session

smartControllers.controller('SessionCtrl', ['dialogService', '$modal', '$scope', '$http', '$routeParams', '$timeout',
  function(dialogService, $modal, $scope, $http, $routeParams, $timeout) {
     if(!$.cookie('ticket')){
      window.location = '#/smartserver/login';
    }
      var groupid = $routeParams.groupid;
      var sessionid = $routeParams.sessionid;
      var product = $routeParams.product;
      var total;
      var tids = [];
      $scope.baseurl = apiBaseURL;
      $scope.buffer = 0;
      $scope.casetype = 'total';
      $scope.product = product;
      $scope.groupid = groupid;  
      if(groupid == undefined || sessionid == undefined){
        return;
      } 
     $http.get(apiBaseURL+'/group/'+groupid+'?subc=members&appid=02&token='+$.cookie('ticket'))
      .success(function(ret){
        $scope.members = ret.data.members;
          $.each($scope.members, function(i, o){
            if(o.avatar.url){
               o.avatar.url = apiBaseURL + o.avatar.url;
            }else{
               o.avatar.url = "http://storage.aliyun.com/wutong-data/system/1_S.jpg";
            }
          });
    });
     $http.get(apiBaseURL+'/group/'+groupid+'/session/'+sessionid+'?subc=summary&appid=02&token='+$.cookie('ticket'))
    .success(function(ret){
      $scope.session = ret.data;
      $scope.deviceinfo = ret.data.deviceinfo;
      $scope.session.runtime = setruntime($scope.session.runtime);
    });

      $scope.getCases = function(casetype){
	$scope.casetype  = casetype;
      	$http.get(apiBaseURL+'/group/'+groupid+'/session/'+sessionid+'?subc=history&appid=02&token='+$.cookie('ticket')+'&casetype='+casetype)
      	.success(function(ret){
       	    $scope.buffer = 0;
	    $scope.pageindex = 1;
            $scope.cases = ret.data.cases;
      	    total = ret.data.totalpage;
      	    $scope.totalpage=[];
      	    if(total <= 10){
      	      for(var i=1;i<=total;i++){
      	        $scope.totalpage.push({'pagenumber':i});
      	      }
      	    }else{
      	       for(var j=1;j<=10;j++){
      	         $scope.totalpage.push({'pagenumber':j});
      	       }
      	    }
      	});  
      }
   
    $http.get(apiBaseURL+'/group/'+groupid+'/session/'+sessionid+'?subc=history&appid=02&token='+$.cookie('ticket'))
      .success(function(ret){
       $scope.cases = ret.data.cases; 
       total = ret.data.totalpage;
       $scope.totalpage=[];
       if(total <= 10){
         for(var i=1;i<=total;i++){
          $scope.totalpage.push({'pagenumber':i});
         }      
       }else{
         for(var j=1;j<=10;j++){
          $scope.totalpage.push({'pagenumber':j});
         }
       }
    });  

  
     $scope.collapse = {};
     $scope.setCollapse = function(caseid){
	$timeout(function(){
	   $scope.collapse[caseid] = true
           }, 500);
     }	
     $scope.delCollapse = function(caseid){
	$timeout(function(){
	   $scope.collapse[caseid] = false 
           }, 1000);
     }
     $scope.pageindex = 1; 
     $scope.pagenationTo = function(page){
        if($scope.pageindex == page.pagenumber + $scope.buffer){
    	     return;
      	}
      	$scope.selected = {};
      	$scope.master = false;
        $scope.pageindex = page.pagenumber + $scope.buffer;
        $http.get(apiBaseURL+'/group/'+groupid+'/session/'+sessionid+'?subc=history&pagenumber='+$scope.pageindex+'&token='+$.cookie('ticket')+'&casetype='+$scope.casetype)
          .success(function(ret){
             $scope.cases = ret.data.cases; 
        });
    }

    $scope.prepage = function(){
      if(total <= 10){
         if($scope.pageindex > 1){
              $scope.pageindex = $scope.pageindex -1;
         }else{
	   	        return;
        }
      }else{
         if($scope.pageindex > 1){
            if($scope.buffer > 0){
              $scope.buffer = $scope.buffer -1;
            }
            $scope.pageindex = $scope.pageindex -1;
         }else{
            return;
         }  
      } 

      $scope.selected = {};     
      $scope.master = false;
      
      $http.get(apiBaseURL+'/group/'+groupid+'/session/'+sessionid+'?subc=history&pagenumber='+$scope.pageindex+'&token='+$.cookie('ticket')+'&casetype='+$scope.casetype)
        .success(function(ret){
          $scope.cases = ret.data.cases; 
 
      });
    }

    $scope.nextpage = function(){
          if(total <= 10){
              if($scope.pageindex < total){
                 $scope.pageindex = $scope.pageindex + 1;
              }else{
	         return;
              }
          }else{
              if($scope.pageindex >= 10){
                  if($scope.pageindex < total){
                      if($scope.buffer < (total-10)){
                          $scope.buffer = $scope.buffer + 1; 
                      }
                      $scope.pageindex = $scope.pageindex + 1;
                  }else{
		    			       	return;
		               }
              }else{
                  $scope.pageindex = $scope.pageindex + 1;
              }   
          }
	     $scope.selected = {};
       $scope.master = false;
       $http.get(apiBaseURL+'/group/'+groupid+'/session/'+sessionid+'?subc=history&pagenumber='+$scope.pageindex+'&token='+$.cookie('ticket')+'&casetype='+$scope.casetype)
        .success(function(ret){
          $scope.cases = ret.data.cases; 
       });

    }    
    $scope.signout = function(){
      $http.post(apiBaseURL+'/account',{'subc':'logout','data':{},'token':$.cookie('ticket')})
      .success(function(ret){
        $.cookie('isadmin','', {expires:-1});
	$.cookie('ticket', '', { expires: -1 });
        window.location = '#/smartserver/login';
      });
    }



    $scope.baseurl = apiBaseURL;
    $scope.selected = {};

    $scope.setAllTids = function(){
     if($scope.master){ 
        $.each($scope.cases, function(i, o){
	  if(o.result == 'fail' || o.result == 'error'){
	     $scope.selected[o.tid] = true;
	  }else{
             $scope.selected[o.tid] = false;
	  }
        });
     }else{
        $.each($scope.cases, function(i, o){
          $scope.selected[o.tid] = false;
        });
     }
    }

 
    var selectedCases = []; 
    $scope.getTids = function(){
	selectedCases = $.grep($scope.cases, function(cas){
	   return $scope.selected[cas.tid];
	});
       tids = [];
       $.each(selectedCases, function(i, o){
	  tids.push(o.tid);
       });
      var modalInstance = $modal.open({
	 templateUrl : 'comments.html',
 	 controller : CommentCtrl,
	 resolve : {
	    tids : function(){
		return tids;
	    },
	    cases : function(){
		return $scope.cases;
	    }
	 }	
      });
	modalInstance.result.then(function (comments){
	  if(comments == 'clear'){
	      var data = {'tid': tids, 'comments':{'caseresult': '', 'commentinfo': '', 'endsession': 0, 'issuetype': ''}};
              $http.post(apiBaseURL + '/session/' + sessionid + '/case', {'subc': 'update', 'data': data, 'token': $.cookie('ticket')})
      		.success(function(ret){
        	if(ret['result'] == 'ok'){
           	    $scope.master=false;
                    var len = tids.length;
           	    for(var i = 0; i<len; i++){
              		$scope.selected[tids[i]] = false;
               		$.each($scope.cases, function(m, n){
                	    if($scope.cases[m].tid == tids[i]){
                     		$scope.cases[m].comments = data.comments;
      	          	    }
               		});
            	    }
        	}
        	else{
          	    alert(ret['msg']);
        	}
      	     });  
	  }else{
	    $scope.comments = comments;
	    if($scope.comments.endsession){
	       $scope.comments.endsession=1;
	    }else{
	       $scope.comments.endsession =0;
	    }
      if($scope.comments.issue == '' || $scope.comments.caseret == '' || $scope.comments.comments == ''){
        alert("IssueType, caseResult and comments can not be empty!");
        return;
      }
	    var data = {'tid':tids, 'comments':{'caseresult':$scope.comments.caseret,
					      'commentinfo':$scope.comments.comments,
					      'endsession':$scope.comments.endsession,
					      'issuetype':$scope.comments.issue}};
            $http.post(apiBaseURL + '/session/' + sessionid + '/case', {'subc': 'update', 'data': data, 'token': $.cookie('ticket')})
              .success(function(ret){
        	if(ret['result'] == 'ok'){
           	  $scope.master=false;
           	  var len = tids.length;
           	  for(var i = 0; i<len; i++){
               	    $scope.selected[tids[i]] = false;
                    $.each($scope.cases, function(m, n){
                      if($scope.cases[m].tid == tids[i]){
                        $scope.cases[m].comments = data.comments;
                      }
      	            });
                  }
                }
                else{
          	  alert(ret['msg']);
        	}
      	    }); 
 	 }
	}, function(){
    
	});
}

    $scope.delMember = function(username){
      var r = window.confirm("Are you sure to delete?");
      if(r){   
          var uid = 0;
          var roleId = 0;
          var delIndex;
          $.each($scope.members, function(i, o){
           if(o.username == username){
              uid = o.uid;
              roleId = o.role;
              delIndex = i;
            }
          });
          var data = {'members':[{'uid':uid,'role':roleId}]};
      
          $http.post(apiBaseURL+'/group/'+groupid,{'subc':'delmember','data':data,'token':$.cookie('ticket')})
          .success(function(ret){
            if(ret.result == 'ok'){
              $scope.members.splice(delIndex, 1);
            }else{
              alert(ret.msg);
            }
          });
        }
    }

      $scope.getLog = function(logurl){
	if(logurl == undefined){
	    alert("log dosen't exist");
	    return;
	}
	window.location = apiBaseURL + logurl;
      }

      $scope.getImages = function(selectedCase){ 
      var rect;
      var zoom = 1;
      var index = 0;
      var x, y, w, h;
      var deviceW = parseInt($scope.deviceinfo.width);
      var deviceH = parseInt($scope.deviceinfo.heigth);
      var tempstr  = JSON.stringify(selectedCase);
      var tempcase = angular.fromJson(tempstr);
      $scope.selectedcase = {};
      $scope.selectedcase = {'expectshot':tempcase.expectshot,'snapshots':tempcase.snapshots};
      if($scope.selectedcase.expectshot.url == undefined && $scope.selectedcase.snapshots.length == 0){
	alert("Image does't exist");
	return;
      }
      if(deviceW >= 400){
	zoom = (deviceW / 400).toFixed(3);
        deviceW = deviceW / zoom;
        deviceH = deviceH / zoom;
      }else{
 	zoom = 1;
      }
      var tempurl = $scope.selectedcase.expectshot.url;
      $scope.selectedcase.expectshot.url = apiBaseURL + tempurl;
      $.each($scope.selectedcase.snapshots, function(i, o){
	var temp = o.url;
        o.url = apiBaseURL + temp;
        rect = o.filename.substring(o.filename.indexOf('(')+1,o.filename.indexOf(')'));
        x = parseInt(rect.substring(rect.indexOf('x')+1, rect.indexOf('y')));
        y = parseInt(rect.substring(rect.indexOf('y')+1, rect.indexOf('w')));
        w = parseInt(rect.substring(rect.indexOf('w')+1, rect.indexOf('h')));
        h = parseInt(rect.substring(rect.indexOf('h')+1));
        o.x = x/zoom;
        o.y = y/zoom;
        o.h = h/zoom;
        o.w = w/zoom;
        if(o.filename == $scope.selectedcase.expectshot.filename){
	  index = i;
          $scope.selectedcase.expectshot.x = x/zoom;
          $scope.selectedcase.expectshot.y = y/zoom;
          $scope.selectedcase.expectshot.h = h/zoom;
          $scope.selectedcase.expectshot.w = w/zoom;
        }
      });
        var temp = $scope.selectedcase.snapshots[0];
	$scope.selectedcase.snapshots[0] = $scope.selectedcase.snapshots[index];
	$scope.selectedcase.snapshots[index] = temp; 
 
	var winclass = 'snapshot';	
        if(!deviceW){
	   winclass = 'snapshot1';
        }
	var modalInstance = $modal.open({
	    templateUrl : 'partials/images.html',
	    controller : ImageCtrl,
	    windowClass : winclass,
	    resolve : {
		selectedcase : function(){
		    return $scope.selectedcase;
		},
		deviceinfo : function(){
		    return {'width' : deviceW,'height' : deviceH}; 
		}
	    }
	});
    }
     
 }]);

//Controller for report
 function setruntime(secs){
    var seconds = Math.floor( secs % 60);
    var minute = Math.floor((secs / 60) % 60);
    var hour = Math.floor((secs / 3600));
    var result = '';
    if(hour>0) result += hour+'h';
    if(minute>0) result += minute+'m';
    if(seconds>=0) result += seconds+'s';
    return result;
}
smartControllers.controller('ReportCtrl', ['$scope', '$http', '$routeParams',
  function($scope, $http, $routeParams) {
     if(!$.cookie('ticket')){
      window.location = '#/smartserver/login';
    }
    $scope.groupid = $routeParams.groupid;
    $scope.cid = $routeParams.cid;
    $scope.product = $routeParams.product;
    var groupid = $routeParams.groupid;
    var cid = $routeParams.cid;
    var product = $routeParams.product;
      $http.get(apiBaseURL+'/group/'+groupid+'?subc=report&cid='+cid+'&token='+$.cookie('ticket'))
      .success(function(ret){
  	var data = ret.data;	
        $scope.summary = data.table1;
        $scope.summary.totaluptime = setruntime($scope.summary.totaluptime);
        $scope.summary.mtbf = setruntime($scope.summary.mtbf);
        $scope.method = data.table1.method;
        var table2 = data.table2;
        $scope.issues= [];
        $.each(table2, function(key, value){
          $scope.issues.push({'issuetype':key,'occurs':value});
        });
	var table3 = ret.data.table3;
        $scope.sessions = [];
        $.each(table3, function(key, value){
	value.firstuptime = setruntime(value.firstuptime);
        value.uptime = setruntime(value.uptime);
	value.firstCuptime = setruntime(value.firstCuptime);
        $scope.sessions.push({'deviceid':key,'content':value});
        });
    var table4 = ret.data.table4;
    $scope.domains = [];
    $scope.cases = [];
    $.each(table4, function(key1, value1){
      var temp={'type':'','total':0,'fail':0,'pass':0,'block':0,'cases':[]};
      temp.type= key1;
      $.each(value1, function(key2, value2){
        var temp1 = {'casetype':key2,'fail':value2.fail,'pass':value2.pass,'block':value2.block,'total':value2.fail+value2.pass+value2.block};
        temp.fail = temp.fail + value2.fail;
        temp.pass = temp.pass + value2.pass;
        temp.block = temp.block + value2.block;
        temp.cases.push(temp1);
      });
      temp.total = temp.fail + temp.pass + temp.block;
      $scope.domains.push(temp);
    });
     });
    $scope.activePosition1 = {};
    $scope.activePosition = {};
    $scope.toggleDetail = function($index) {
        $scope.activePosition[$index] = $scope.activePosition[$index] == true ? false : true;
      
    };      
    $scope.toggleDetail1 = function($index) {
        $scope.activePosition1[$index] = $scope.activePosition1[$index] == true ? false : true;
      
    }; 
     $scope.signout = function(){
      $http.post(apiBaseURL+'/account',{'subc':'logout','data':{},'token':$.cookie('ticket')})
      .success(function(ret){
        $.cookie('ticket', '', { expires: -1 });
	$.cookie('isadmin','', {expires:-1});
	window.location = '#/smartserver/login';
      });
    }
    /*$http.get(apiBaseURL+'/group/'+groupid+'?subc=members&appid=02&token='+$.cookie('ticket'))
      .success(function(ret){
        if(ret.result == 'ok'){
          $scope.members = ret.data.members; 
          $.each($scope.members, function(i, o){
        	  if(o.avatar.url){
        	    o.avatar.url = apiBaseURL + o.avatar.url;
            }else{
        	    o.avatar.url = "http://storage.aliyun.com/wutong-data/system/1_S.jpg";
            }
          });
        }else{
          alert(ret.msg);
        }
    });*/

    $scope.delMember = function(username){
      var r = window.confirm("Are you sure to delete?");
      if(r){   
          var uid = 0;
          var roleId = 0;
          var delIndex;
          $.each($scope.members, function(i, o){
           if(o.username == username){
              uid = o.uid;
              roleId = o.role;
              delIndex = i;
            }
          });
          var data = {'members':[{'uid':uid,'role':roleId}]};
      
          $http.post(apiBaseURL+'/group/'+groupid,{'subc':'delmember','data':data,'token':$.cookie('ticket')})
          .success(function(ret){
            if(ret.result == 'ok'){
              $scope.members.splice(delIndex, 1);
            }else{
              alert(ret.msg);
            }
          });
        }
    }

    $scope.toggleInfo = function(){
	$("#article").toggle();
    }

  }]);

var ModalInstanceCtrl = function ($scope, $modalInstance, users, $http) {
      $scope.users = users;
      $scope.selected = {'membername':$scope.users[0].username,
			 'rolename':'admin'};
      $scope.ok = function () {
        $modalInstance.close($scope.selected);
      };

      $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
      };
};

var CommentCtrl = function($scope, $modalInstance, tids, cases, $http){
     $scope.cases = cases;
      $scope.selected = {
	'issue' : '',
	'caseret' : '',
	'endsession' : false,
	'comments' : ''
      };
    var len = tids.length;
    if(len > 1){
	$scope.disable = true;
    }
    $scope.commit = function(){
      if(len == 0){
    	   alert('please select some cases!');
         return;
    	}
      $modalInstance.close($scope.selected);
      }
    $scope.clear = function(){
	if(len == 0){
	   alert('please select some cases!');
	   return;
	}
	$modalInstance.close('clear');
    }
}

var ImageCtrl = function($scope, $modalInstance,selectedcase, deviceinfo){
	$scope.selectedcase = selectedcase;
	$scope.deviceinfo = deviceinfo;
	$scope.myInterval = 5000;	
        if(!$scope.deviceinfo.width){
	    $scope.deviceinfo.width = 240;
	}			
	$scope.close = function(){
	    $modalInstance.dismiss("cancle");
	}
}
