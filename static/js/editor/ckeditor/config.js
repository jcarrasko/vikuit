/*
(C) Copyright 2011 Jose Carrasco <jose.carrasco at vikuit dot com>
(C) Copyright 2011 Jose Blanco <jose.blanco at vikuit dot com>

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

CKEDITOR.editorConfig = function( config )
{
	
	config.extraPlugins = 'gadget';
	  
	config.toolbar_Full =
		[
		    ['Source','-','Save','NewPage','Preview','-','Templates'],
		    ['Cut','Copy','Paste','PasteText','PasteFromWord','-','Print', 'SpellChecker', 'Scayt'],
		    ['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
		    ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField'],
		    '/',
		    ['Bold','Italic','Underline','Strike','-','Subscript','Superscript'],
		    ['NumberedList','BulletedList','-','Outdent','Indent','Blockquote','CreateDiv'],
		    ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
		    ['BidiLtr', 'BidiRtl'],
		    ['Link','Unlink','Anchor'],
		    ['Image','Flash','Table','HorizontalRule','Smiley','SpecialChar','PageBreak','Iframe'],
		    '/',
		    ['Styles','Format','Font','FontSize'],
		    ['TextColor','BGColor'],
		    ['Maximize', 'ShowBlocks','-','About']
		];
	
		config.toolbar_Article =
		[
			 
			 ['Styles','Undo','Redo','-','Find','Replace'],
	         ['Bold','Italic','Underline','StrikeThrough'],
	         ['OrderedList','UnorderedList','-','Outdent','Indent'],
	         ['NumberedList','BulletedList','-','Outdent','Indent','Blockquote','CreateDiv'],
	         ['JustifyLeft','JustifyCenter','JustifyRight','JustifyFull'],
	         ['Link','Unlink'],
	         ['Gadget', 'Image','Flash','SpecialChar'] 
		];
		 
		config.toolbar_Basic =
		[
		    ['Bold', 'Italic', '-', 'NumberedList', 'BulletedList', '-', 'Link', 'Unlink']
		];
};
