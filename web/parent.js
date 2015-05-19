
var url = "http://" + location.hostname + ":8080";
var hostList = {};

function updateHosts() {
    var serverSelect = document.getElementById("servers");

    while (serverSelect.firstChild) {
        serverSelect.removeChild(serverSelect.firstChild);
    }

	//$.getJSON(url.concat("/v1.0/hosts"), function(hosts){
    $.getJSON(url.concat("/blacklist"), function(hosts){
	    $.each(hosts, function(key, value){
            hostList[key] = value
            el = document.createElement("option");
            el.textContent = value;
            el.value = key;
            serverSelect.appendChild(el);
        });
    });
}
    
updateHosts();
var dns = {"www.game.com":"10.0.0.6","www.google.com":"10.0.0.4","www.youtube.com":"10.0.0.5"};

function makeData() {
    var vip = $('#virtual-ip').val();
    if(vip in dns){
        vip = dns[vip];
    }
    var lbConfig = {};

    lbConfig['ip'] = vip;

    return lbConfig;
}

function addBlacklist() {
    $('#post-status').html('');

    var lbConfig = makeData();
    if (lbConfig == undefined)
        return;

    var put_url = url.concat("/blacklist");
    var request_data = JSON.stringify(lbConfig);
    $.ajax({
        url: put_url,
        type: 'PUT',
        data: request_data,
        success: function () {
            $('#post-status').html('<p style="color:red; background:silver;">IP added successfully.');
        },
        error: function () {
            $('#post-status').html('<p style="color:red; background:silver;">Error: Add IP failed. Please try again.');
        }
    });

    updateHosts();
}

function deleteBlacklist(vip) {
    if (typeof(vip)==='undefined') {
        vip = $('#virtual-ip').val();
    }

    var select_elt = document.getElementById('servers');
    if (select_elt.selectedIndex != -1) {
        vip = select_elt.options[select_elt.selectedIndex].text;
    }

    $('#post-status').html('');

    lbConfig = {};
    lbConfig['ip'] = vip;

    var del_url = url.concat("/blacklist");
    var request_data = JSON.stringify(lbConfig);
    $.ajax({
        url: del_url,
        type: 'DELETE',
        data: request_data,
        success: function () {
            $('#post-status').html('');
        },
        error: function () {
            $('#post-status').html('<p style="color:red; background:silver;">Error: Delete IP failed. Please try again.');
        }
    });

    updateHosts();
}
/* Format of the POST data is as follows:

{'servers': list of {'ip': ip string, 'mac': mac string},
'virtual_ip': ip string,
'rewrite_ip': 0 or 1 }

 */

/*
function makePostData() {
    var vip = $('#virtual-ip').val();
    var servers = $('#servers').val();
    var rewriteIP = $('#rewrite-ip').is(':checked');
    var lbConfig = {};
    lbConfig['servers'] = [];

    if (servers != undefined) {
        for (i=0; i<servers.length;i++) {
            var server = servers[i];
            lbConfig['servers'].push({'ip': server, 'mac': hostList[server]});
        }
    }
    lbConfig['virtual_ip'] = vip;

    if (rewriteIP) 
        lbConfig['rewrite_ip'] = 1;
    else
        lbConfig['rewrite_ip'] = 0;

    return lbConfig;
}


function createLBPool() {
    $('#post-status').html('');

    var lbConfig = makePostData();
    if (lbConfig == undefined)
        return;

    $.post(url.concat("/v1.0/loadbalancer/create"), JSON.stringify(lbConfig), function() { 
    }, "json")
    .done(function() {
        $('#post-status').html('');
        $('#main').html('<h2>Load-balancer pool created</h2><p>Successfully created load-balancer pool.  Start sending requests to the virtual IP.</p><button class="pure-button pure-button-primary" onclick="deleteLBPool(\''+lbConfig.virtual_ip+'\')">Delete LB pool</button>');
    })
    .fail(function() {
        $('#post-status').html('<p style="color:red; background:silver;">Error: Load-balancer pool creation failed. Please verify your input.');
    });
}

function deleteLBPool(vip) {
    if (typeof(vip)==='undefined') {
        vip = $('#virtual-ip').val();
    }

    $('#post-status').html('');

    lbConfig = {};
    lbConfig['virtual_ip'] = vip;
    lbConfig['rewrite_ip'] = 1;
    lbConfig.servers = [];

    $.post(url.concat("/v1.0/loadbalancer/delete"), JSON.stringify(lbConfig), function() { 
    }, "json")
    .done(function() {
        // In direct call cases where VIP was pre-specified in onClick,
        // it will be best to direct to the original main even before
        // the delete pool button click
        $('#post-status').html('');
        $('#main').html('<h2>Load-balancer pool deleted</h2><p>Successfully deleted load-balancer pool.</p><button class="pure-button pure-button-primary" onclick="window.location.reload()">Create LB pool</button>');
    })
    .fail(function() {
        $('#post-status').html('<p style="color:red; background:silver;">Error: Load-balancer pool deletion failed. Please verify your input.');
    });
}
*/

