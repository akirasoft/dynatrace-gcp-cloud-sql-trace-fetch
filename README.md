# dynatrace-gcp-cloud-sql-trace-fetch
fetch traces from GCP Cloud SQL and import into Dynatrace

Create a service account that has the `cloudtrace.traces.list` and `cloudtrace.traces.get` permissions and download the json service account definition

Deploy an OpenTelemetry Collector configured to receive Zipkin spans and send OLTP to Dynatrace. A sample config.yaml is present in this repo.

Create three environment variables:

    export GOOGLE_CLOUD_PROJECT="your-project-name
    export GOOGLE_APPLICATION_CREDENTIALS="your-service-account.json
    export OPENTEL_COLLECTOR_HTTP="http://otel-collector-host:9411/api/v2/spans

**IMPORTANT NOTE: the GOOGLE_APPLICATION_CREDENTIALS environment variable should be an ABSOLUTE path to the service account json file.**

install python 3.9 and install the python requirements via: `pip install -r requirements.txt`

then simply run `python3 main.py`, this will fetch all traces and send them to the OTEL collector, the otel collector will then forward them on to Dynatrace. 

To run within Docker:
after you have created the environment variables, run the following command:

    docker run -it \
    -e OPENTEL_COLLECTOR_HTTP=$OPENTEL_COLLECTOR_HTTP \
    -e GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/sa.json \
    -v $GOOGLE_APPLICATION_CREDENTIALS:/app/sa.json:ro \
    mvilliger/dynatrace-gcp-cloud-sql-trace-fetch:0.1