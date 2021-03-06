#!/usr/bin/env python
# -*- coding: utf-8 -*-

import seiscomp3.DataModel, seiscomp3.IO

def readEventParametersFromXML(xmlFile):
    """
    Reads an EventParameters root element from a SC3 XML file. The
    EventParameters instance holds all event parameters as child
    elements.
    """
    ar = seiscomp3.IO.XMLArchive()
    if ar.open(xmlFile) == False:
        raise IOError, xmlFile + ": unable to open"
    obj = ar.readObject()
    if obj is None:
        raise TypeError, xmlFile + ": invalid format"
    ep  = seiscomp3.DataModel.EventParameters.Cast(obj)
    if ep is None:
        raise TypeError, xmlFile + ": no eventparameters found"
    return ep


def extractEventParameters(ep, eventID=None, filterOrigins=True, filterPicks=True):
    """
    Extract picks, amplitudes, origins, events and focal mechanisms
    from an EventParameters instance. 

    NOTE than the EventParameters is modified; extracted objects are removed.
    """
    pick  = {}
    ampl  = {}
    event = {}
    origin = {}
    fm = {}

    while ep.eventCount() > 0:
        # FIXME: The cast hack forces the SC3 refcounter to be increased.
        obj = seiscomp3.DataModel.Event.Cast(ep.event(0))
        ep.removeEvent(0)
        publicID = obj.publicID()
        if eventID is not None and publicID != eventID:
            continue
        event[publicID] = obj

    pickIDs = []
    while ep.originCount() > 0:
        # FIXME: The cast hack forces the SC3 refcounter to be increased.
        obj = seiscomp3.DataModel.Origin.Cast(ep.origin(0))
        ep.removeOrigin(0)
        publicID = obj.publicID()
        if filterOrigins:
            # only keep origins that are preferredOrigin's of an event
            for _eventID in event:
                if publicID == event[_eventID].preferredOriginID():
                    origin[publicID] = org = obj
                    # collect pick ID's for all associated picks
                    for i in xrange(org.arrivalCount()):
                        arr = org.arrival(i)
                        pickIDs.append(arr.pickID())
                    break

        else:
            origin[publicID] = obj

    while ep.pickCount() > 0:
        # FIXME: The cast hack forces the SC3 refcounter to be increased.
        obj = seiscomp3.DataModel.Pick.Cast(ep.pick(0))
        ep.removePick(0)
        publicID = obj.publicID()
        if filterPicks and publicID not in pickIDs:
            continue
        pick[publicID] = obj

    while ep.amplitudeCount() > 0:
        # FIXME: The cast hack forces the SC3 refcounter to be increased.
        obj = seiscomp3.DataModel.Amplitude.Cast(ep.amplitude(0))
        ep.removeAmplitude(0)
        if obj.pickID() not in pick:
            continue
        ampl[obj.publicID()] = obj

    while ep.focalMechanismCount() > 0:
        # FIXME: The cast hack forces the SC3 refcounter to be increased.
        obj = seiscomp3.DataModel.FocalMechanism.Cast(ep.focalMechanism(0))
        ep.removeFocalMechanism(0)
        fm[obj.publicID()] = obj

    return event, origin, pick, ampl, fm


def nslc(wfid):
    """
    Convenience function to retrieve network, station, location and channel codes from a waveformID object and return them as tuple
    """
    n,s,l,c = wfid.networkCode(),wfid.stationCode(),wfid.locationCode(),wfid.channelCode()
    return n,s,l,c


def format_nslc_spaces(wfid):
    """
    Convenience function to return network, station, location and channel code as fixed-length, space-separated string
    """
    n,s,l,c = nslc(wfid)
    if l=="": l="--"
    return "%-2s %5s %2s %3s" % (n,s,l,c)


def format_nslc_dots(wfid):
    """
    Convenience function to return network, station, location and channel code as dot-separated string
    """
    return "%s.%s.%s.%s" % nslc(wfid)


def format_time(time, digits=3):
    """
    Convert a seiscomp3.Core.Time to a string
    """
    return time.toString("%Y-%m-%d %H:%M:%S.%f000000")[:20+digits].strip(".")

def automatic(obj):
    return obj.evaluationMode() == seiscomp3.DataModel.AUTOMATIC
