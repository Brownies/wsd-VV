function getCookie(c_name) {
    if (document.cookie.length > 0) {

        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
}

function getOrigin(url) {
    
    url = url.replace("://", "#%#");
    url = url.split('/')[0];
    url = url.split(':')[0];
    url = url.replace("#%#", "://");

    return url;
}

function jsonRequest(data, game_id, action) {
	$.ajax({
        type: "POST",
        url: "/ajax/",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        data: JSON.stringify({'data': data, 'game_id': game_id}),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: action,
        failure: function(errMsg) {
            alert("Request Error: " + errMsg);
	    }
	});
} 

function sendMessage(msg, origin){      
	var iframe = document.getElementById('game');		
    iframe.contentWindow.postMessage(msg, origin);   	
}

function ordinal(i) {
    var j = i % 10,
        k = i % 100;
    if (j == 1 && k != 11) {
        return i + "st";
    }
    if (j == 2 && k != 12) {
        return i + "nd";
    }
    if (j == 3 && k != 13) {
        return i + "rd";
    }
    return i + "th";
}