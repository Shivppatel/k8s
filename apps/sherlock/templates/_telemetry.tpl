{{/* Connection-bound peers never grant access for disabled integrations. */}}
{{- define "sherlock.telemetry.sources" -}}
{{- $sources := dict -}}
{{- range $kind := list "prometheus" "loki" "tempo" "grafana" "pyroscope" -}}
{{- range (get $.Values.sherlock.config $kind | default list) -}}
{{- $_ := set $sources .id . -}}
{{- end -}}
{{- end -}}
{{- /* The Alertmanager reconciliation read is a source too: its ID keys a telemetryPeers egress grant. */ -}}
{{- with $.Values.sherlock.config.alertmanager_reconcile -}}
{{- $_ := set $sources .id . -}}
{{- end -}}
{{- $sources | toJson -}}
{{- end -}}
{{- define "sherlock.telemetry.alerts" -}}
{{- $sources := dict -}}
{{- range (.Values.sherlock.config.alertmanager | default list) -}}
{{- $_ := set $sources .id . -}}
{{- end -}}
{{- $sources | toJson -}}
{{- end -}}
