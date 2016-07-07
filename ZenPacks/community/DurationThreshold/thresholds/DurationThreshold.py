__doc__= """DurationThreshold
"""

import rrdtool
from AccessControl import Permissions

from Globals import InitializeClass
from Products.ZenModel.ThresholdClass import ThresholdClass
from Products.ZenModel.ThresholdInstance import ThresholdInstance, ThresholdContext
from Products.ZenEvents import Event
from Products.ZenEvents.ZenEventClasses import Perf_Snmp
from Products.ZenUtils.ZenTales import talesEval, talesEvalStr
from Products.ZenUtils.Utils import readable_time
from Products.ZenEvents.Exceptions import pythonThresholdException, \
        rpnThresholdException

import logging
log = logging.getLogger('zen.DurationThreshold')

from Products.ZenUtils.Utils import unused, nanToNone

# Note:  this import is for backwards compatibility.
# Import Products.ZenRRD.utils.rpneval directy.
from Products.ZenRRD.utils import rpneval

NaN = float('nan')

class DurationThreshold(ThresholdClass):
    """
    Threshold class that can evaluate RPNs and Python expressions
    """

    minval = ""
    maxval = ""
    interval = ""
    eventClass = Perf_Snmp
    severity = 3
    escalateCount = 0
    description = ''
    explanation = ''
    resolution = ''

    _properties = ThresholdClass._properties + (
        {'id':'minval',        'type':'string',  'mode':'w'},
        {'id':'maxval',        'type':'string',  'mode':'w'},
        {'id':'interval',      'type':'string',  'mode':'w'},
        {'id':'escalateCount', 'type':'int',     'mode':'w'},
        {'id': 'description', 'type': 'string', 'mode': 'rw'},
        {'id': 'explanation', 'type': 'string', 'mode': 'rw'},
        {'id': 'resolution', 'type': 'string', 'mode': 'rw'},
        )

    factory_type_information = (
        {
        'immediate_view' : 'editDurationThreshold',
        'actions'        :
        (
          { 'id'            : 'edit',
            'name'          : 'Duration Threshold',
            'action'        : 'editDurationThreshold',
            'permissions'   : ( Permissions.view, ),
          },
        )
        },
        )

    def createThresholdInstance(self, context):
        """Return the config used by the collector to process point
        thresholds. (id, minval, maxval, interval, severity, escalateCount)
        """
        mmt = DurationThresholdInstance(self.id,
                                      ThresholdContext(context),
                                      self.dsnames,
                                      minval=self.getMinval(context),
                                      maxval=self.getMaxval(context),
                                      interval=self.getInterval(context),
                                      eventClass=self.eventClass,
                                      severity=self.getSeverity(context),
                                      escalateCount=self.getEscalateCount(context),
                                      )
        return mmt

    def getMinval(self, context):
        """
        Build the min value for this threshold.
        """
        return self.evaluateDataSourceExpression(context, 'minval', 'minimum value')

    def getMaxval(self, context):
        """
        Build the max value for this threshold.
        """
        return self.evaluateDataSourceExpression(context, 'maxval', 'maximum value')

    def getInterval(self, context):
        """
        Build the interval for this threshold.
        """
        return self.evaluateDataSourceExpression(context, 'interval', 'interval')

    def getSeverity(self, context):
        """
        Build the severity for this threshold.
        """
        return self.severity

    def getEscalateCount(self, context):
        """
        Build the escalation count for this threshold.
        """
        return self.escalateCount

    def evaluateDataSourceExpression(self, context, propName, readablePropName):
        """
        Return back a sane value from evaluation of an expression.

        @paramter context: device or component object
        @type context: device or component object
        @paramter propName: name of the threshold property to evaluate
        @type propName: string
        @paramter readablePropName: property name for displaying in error messages
        @type readablePropName: string
        @returns: numeric
        @rtype: numeric
        """
        value = getattr(self, propName, None)
        if value:
            try:
                express = "python:%s" % value
                evaluated = talesEval(express, context)
                value = evaluated
            except:
                msg= "User-supplied Python expression (%s) for %s caused error: %s" % (
                    value, readablePropName, self.dsnames)
                log.error(msg)
                raise pythonThresholdException(msg)
                value = None
            return nanToNone(value)

InitializeClass(DurationThreshold)
DurationThresholdClass = DurationThreshold

