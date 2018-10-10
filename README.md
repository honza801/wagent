# Webvirtcloud Agent

This is helper agent for doing nasty things on hypervisor, which are impossible to do with libvirt itself.

It uses pyzmq (python bindings for zeromq) for message transport.

# Installation

Install python3 and virtualenv.

```
apt install python3 python3-virtualenv virtualenv
```

Clone repository

```
git clone ... /opt/wagent
```

Create python virtual environment

```
virtualenv -p python3 /opt/wagent/venv
source /opt/wagent/venv/bin/activate
pip install -r /opt/wagent/requirements.txt
```

Enable service

```
systemctl enable /opt/wagent/wagent.service
systemctl start wagent
```

