{{/* Explicit ordered profile: these aliases are stable digest inputs and mounted keys. */}}
{{- define "sherlock.ai.documents" -}}
{{- $docs := list (dict "name" "response.md" "path" "ai/response.md") (dict "name" "AGENTS.md" "path" "ai/AGENTS.md") (dict "name" "telemetry-SKILL.md" "path" "ai/skills/sherlock-telemetry/SKILL.md") (dict "name" "gitops-SKILL.md" "path" "ai/skills/sherlock-gitops/SKILL.md") -}}
{{- $docs | toJson -}}
{{- end -}}
{{- define "sherlock.ai.profile" -}}
{{- $parts := list (.Files.Get "ai/guardrails-reference.md") -}}
{{- range $doc := (include "sherlock.ai.documents" . | fromJsonArray) -}}
{{- $content := $.Files.Get $doc.path -}}
{{- if or (eq $content "") (gt (len $content) 16000) -}}{{- fail "AI document unavailable or exceeds 16KB" -}}{{- end -}}
{{- $parts = append $parts (printf "Operator document: %s\n%s" $doc.name $content) -}}
{{- end -}}
{{- $instructions := join "\n\n" $parts -}}
{{- if gt (len $instructions) 24000 -}}{{- fail "AI profile exceeds 24KB" -}}{{- end -}}
{{- $instructions | sha256sum -}}
{{- end -}}
