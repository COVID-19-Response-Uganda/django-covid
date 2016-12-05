# -*- coding: utf-8 -*-

"""
Tests for ORB resource models
"""

import pytest

from orb.peers.models import Peer


class TestPeerModel(object):
    """
    Tests for the primary Peer model
    """
    def test_string_representation(self):
        peer = Peer(name="Another ORB", host="http://www.yahoo.mx")
        assert unicode(peer) == u"Another ORB"


@pytest.mark.django_db
class TestPeerQuerysets(object):

    def test_active_peers(self):
        Peer.peers.create(name="Second ORB", host="http://www.yahoo.mx")
        Peer.peers.create(name="Third ORB", host="http://www.yahoo.ca", active=False)
        assert u"Second ORB" == Peer.peers.active().get().name


@pytest.mark.django_db
class TestLoggingQuerysets(object):

    def test_log(self):
        peer = Peer.peers.create(name=u"Sécond ORB", host="http://www.yahoo.mx")
        update_log = peer.logs.create()
        update_log.finish()
        assert update_log.finished > update_log.created
