import json
import logging
import os
import mimetypes
import hopcon_switch_13
import urllib2

from operator import attrgetter
from webob import Response
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, \
    CONFIG_DISPATCHER, DEAD_DISPATCHER

from ryu.ofproto.ofproto_v1_3 import OFPG_ANY
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from ryu.lib import dpid as dpid_lib

simple_switch_instance_name = 'simple_switch_api_app'
mac_url = '/simpleswitch/mactable/{dpid}'

pt_url = '/switch/port/{dpid}'
bl_url = '/blacklist'
tc_url = '/switch/info'
bw_url = '/bw'

class SimpleSwitchRest13(hopcon_switch_13.SimpleSwitch13):

    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SimpleSwitchRest13, self).__init__(*args, **kwargs)
        self.switches = {}
        self.portsinfo = {}
        self.datapaths = {}
        self.reset = False
        wsgi = kwargs['wsgi']
        wsgi.register(
            SimpleSwitchController, {simple_switch_instance_name: self})
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        for stat in sorted(body, key=attrgetter('port_no')):
            port = stat.port_no
            portinfo = {}

            if self.reset:
                datapath = ev.msg.datapath.id
            if port in self.portsinfo:
                portinfo = self.portsinfo[port]
            else:
                portinfo['port'] = port
                #portinfo['datapath'] = ev.msg.datapath.id
                portinfo['rx_bytes'] = 0
                portinfo['tx_bytes'] = 0

            portinfo['rx_packets'] = stat.rx_packets
            portinfo['rx_errors'] = stat.rx_errors
            portinfo['rx_bytes_pre'] = portinfo['rx_bytes']
            portinfo['rx_bytes'] = stat.rx_bytes
            portinfo['tx_packets'] = stat.tx_packets
            portinfo['tx_errors'] = stat.tx_errors
            portinfo['tx_bytes_pre'] = portinfo['tx_bytes']
            portinfo['tx_bytes'] = stat.tx_bytes
            self.portsinfo[port] = portinfo

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(SimpleSwitchRest13, self).switch_features_handler(ev)
        datapath = ev.msg.datapath
        self.switches[datapath.id] = datapath
        self.mac_to_port.setdefault(datapath.id, {})

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER,
                DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    def addtolist(self, entry):
        entry_ip = entry['ip']
        self.black_list.append(entry_ip)

    def rmfromlist(self, entry):
        entry_ip = entry['ip']
        if entry_ip in self.black_list:
            self.black_list.remove(entry_ip)
            return True
        return False

    def remove_flows(self):
        for datapath in self.datapaths.values():
            parser = datapath.ofproto_parser
            ofproto = datapath.ofproto
            empty_match = parser.OFPMatch()
            instructions = []
            flow_mod = self.remove_table_flows(datapath, 1,
                                            empty_match, instructions)
            datapath.send_msg(flow_mod)
    
    def remove_table_flows(self, datapath, table_id, match, instructions):
        ofproto = datapath.ofproto
        flow_mod = datapath.ofproto_parser.OFPFlowMod(datapath, 0, 0, table_id,
                                                      ofproto.OFPFC_DELETE, 0, 0,
                                                      1,
                                                      ofproto.OFPCML_NO_BUFFER,
                                                      ofproto.OFPP_ANY,
                                                      OFPG_ANY, 0,
                                                      match, instructions)
        return flow_mod

    def set_mac_to_port(self, dpid, entry):
        mac_table = self.mac_to_port.setdefault(dpid, {})
        datapath = self.switches.get(dpid)

        entry_port = entry['port']
        entry_mac = entry['mac']

        if datapath is not None:
            parser = datapath.ofproto_parser
            if entry_port not in mac_table.values():

                for mac, port in mac_table.items():

                    # from known device to new device
                    actions = [parser.OFPActionOutput(entry_port)]
                    match = parser.OFPMatch(in_port=port, eth_dst=entry_mac)
                    self.add_flow(datapath, 1, match, actions)

                    # from new device to known device
                    actions = [parser.OFPActionOutput(port)]
                    match = parser.OFPMatch(in_port=entry_port, eth_dst=mac)
                    self.add_flow(datapath, 1, match, actions)

                mac_table.update({entry_mac: entry_port})
        return mac_table


