__doc__="""info.py

Representation of Point Threshold components.

$Id: info.py,v 1.2 2010/12/14 20:45:46 jc Exp $"""

__version__ = "$Revision: 1.4 $"[11:-2]

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
