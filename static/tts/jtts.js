$(document).ready(function(){

		$.fn.jtts_getMyPath = function(){
			var path= $('script[src*="jtts.js"]').attr('src').split('?')[0];      // remove any ?query
			var mydir= path.split('/').slice(0, -1).join('/')+'/';
			return mydir;
		}
		
		$.fn.jtts = function() {
				$('#jtts_player').remove();
				$('body').append('<div id="jtts_player" style="height:0px; width:0px;"></div>');
				$('#jtts_player').data('jtts_text', $(this).jtts_getText());				
				$('#jtts_player').jPlayer({
					swfPath: $(this).jtts_getMyPath() + "jQuery.jPlayer.2.0.0/",
					supplied: "mp3",					
					ready: function(){
						setTimeout(function(){ $('#jtts_player').jtts_sayIt(); },100);
					},
					ended: function(){
						$('#jtts_player').jtts_sayIt();
					}
				});
				return $(this); 
		}
		
		$.fn.jtts_getText = function(){		
			var newTtsText = '';
			$(this).each(function(){
					newTtsText = newTtsText + " . " + $(this).text();
			});
			newTtsText = newTtsText.replace(/\n/g," ");			
			newTtsText = newTtsText.replace(/:/g,".");
			newTtsText = newTtsText.replace(/\.com/g," dot com");
			newTtsText = newTtsText.replace(/\.net/g," dot net");
			newTtsText = newTtsText.replace(/@/g," at ");
			newTtsText = newTtsText.replace(/\%/g," percent ");
			var regexDecimal = /\d+\.\d+/g;
			var match=null;
			while(match = regexDecimal.exec(newTtsText)){
				var newDecimal = match[0].replace("."," point ");
				newTtsText = newTtsText.replace(match[0],newDecimal);
			}
			return newTtsText;
		}
		
		$.fn.jtts_sayIt = function(){
				var text = $.trim($(this).data('jtts_text'));
				var remainder = '';
				if (text.length==0){
					return;
				}
				else if(text.length > 100){
					var tmp = text.substring(0,100);
					var lastSpace=tmp.lastIndexOf(".");
					if (lastSpace<=0){ lastSpace=tmp.lastIndexOf(","); }
					if (lastSpace<=0){ lastSpace=tmp.lastIndexOf(" "); }
					remainder=text.substring(lastSpace);
					text=text.substring(0,lastSpace);
				}
				$(this).data('jtts_text',remainder);
				$('#jtts_player').jPlayer("setMedia", {
					mp3: "http://translate.google.com/translate_tts?tl=en&q="+escape(text)
				}).jPlayer("play");		
		}
		
});
		