class DurationThresholdInstance(ThresholdInstance):
    # Not strictly necessary, but helps when restoring instances from
    # pickle files that were not constructed with a count member.
    count = {}

    def __init__(self, id, context, dpNames,
                 minval, maxval, interval, eventClass, severity, escalateCount):
        self.count = {}
        self._context = context
        self.id = id
        self.minimum = minval if minval != '' else None
        self.maximum = maxval if maxval != '' else None
        self.interval = interval if interval != '' else None
        self.eventClass = eventClass
        self.severity = severity
        self.escalateCount = escalateCount
        self.dataPointNames = dpNames
        self._rrdInfoCache = {}

    def name(self):
        "return the name of this threshold (from the ThresholdClass)"
        return self.id

    def context(self):
        "Return an identifying context (device, or device and component)"
        return self._context

    def dataPoints(self):
        "Returns the names of the datapoints used to compute the threshold"
        return self.dataPointNames

    def rrdInfoCache(self, dp):
        if dp in self._rrdInfoCache:
            return self._rrdInfoCache[dp]
        data = rrdtool.info(self.context().path(dp))
        # handle both old and new style RRD versions
        try:
            # old style 1.2.x
            value = data['step'], data['ds']['ds0']['type']
        except KeyError:
            # new style 1.3.x
            value = data['step'], data['ds[ds0].type']
        self._rrdInfoCache[dp] = value
        return value

    def countKey(self, dp):
        return(':'.join(self.context().key()) + ':' + dp)

    def getCount(self, dp):
        countKey = self.countKey(dp)
        if not self.count.has_key(countKey):
            return None
        return self.count[countKey]

    def incrementCount(self, dp):
        countKey = self.countKey(dp)
        if not self.count.has_key(countKey):
            self.resetCount(dp)
        self.count[countKey] += 1
        return self.count[countKey]

    def resetCount(self, dp):
        self.count[self.countKey(dp)] = 0

    def fetchValuesList(self, dp, durationTime):
        """
        Fetch the most recent value for a data point from the RRD file.
        """
        startStop, names, values = rrdtool.fetch(self.context().path(dp),
            'AVERAGE', '-s', 'now-%d' % (durationTime*2), '-e', 'now')
        values = [ v[0] for v in values if v[0] is not None ]
        if values: return values

    def check(self, dataPoints):
        """The given datapoints have been updated, so re-evaluate.
        returns events or an empty sequence"""
        unused(dataPoints)
        result = []
        for dp in self.dataPointNames:
            cycleTime, rrdType = self.rrdInfoCache(dp)
            result.extend(self.checkDuration(
                dp, self.fetchValuesList(dp, self.interval)))
        return result

    def checkRaw(self, dataPoint, timeOf, value):
        """A new datapoint has been collected, use the given _raw_
        value to re-evalue the threshold."""
        unused(timeOf)
        result = []
        if value is None: return result
        try:
            cycleTime, rrdType = self.rrdInfoCache(dataPoint)
        except Exception:
            log.exception('Unable to read RRD file for %s' % dataPoint)
            return result
        values = self.fetchValuesList(dataPoint, self.interval)
        result.extend(self.checkDuration(dataPoint, values))
        return result

    def checkDuration(self, dp, values):
        'Check the value for point thresholds'
        log.debug("Checking %s %s against interval %s",
                  dp, values, self.interval)
        if not values:
            return []
        values = map(float, values)
        avg_value = sum(values)/len(values)
        thresh = None
        if self.maximum is not None and avg_value > self.maximum:
            thresh = self.maximum
            how = 'above'
        if self.minimum is not None and avg_value < self.minimum:
            thresh = self.minimum
            how = 'below'
        if thresh is not None:
            severity = self.severity
            count = self.incrementCount(dp)
            if self.escalateCount and count >= self.escalateCount:
                severity = min(severity + 1, 5)
            summary = 'Threshold of %s: in the last %s average value was %s %s.' % (
                self.name(), readable_time(self.interval), how, thresh)
            return [dict(device=self.context().deviceName,
                         summary=summary,
                         eventKey=self.id,
                         eventClass=self.eventClass,
                         component=self.context().componentName,
                         severity=severity)]
        else:
            count = self.getCount(dp)
            if count is None or count > 0:
                summary = 'Threshold of %s restored: current value: %.2f' % (
                    self.name(), avg_value)
                self.resetCount(dp)
                return [dict(device=self.context().deviceName,
                             summary=summary,
                             eventKey=self.id,
                             eventClass=self.eventClass,
                             component=self.context().componentName,
                             severity=Event.Clear)]
        return []

    def getGraphElements(self, template, context, gopts, namespace, color,
                         legend, relatedGps):
        """Produce a visual indication on the graph of where the
        threshold applies."""
        unused(template, namespace)
        return gopts

from twisted.spread import pb
pb.setUnjellyableForClass(DurationThresholdInstance, DurationThresholdInstance)