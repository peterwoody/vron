/**
 * util.js
 * Common javascript functions
 *
 * @author Humberto Moreira <humberto.mn@gmail.com>
 * @version 2.0
 */



/**
 * Load sub-dropdown accordingly to parent one
 *
 */
function load_ajax_dropdown( parent_id, child_id, parent_value, child_value, url, img ) {	
	
		if ( parent_value != '' ){
			$( "#" + parent_id ).val( parent_value );
		}
		var parent_elem = $( "#" + parent_id );
		var child_elem = $( '#' + child_id );
		var ajax_url = url.replace( parent_id, parent_elem.val() );
		child_elem.before( '<div id="loader"><img src="'+img+'" alt="Loading" title="Loading" /></div>' );
		$.get( ajax_url, function( data ) {
			child_elem.html( data );
			$( '#loader' ).slideUp( 200, function() {
				$( this ).remove();
			});
			child_elem.val( child_value );
		});	
		

}

/**
 * Clean and replace signs from brazilian standard flaot number
 *
 */
function clean_float( number ) {
	
	// clean numbers
	number = number.replace( ".", "" );
	number = number.replace( ",", "." );
	
	return parseFloat( number );

}

/**
 *  Confirm BOX before submitting to some url
 *
 */
function confirm_and_redirect( msg, path ){
    if ( confirm( msg ) ) {
    	
    	window.location = path;
		
    }
}

/**
 *  Confirm BOX before removing something
 *
 */
function confirm_delete( path ){
    if ( confirm( 'Are you sure you want to delete this item?' ) ) {
    	
    	window.location = path;
		
    }
}

/**
 *  Confirm BOX before removing multiple itens (submitting a form)
 *
 */
function confirm_multi_delete(){
	
	if( confirm( 'Are you sure wou want to delete selected items?' ) ){
		return true;
	} else {
		return false;
	}
}

/**
 *  Highlight fieds that did not pass on PHP Validation
 *
 */
function hightlight_error_element( field_id ){
	
	$( "#" + field_id ).parent().addClass( 'has-error' );
	/*if ( $( "#select-" + field_id ).length > 0 ){
		$( "#select-" + field_id ).addClass( 'has-error' );
	}*/

}

/**
*  Remove error highlight from element
*
*/
function remove_hightlight_error_element( field_id, parent_nodes ){
	
	$( "#" + field_id ).parent().removeClass( 'has-error' );
	/*if ( $( "#select-" + field_id ).length > 0 ){
		$( "#select-" + field_id ).removeClass( 'has-error' );
	}*/
}



/**
*  Add field to the required list
*
*/
function add_required_field( field, list ){
	
	// convert to array
	var list = list.split( ',' );
	
	// check if field is already there
	if ( !in_array( field, list ) ){
		list.push( field );
	}
	
	// convert back to csv string and return it
	return list.join( ',' );
} 

/**
*  Remove field from the required list
*
*/
function remove_required_field( field, list ){
	
	// convert to array
	var list = list.split( ',' );
	
	// loop through array to manually remove item
	for ( key in list ) {
	    if ( list[key] == field ) {
	    	list.splice( key, 1 );
	    }
	}

	// convert back to csv string and return it
	return list.join( ',' );
	
} 


/**
 *  Look for required fields that were not set.
 *
 */
function validate_empty_fields( form, required, alert_message ){

	// intial settings
	var error = false;
	
	// if we have a form and list of required fields
	if ( form && required ){
		
		// set variables
		var elem = form.elements;
		var form_size = form.elements.length;
		var required = required.split( ',' );
		
		// if we don't have a cutom error message
		if ( !alert_message ){
			alert_message = "Fill in all required fields!";
		}
		
		// loop through all form elements
		for ( i = 0; i < form_size; i++ ){
			
			// if id is set and element is in the required array
			if ( elem[i].id && in_array( elem[i].id, required ) ){

				// make sure it is a readable form element
				if ( elem[i].type == 'text' || elem[i].type == 'password' || elem[i].type == 'select-one' || elem[i].type == 'textarea' ){
					
					// validate field
					if ( elem[i].value == ""){	// if it's empty we need to hightlight element as error
						
						error = true;
						hightlight_error_element( elem[i].id );
						
					} else { // if it's not empty we put original style
						
						remove_hightlight_error_element( elem[i].id );
	
					}	
				} 
			}	
		}
	}
	
	if ( error ){
		$( "#global_alert" ).show();
		$( "#global_alert_msg" ).html( alert_message );
		window.scrollTo(0, 0);
		return false;
	} else {
		return true;
	}
}


/**
*  X-Browser isArray(), including Safari
*
*/
function isArray(obj) {
	return obj.constructor == Array;
}


/**
*  Check or uncheck all radio or checkboxes of the parent elem_id given
*
*/
function check_all( elem_id, checked ){
	
	var area = document.getElementById( elem_id );
	var elem = area.getElementsByTagName( "input" );
	var size = elem.length;
	
	for ( var i = 0; i < size; i++ ){
		if ( elem[i].type == "checkbox" ){
			elem[i].checked = checked;
		}
	}

}

