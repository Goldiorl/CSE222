
var url = "http://" + location.hostname + ":8080";

function updatePortStats() {
    var statsTableBody = document.getElementById('port-stats-data');
    while (statsTableBody.firstChild) {
            statsTableBody.removeChild(statsTableBody.firstChild);
    }


   // $.getJSON(url.concat("/stats/switches"), function(switches){
   //     $.each(switches, function(index, dpid){
            var hex_dpid = parseInt(1).toString(16);
            var tr = document.createElement('TR');
            var physicalPorts = 0;
            var switchColTd = document.createElement('TD');
            switchColTd.appendChild(document.createTextNode(hex_dpid));
            tr.appendChild(switchColTd);

            $.getJSON(url.concat("/switch/info"), function(portStats) {
                //var portStats = ports[dpid];

                $.each(portStats, function(index, obj) {
                    if (obj.port < 65280) {
                        physicalPorts += 1;
                        //var statsArray = new Array(obj.port_no, obj.rx_packets, obj.rx_bytes, obj.rx_dropped, obj.rx_errors, obj.tx_packets, obj.tx_bytes, obj.tx_dropped, obj.tx_errors);
                        var statsArray = new Array(obj.port, obj.rx_packets, obj.rx_bytes, obj.rx_errors, (obj.rx_bytes-obj.rx_bytes_pre)/10,  obj.tx_packets, obj.tx_bytes, obj.tx_errors, (obj.tx_bytes-obj.tx_bytes_pre)/10);
                        $.each(statsArray, function(index, value) {
                            var td = document.createElement('TD');
                            td.appendChild(document.createTextNode(value));
                            tr.appendChild(td);
                        });
                        statsTableBody.appendChild(tr);
                        tr = document.createElement('TR');
                    }
                });

                //switchColTd.rowSpan = physicalPorts;
            });
            switchColTd.rowSpan = physicalPorts;
  //      });
  //  });
}

updatePortStats();

var portStatsIntervalID = setInterval(function(){updatePortStats()}, 5000);

function stopPortStatsTableRefresh() {
    clearInterval(portStatsIntervalID);
}
