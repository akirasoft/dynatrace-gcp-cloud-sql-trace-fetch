# -*- coding: utf-8 -*-

from google.cloud import trace_v1
import sys
import os
import requests
import json

OPENTEL_COLLECTOR = os.environ['OPENTEL_COLLECTOR_HTTP']

class ZipkinSpan:
    traceId: str
    name: str
    id: str
    parentId: str
    timestamp: int
    duration: int
    kind: str
    tags: dict

    def __init__(self, traceId: str, name: str, id: str, parentId: str, timestamp: int, duration: int, kind: str, tags: dict) -> None:
        self.traceId = traceId
        self.name = name
        self.id = id
        self.parentId = parentId
        self.timestamp = timestamp
        self.duration = duration
        self.kind = kind
        self.tags = tags


def nsec_to_usec_round(DatetimeNanos) -> int:
    """Round nanoseconds to microseconds

    Timestamp in zipkin spans is int of microseconds.
    See: https://zipkin.io/pages/instrumenting.html
    """
    inttimestamp = DatetimeNanos.timestamp() * 1e9
    return int((inttimestamp + 500) // 10 ** 3)


def mapSpanKind(kind):      
# Defining the dict
    switcher = {
            "RPC_SERVER": "SERVER",
            "RPC_CLIENT": "CLIENT",
    }
    return switcher.get(kind, "SERVER")


def send_trace(JsonSpanList):

    print("sending Zipkin trace to: ", OPENTEL_COLLECTOR)

    x = requests.post(OPENTEL_COLLECTOR, headers={'Content-Type': 'application/json'}, data = JsonSpanList)

    print(x.text)
    print("trace sent")
    print("")
    return None


def parse_trace(googletrace):
    projectId = googletrace.project_id
    traceId = googletrace.trace_id
    # service_name = "CloudTrace." + projectId
    service_name = projectId + ":Undefined"
    # print("Service Name: ", service_name, " Trace ID: ", traceId)

    SpanList = []
    # JsonSpanList = []

    for Span in googletrace.spans:

        # SpanId = hex(Span.span_id)
        SpanId = format(Span.span_id, '016x')

        Name = Span.name
        Kind = mapSpanKind(Span.kind)
        StartTimeUnixMicroseconds = nsec_to_usec_round(Span.start_time)
        # EndTimeUnixMicroseconds = nsec_to_usec_round(Span.end_time)
        # zipkin doesn't use endtime, so we use duration
        td = Span.end_time - Span.start_time
        Duration = td.microseconds

        # zipkin will want the parent span id removed if it is the root span
        # but CloudTrace gives us a 0
        ParentSpanId = Span.parent_span_id
        if ParentSpanId == 0:
            ParentSpanId = ""
        else:
            ParentSpanId = format(ParentSpanId, '016x')
        tags = {}
        for key in Span.labels.keys():
            Value = Span.labels[key]
            FixedKey = key.replace("/", ".")
            FixedValue = Value.replace("/", ".")
            tags[FixedKey] = FixedValue

        # create json object
        zipkin_span = ZipkinSpan(traceId=traceId, name=Name, id=SpanId, parentId=ParentSpanId, timestamp=StartTimeUnixMicroseconds, duration=Duration, kind=Kind, tags=tags)

        SpanList.append(zipkin_span)
 
    JsonSpanList = json.dumps(SpanList, default=lambda o: o.__dict__, indent=4)
    print("Sending Zipkin Trace to OT Collector - Trace Data: ", JsonSpanList)
    send_trace(JsonSpanList)


def get_trace(project_id: str, trace_id: str):
    """Get a trace by its ID."""

    client = trace_v1.TraceServiceClient()

    trace = client.get_trace(project_id=project_id, trace_id=trace_id)
    print("getting trace: ", trace_id)
    # print(trace)
    print("parsing trace")
    parse_trace(trace)
    return trace

def list_traces(project_id: str):
    """List traces for a project."""

    client = trace_v1.TraceServiceClient()
    filter = '+span:"Cloud SQL Query"'
    request = trace_v1.ListTracesRequest(project_id=project_id, filter=filter)
    traces = client.list_traces(request=request)

    for trace in traces:
        get_trace(project_id, trace.trace_id)

    return traces

def main(argv):
    """Main entrypoint to the integration with the Cloud Trace."""

    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]    

    print("Listing traces for project: ", project_id)
    list_traces(project_id)
    # get_trace(project_id, "fe06a461018e5a55e9b922c23e3739f3")
    # print("fetching all traces")
    

if __name__ == '__main__':
    main(sys.argv)    