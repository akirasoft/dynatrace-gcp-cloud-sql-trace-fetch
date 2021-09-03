# dynatrace-gcp-cloud-sql-trace-fetch
fetch traces from GCP Cloud SQL and import into Dynatrace

Create a service account that has the cloudtrace.traces.list and cloudtrace.traces.get permissions and download the json service account information

Deploy an OpenTelemetry Collector configured to receive Zipkin spans and send OLTP to Dynatrace. A sample config.yaml is present in this repo.

Create three environment variables:

export GOOGLE_CLOUD_PROJECT="your-project-name"
export GOOGLE_APPLICATION_CREDENTIALS="your-service-account.json"
export OPENTEL_COLLECTOR_HTTP="http://otel-collector-host:9411/api/v2/spans"

install python 3.9 and install the python requirements via pip install -r requirements.txt

then simply run main.py, this will fetch all traces and send them to the OTEL collector, the otel collector will then forward them on to Dynatrace. 