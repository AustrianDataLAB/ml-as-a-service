# Persistence Service Helm Chart

## Prerequisites
- [Helm](https://github.com/helm/helm/releases)
- [Helmify](https://github.com/arttor/helmify?tab=readme-ov-file)

## Create Helm Chart

- Run ``helmify -f ./../k8s persistence`` from within the helm directory to generate chart
- Adapt created templates and values-file to your own liking (Note: secret values are left empty in the generated values-file!)
- Run ``helm package persistence`` to package generated chart

## Install Helm Chart
- Run ``helm install persistence ./persistence-0.1.0.tgz`` to install from packaged helm chart, alternatively run ``helm install persistence ./persistence`` to install from chart directory.

## Uninstall Helm Chart
- Run ``helm uninstall persistence``

## TODO
- Remove azurite from helmchart
- Include other services in helmchart
- Adapt generated template (decide what to keep configurable)
- Push helmchart to a registry