/**
*  Counts number of checked elements on the given form
*
*/
function count_checked( elem_id ){

	var selected = 0;
	var area = document.getElementById( elem_id );
	var elem = area.getElementsByTagName( "input" );
	var size = elem.length;
	
	for ( var i = 0; i < size; i++ ){
		if ( elem[i].type == "checkbox" && elem[i].checked ){
			selected++;
		}
	}
	
	return selected;
}


/**
*  Equivalent to PHP's in_array()
*
*/
function in_array (needle, haystack, argStrict) {
    // http://kevin.vanzonneveld.net
    // +   original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +   improved by: vlado houba
    // *     example 1: in_array('van', ['Kevin', 'van', 'Zonneveld']);
    // *     returns 1: true
    // *     example 2: in_array('vlado', {0: 'Kevin', vlado: 'van', 1: 'Zonneveld'});
    // *     returns 2: false
    // *     example 3: in_array(1, ['1', '2', '3']);
    // *     returns 3: true
    // *     example 3: in_array(1, ['1', '2', '3'], false);
    // *     returns 3: true
    // *     example 4: in_array(1, ['1', '2', '3'], true);
    // *     returns 4: false
 
    var key = '', strict = !!argStrict;
 
    if (strict) {
        for (key in haystack) {
            if (haystack[key] === needle) {
                return true;
            }
        }
    } else {
        for (key in haystack) {
            if (haystack[key] == needle) {
                return true;
            }
        }
    }
 
    return false;
}

/**
*  Equivalent to PHP's number_format()
*
*/
function number_format (number, decimals, dec_point, thousands_sep) {
    // Formats a number with grouped thousands
    //
    // version: 906.1806
    // discuss at: http://phpjs.org/functions/number_format
    // +   original by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
    // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +     bugfix by: Michael White (http://getsprink.com)
    // +     bugfix by: Benjamin Lupton
    // +     bugfix by: Allan Jensen (http://www.winternet.no)
    // +    revised by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
    // +     bugfix by: Howard Yeend
    // +    revised by: Luke Smith (http://lucassmith.name)
    // +     bugfix by: Diogo Resende
    // +     bugfix by: Rival
    // +     input by: Kheang Hok Chin (http://www.distantia.ca/)
    // +     improved by: davook
    // +     improved by: Brett Zamir (http://brett-zamir.me)
    // +     input by: Jay Klehr
    // +     improved by: Brett Zamir (http://brett-zamir.me)
    // +     input by: Amir Habibi (http://www.residence-mixte.com/)
    // +     bugfix by: Brett Zamir (http://brett-zamir.me)
    // *     example 1: number_format(1234.56);
    // *     returns 1: '1,235'
    // *     example 2: number_format(1234.56, 2, ',', ' ');
    // *     returns 2: '1 234,56'
    // *     example 3: number_format(1234.5678, 2, '.', '');
    // *     returns 3: '1234.57'
    // *     example 4: number_format(67, 2, ',', '.');
    // *     returns 4: '67,00'
    // *     example 5: number_format(1000);
    // *     returns 5: '1,000'
    // *     example 6: number_format(67.311, 2);
    // *     returns 6: '67.31'
    // *     example 7: number_format(1000.55, 1);
    // *     returns 7: '1,000.6'
    // *     example 8: number_format(67000, 5, ',', '.');
    // *     returns 8: '67.000,00000'
    // *     example 9: number_format(0.9, 0);
    // *     returns 9: '1'
    // *     example 10: number_format('1.20', 2);
    // *     returns 10: '1.20'
    // *     example 11: number_format('1.20', 4);
    // *     returns 11: '1.2000'
    // *     example 12: number_format('1.2000', 3);
    // *     returns 12: '1.200'
    var n = number, prec = decimals;
 
    var toFixedFix = function (n,prec) {
        var k = Math.pow(10,prec);
        return (Math.round(n*k)/k).toString();
    };
 
    n = !isFinite(+n) ? 0 : +n;
    prec = !isFinite(+prec) ? 0 : Math.abs(prec);
    var sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep;
    var dec = (typeof dec_point === 'undefined') ? '.' : dec_point;
 
    var s = (prec > 0) ? toFixedFix(n, prec) : toFixedFix(Math.round(n), prec); //fix for IE parseFloat(0.55).toFixed(0) = 0;
 
    var abs = toFixedFix(Math.abs(n), prec);
    var _, i;
 
    if (abs >= 1000) {
        _ = abs.split(/\D/);
        i = _[0].length % 3 || 3;
 
        _[0] = s.slice(0,i + (n < 0)) +
              _[0].slice(i).replace(/(\d{3})/g, sep+'$1');
        s = _.join(dec);
    } else {
        s = s.replace('.', dec);
    }
 
    var decPos = s.indexOf(dec);
    if (prec >= 1 && decPos !== -1 && (s.length-decPos-1) < prec) {
        s += new Array(prec-(s.length-decPos-1)).join(0)+'0';
    }
    else if (prec >= 1 && decPos === -1) {
        s += dec+new Array(prec).join(0)+'0';
    }
    return s;
}

