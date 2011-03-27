( function(){
	
	var gadgetDialog = function(editor){
		
	
		return {
			title : 'Google Gadget Properties',
			minWidth : 400,
			minHeight : 300,
			contents :
                [
                   {
                      id : 'dialog',
                      label : 'Google Gadget Properties',
                      expand : true,
                      elements :
                            [
                               {
	                                type : 'text',
	                                id : 'url',
	                                label : 'url',
	                                style : 'width:100%'
                               },
                               {
                                   type : 'text',
                                   id : 'width',
                                   label : 'width',
                                   style : 'width:100%'
                              },
                              {
	                              type : 'text',
	                              id : 'height',
	                              label : 'height',
	                              style : 'width:100%'
                             }
                               
                         ]
                   }
                ]
		    
		}
	}
	
	CKEDITOR.dialog.add('gadget', function(editor) {
		return gadgetDialog(editor);
	});
		
})();