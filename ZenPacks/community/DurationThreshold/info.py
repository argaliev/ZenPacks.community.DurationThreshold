__doc__="""info.py

Representation of Duration Threshold components.

"""

from zope.interface import implements
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.interfaces import template as templateInterfaces
from Products.Zuul.infos.template import ThresholdInfo
from Products.Zuul.decorators import info
from ZenPacks.community.DurationThreshold import interfaces

class DurationThresholdInfo(ThresholdInfo):
    implements(interfaces.IDurationThresholdInfo)
    minval = ProxyProperty("minval")
    maxval = ProxyProperty("maxval")
    interval = ProxyProperty("interval")
    severity = ProxyProperty("severity")
    eventClass = ProxyProperty("eventClass")
    escalateCount = ProxyProperty("escalateCount")
