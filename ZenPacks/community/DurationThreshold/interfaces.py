__doc__="""interfaces.py

Representation of Point Threshold components.

$Id: info.py,v 1.2 2010/12/14 20:45:46 jc Exp $"""

__version__ = "$Revision: 1.4 $"[11:-2]

from Products.Zuul.interfaces import IInfo, IFacade
from Products.Zuul.interfaces.template import IThresholdInfo
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t

class IDurationThresholdInfo(IThresholdInfo):
    """
    Interfaces for Duration Threshold
    """
    escalateCount = schema.Int(title=_t(u'Escalate Count'), order=20)
    minval = schema.TextLine(title=_t(u'Minimum value'), order=10)
    maxval = schema.TextLine(title=_t(u'Maximum value'), order=11)
    interval = schema.TextLine(title=_t(u'Time Interval(seconds)'), order=12)
