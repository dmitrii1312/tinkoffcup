{{- define "scheduler.fullname" -}}
{{- .Chart.Name }}
{{- end }}

{{- define "scheduler.name" -}}
{{- default .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "scheduler.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "scheduler.labels" -}}
helm.sh/chart: {{ include "scheduler.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{ include "scheduler.selectorLabels" . }}
app.kubernetes.io/version: {{ .Values.image.tag | quote | default "" }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "scheduler.selectorLabels" -}}
app.kubernetes.io/name: {{ include "scheduler.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "scheduler.imageName" -}}
{{- $registryName := .Values.image.registry -}}
{{- $tag := .Values.image.tag | toString -}}
{{- printf "%s:%s" $registryName $tag -}}
{{- end -}}

{{/*
Secret name
*/}}
{{- define "scheduler.secretName" -}}
{{- if .Values.secretStorage.existingSecret }}
{{- .Values.secretStorage.existingSecret }}
{{- else }}
{{- include "scheduler.fullname" . }}
{{- end }}
{{- end }}

{{- define "scheduler.url" -}}
{{- $appName := printf "%s" .Values.ingress.overrideAppName | default (include "scheduler.fullname" .) | trimSuffix "-" }}
{{- printf "%s.%s" $appName .Values.ingress.clusterDomainName | trunc 63 | trimSuffix "-" -}}
{{- end }}