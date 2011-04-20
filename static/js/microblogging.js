/**
 * Modified by jose.blanco at vikuit dot com
 * This file is part of vikuit, please check vikuit license.
 **/
(function($){

	var maxItems=0;
	var style = 'mblog';
	var labelBy = 'By';
	var labelRead = 'Read more';
	var current = "";
	var standard = true;
	$.fn.microblogging = function(j){
		var k=$.extend({
			targeturl:"http://www.vikuit.com/",
			loadingImg:'/static/images/throbber.gif',
			maxItems:1,
			standard:true,
			current:"",
			style:'mblog',
			labelBy:'By',
			labelRead:'Read more'},j);

		if(!j.targeturl)
			return false;

		var l=$.extend(k,j);
		var n="xml";
		var divid=guid();
		this.append('<div id="'+divid+'newsfeed"><div class="atomloader" style="position:absolute;text-align:center;z-index:99;"><img src="'+l.loadingImg+'"/></div></div>');
		$('#'+divid+'newsfeed .atomloader').width(this.width());
		$('#'+divid+'newsfeed .atomloader').height(this.height());
		$('#'+divid+'newsfeed .atomloader img').height(this.height()/4);
		var toplocal=(this.height()/2)-($('#'+divid+'newsfeed .atomloader img').height()/2)
		$('#'+divid+'newsfeed .atomloader img').css('margin-top',toplocal+'px');
		var path=l.targeturl;
		maxItems=l.maxItems;
		standard = l.standard;
		style = l.style;
		labelBy = l.labelBy;
		labelRead = l.labelRead;
		current = l.current;
		requestRSS(path,function(results){
			$('#'+divid+'newsfeed').append(results);
			$('#'+divid+'newsfeed .atomloader').remove();
			});
		};

		function S4(){
			return(((1+Math.random())*0x10000)|0).toString(16).substring(1);
		}
		
		function guid(){
			return(S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
		}

		function requestRSS(site,callback){
			if(!site){
				alert('No site was passed.');
				return false;
			}
			    $.ajax({
			    	type: 'get',
			    	url: site,
			    	async: true,
			    	error: function(){
		    				document.getElementById("mssger" ).innerHTML = "Oops!! :(";
		    				$( "#mssger" ).dialog( "open" );
			    		},
			    	success: function(data){cbFunc(data)}
			    });
			    
			function cbFunc(data){
				var items = data.getElementsByTagName("item");

				if(items[0]){
					var datalength=items.length;
					if(datalength>maxItems){
						datalength=maxItems
					};
					var i;
					var feedHTML="";
					for(i=0;i<datalength;i++) {
						var author = items[i].getElementsByTagName("author")[0].childNodes[0].nodeValue;
						feedHTML += "<div class='"+style+"'><blockquote>";
						feedHTML+="<cite>"+(standard?labelBy+": ":"")+"<strong>"+author +"</strong>"
						try {
							if (standard && (author == current || current == 'admin' )){
								try {
									var key = -1;
									var tokens = items[i].getElementsByTagName("link")[0].textContent.split("/");
									if (tokens.length > 0){
										key = tokens[tokens.length-1];
									}
									feedHTML+=" <a href='javascript:removeBloggingPost(\""+key+"\");'><img src='/static/images/cross.png' /></a> ";
								} catch(e){}
							}

						} catch(e) {}
						try {
							var pub = new Date(items[i].getElementsByTagName("pubDate")[0].childNodes[0].nodeValue);
							feedHTML+=" | "+ pub.toLocaleDateString()+" "+pub.toLocaleTimeString()+""
						} catch(e) {}
						feedHTML += "</cite>";
						feedHTML+="<p>"+items[i].getElementsByTagName("title")[0].childNodes[0].nodeValue+"</p>";
						feedHTML+="</blockquote></div>";
					}
					if(typeof callback==='function'){
						callback(feedHTML);
					}
				} else throw new Error('Nothing returned from getJSON.');
			}
		}//Cross
})(jQuery);

function sendBloggingPost(user, content) {
	var params = "auth="+auth+"&content="+content;
	var href = "/module/mblog.edit?"
	ajaxPost(href, params);
}

function removeBloggingPost(key) {
	var params = "act=del&auth="+auth+"&key="+key;
	var href = "/module/mblog.edit?"
	ajaxPost(href, params);

}

function ajaxPost(href, params){
	
    $.ajax({
    	type: 'post',
    	url: href,
    	data: params,
    	dataType: 'json',
    	async: true,
	cache: false,
    	error: function(){
				document.getElementById("mssger" ).innerHTML = 'OOops!!';
				$( "#mssger" ).dialog( "open" );
    		},
    	success: function(json){
    			var saved = json.saved;
    			if (saved == true){
    				document.getElementById("mssger").innerHTML = "OK";
    				$( "#mssger" ).dialog( "open" );
    			} else {
    				document.getElementById("mssger" ).innerHTML = json.msg;
    				$( "#mssger" ).dialog( "open" );
    			}
    		}
    });
	
}
