"""
    Copyright (c) 2016 Deciso B.V. - Ad Schellevis
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
    AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
    AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
    OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.

"""

class NetwConfObject(object):
    def __init__(self):
        self._payload = dict()
        self._payload['hostname'] = None
        self._payload['network'] = None

    def is_valid(self):
        for key in self._payload:
            if self._payload[key] is None:
                return False
        return True

    def set(self, prop, value):
        if ('set_%s' % prop) in dir(self):
            getattr(self,'set_%s' % prop)(value)
        else:
            # default copy propery to _payload
            self._payload[prop] = value.text

    def get_hostname(self):
        return self._payload['hostname']

    def get_basepath(self):
        return '/usr/local/etc/tinc/%(network)s' % self._payload

class Network(NetwConfObject):
    def __init__(self):
        super(Network, self).__init__()
        self._payload['id'] = None
        self._payload['privkey'] = None
        self._hosts = list()

    def set_id(self, value):
        self._payload['id'] = value.text

    def set_hosts(self, hosts):
        for host in hosts:
            hostObj = Host()
            for host_prop in host:
                hostObj.set(host_prop.tag, host_prop)
            self._hosts.append(hostObj)

    def config_text(self):
        result = list()
        result.append('AddressFamily=any')
        for host in self._hosts:
            if host.connect_to_this_host():
                result.append('ConnectTo = %s' % (host.get_hostname(),))
        result.append('Device=/dev/tinc%(id)s' % self._payload)
        result.append('Name=%(hostname)s' % self._payload)
        return '\n'.join(result)

    def filename(self):
        return self.get_basepath() + '/tinc.conf'

    def privkey(self):
        return {'filename': self.get_basepath() + '/rsa_key.priv', 'content': self._payload['privkey']}

    def all(self):
        yield self
        for host in self._hosts:
            yield host

class Host(NetwConfObject):
    def __init__(self):
        super(Host, self).__init__()
        self._connectTo = "0"
        self._payload['address'] = None
        self._payload['subnet'] = None
        self._payload['pubkey'] = None

    def connect_to_this_host(self):
        if self.is_valid() and self._connectTo == "1":
            return True
        else:
            return False

    def set_connectto(self, value):
        self._connectTo = value.text

    def config_text(self):
        result = list()
        result.append('Address=%(address)s'%self._payload)
        result.append('Subnet=%(subnet)s'%self._payload)
        result.append(self._payload['pubkey'])
        return '\n'.join(result)

    def filename(self):
        return '%s/hosts/%s' % (self.get_basepath(), self._payload['hostname'])