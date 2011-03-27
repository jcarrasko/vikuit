/*
(C) Copyright 2011 Jose Carrasco <jose.carrasco at vikuit dot com>

This file is part of "vikuit".

"vikuit" is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

"vikuit" is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with "vikuit".  If not, see <http://www.gnu.org/licenses/>.
*/

// Register the related command.

CKEDITOR.plugins.add('gadget',
{
    init: function(editor)
    {
    	  var pluginName = 'gadget';
    	  
          CKEDITOR.dialog.add(pluginName, this.path + 'dialogs/gadget.js');
          editor.addCommand(pluginName, new CKEDITOR.dialogCommand(pluginName));
          
          editor.ui.addButton('Gadget',
                  {
                      label: 'Google Gadget',
                      command: pluginName,
                      icon: CKEDITOR.plugins.getPath(pluginName	) + 'images/gadget.png'
                  });
          
      
    }
});
 

 