class SimpleSwitchController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(SimpleSwitchController, self).__init__(req, link, data, **config)
        self.simpl_switch_spp = data[simple_switch_instance_name]
        self.directory = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'web')

    @route('app', '/')
    def start(self, req, **kwargs):
        return self.get_root(req, **kwargs)

    @route('app', '/web/{filename}', methods=['GET'])
    def getWeb(self, req, **kwargs):
        filename = kwargs['filename']
        return self.get_file(req, filename)

    @route('host', bl_url, methods=['PUT'])
    def add_to_blacklist(self, req, **kwargs):
        simple_switch = self.simpl_switch_spp
        new_entry = eval(req.body)
        try:
            simple_switch.addtolist(new_entry)
            simple_switch.remove_flows()
            return 'Success'
        except Exception:
            return Response(status=500)

    @route('host', bl_url, methods=['GET'])
    def get_blacklist(self, req, **kwargs):
        simple_switch = self.simpl_switch_spp
        try:
            black_list = simple_switch.black_list
            body = json.dumps(black_list)
            return Response(content_type='application/json', body=body)
        except Exception:
            return Response(status=500)

    @route('host', bl_url, methods=['DELETE'])
    def delete_from_blacklist(self, req, **kwargs):
        simple_switch = self.simpl_switch_spp
        new_entry = eval(req.body)
        try:
            simple_switch.rmfromlist(new_entry)
            simple_switch.remove_flows()
            return 'Success'
        except Exception:
            return Response(status=500)

    @route('switch', mac_url, methods=['GET'],
           requirements={'dpid': dpid_lib.DPID_PATTERN})
    def list_mac_table(self, req, **kwargs):

        simple_switch = self.simpl_switch_spp
        dpid = dpid_lib.str_to_dpid(kwargs['dpid'])

        if dpid not in simple_switch.mac_to_port:
            return Response(status=404)

        mac_table = simple_switch.mac_to_port.get(dpid, {})
        body = json.dumps(mac_table)
        return Response(content_type='application/json', body=body)

    @route('switch', mac_url, methods=['PUT'],
           requirements={'dpid': dpid_lib.DPID_PATTERN})
    def put_mac_table(self, req, **kwargs):

        simple_switch = self.simpl_switch_spp
        dpid = dpid_lib.str_to_dpid(kwargs['dpid'])
        new_entry = eval(req.body)

        if dpid not in simple_switch.mac_to_port:
            return Response(status=404)

        try:
            mac_table = simple_switch.set_mac_to_port(dpid, new_entry)
            body = json.dumps(mac_table)
            return Response(content_type='application/json', body=body)
        except Exception:
            return Response(status=500)

    @route('monitor', tc_url, methods=['GET'])
    def get_traffic(self, req, **kwargs):
        simple_switch = self.simpl_switch_spp
        portslist = simple_switch.portsinfo.values()
        body = json.dumps(portslist)
        return Response(content_type='application/json', body=body)


    @route('bw', bw_url, methods=['POST'])
    def set_bw(self, req, **kwargs):
        simple_switch = self.simpl_switch_spp
        entry = eval(req.body)
        
        maxbw = entry['maxbw']
        port = entry['port']

        queues = [{"max_rate":maxbw}]
        queue = {}
        queue['port_name'] = 's1-eth' + port
        queue['type'] = 'linux-htb'
        queue['max_rate'] = '10000000'
        queue['queues'] = queues
        data = json.dumps(queue)
        url = 'http://localhost:8080/qos/queue/0000000000000001'
        print data
        try:
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req)
            return response.read()
        except Exception, e:
            print e
            return Response(status=500)
       

    def get_file(self, req, filename, **_kwargs):
        if(filename == "" or filename is None):
            filename = "index.html"
        try:
            filename = os.path.join(self.directory, filename)
            return self.make_response(filename)
        except IOError:
            return Response(status=400)

    def get_root(self, req, **_kwargs):
        return self.get_file(req, None)

    def make_response(self, filename):
        filetype, encoding = mimetypes.guess_type(filename)
        if filetype is None:
            filetype = 'application/octet-stream'
        res = Response(content_type=filetype)
        res.body = open(filename, 'rb').read()
        return res
