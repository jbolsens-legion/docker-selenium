+++
title = "Selenium Grid Scaler"
availability = "v2.4+"
maintainer = "Volvo Cars, SeleniumHQ"
category = "Testing"
description = "Scales Selenium browser nodes based on number of requests waiting in session queue"
go_file = "selenium_grid_scaler"
+++

### Trigger Specification

This specification describes the `selenium-grid` trigger that scales browser nodes based on number of requests in session queue and the max sessions per grid.

The scaler creates one browser node per pending request in session queue, divided by the max amount of sessions that can run in parallel. You will have to create one trigger per browser capability that you would like to support in your Selenium Grid.

The below is an example trigger configuration for chrome node.

```yaml
triggers:
  - type: selenium-grid
    metadata:
      url: 'http://selenium-hub:4444/graphql' # Required. Can be ommitted if specified via TriggerAuthentication/ClusterTriggerAuthentication.
      browserName: 'chrome'  # Required
      browserVersion: '91.0' # Optional. Only required when supporting multiple versions of browser in your Selenium Grid.
      unsafeSsl : 'true' # Optional
      activationThreshold: 5 # Optional
      platformName: 'Linux' # Optional
```

**Parameter list:**

- `url` - Graphql url of your Selenium Grid. Refer to the Selenium Grid's documentation [here](https://www.selenium.dev/documentation/en/grid/grid_4/graphql_support/) to for more info. If endpoint requires authentication, you can use `TriggerAuthentication` to provide the credentials instead of embedding in the URL.
- `browserName` - Name of browser that usually gets passed in the browser capability. Refer to the [Selenium Grid's](https://www.selenium.dev/documentation/en/getting_started_with_webdriver/browsers/) and [WebdriverIO's](https://webdriver.io/docs/options/#capabilities) documentation for more info.
- `sessionBrowserName` -  Name of the browser when it is an active session, only set if `BrowserName` changes between the queue and the active session. See the Edge example below for further detail. (Optional)
- `browserVersion` - Version of browser that usually gets passed in the browser capability. Refer to the [Selenium Grid's](https://www.selenium.dev/documentation/en/getting_started_with_webdriver/browsers/) and [WebdriverIO's](https://webdriver.io/docs/options/#capabilities) documentation for more info. (Optional)
- `unsafeSsl` - Skip certificate validation when connecting over HTTPS. (Values: `true`, `false`, Default: `false`, Optional)
- `activationThreshold` - Target value for activating the scaler. Learn more about activation [here](./../concepts/scaling-deployments.md#activating-and-scaling-thresholds). (Default: `0`, Optional)
- `platformName` - Name of the browser platform. Refer to the [Selenium Grid's](https://www.selenium.dev/documentation/en/getting_started_with_webdriver/browsers/) and [WebdriverIO's](https://webdriver.io/docs/options/#capabilities) documentation for more info. (Default: `Linux`, Optional)
- `nodeMaxSessions` - Number of maximum sessions that can run in parallel on a Node. Update this parameter align with node config `--max-sessions` (`SE_NODE_MAX_SESSIONS`) to have the correct scaling behavior. (Default: `1`, Optional).
- `targetQueueLength` - The target number of queued sessions to scale on. (Default: `1`, Optional).

**Trigger Authentication**
- `username` - Username for basic authentication in GraphQL endpoint instead of embedding in the URL. (Optional)
- `password` - Password for basic authentication in GraphQL endpoint instead of embedding in the URL. (Optional)
- `authType` - Type of authentication to be used. This can be set to `Bearer` or `OAuth2` in case Selenium Grid behind an Ingress proxy with other authentication types. (Optional)
- `accessToken` - Access token. This is required when `authType` is set a value. (Optional)

### How does it work?

The scaler will query the Hub GraphQL response to get the number of queued sessions in the specified combination of browser name, version, and platform. If the number of queued sessions is **equal to or greater than** the `targetQueueLength`, the scaler will scale up.

### Example

Here is a full example of scaled object definition using Selenium Grid trigger:

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: selenium-grid-chrome-scaledobject
  namespace: keda
  labels:
    deploymentName: selenium-chrome-node
spec:
  maxReplicaCount: 8
  scaleTargetRef:
    name: selenium-chrome-node
  triggers:
    - type: selenium-grid
      metadata:
        url: 'http://selenium-hub:4444/graphql'
        browserName: 'chrome'
```

The above example will create Chrome browser nodes equal to the requests pending in session queue for Chrome browser.

Similarly for Firefox

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: selenium-grid-firefox-scaledobject
  namespace: keda
  labels:
    deploymentName: selenium-firefox-node
spec:
  maxReplicaCount: 8
  scaleTargetRef:
    name: selenium-firefox-node
  triggers:
    - type: selenium-grid
      metadata:
        url: 'http://selenium-hub:4444/graphql'
        browserName: 'firefox'
```

Similarly for Edge. Note that for Edge you must set the `sessionBrowserName` to `msedge` inorder for scaling to work properly.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: selenium-grid-edge-scaledobject
  namespace: keda
  labels:
    deploymentName: selenium-edge-node
spec:
  maxReplicaCount: 8
  scaleTargetRef:
    name: selenium-edge-node
  triggers:
    - type: selenium-grid
      metadata:
        url: 'http://selenium-hub:4444/graphql'
        browserName: 'MicrosoftEdge'
        sessionBrowserName: 'msedge'
```

In case you want to scale from 0 (`minReplicaCount: 0`), and browser nodes are configured different `--max-sessions` greater than 1, you can set `nodeMaxSessions` for scaler align with number of slots available per node to have the correct scaling behavior.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: selenium-grid-chrome-scaledobject
  namespace: keda
  labels:
    deploymentName: selenium-chrome-node
spec:
  maxReplicaCount: 8
  scaleTargetRef:
    name: selenium-chrome-node
  triggers:
    - type: selenium-grid
      metadata:
        url: 'http://selenium-hub:4444/graphql'
        browserName: 'chrome'
        nodeMaxSessions: 4
```

If you are supporting multiple versions of browser capability in your Selenium Grid, You should create one scaler for every browser version and pass the `browserVersion` in the metadata.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: selenium-grid-chrome-91-scaledobject
  namespace: keda
  labels:
    deploymentName: selenium-chrome-node-91
spec:
  maxReplicaCount: 8
  scaleTargetRef:
    name: selenium-chrome-node-91
  triggers:
    - type: selenium-grid
      metadata:
        url: 'http://selenium-hub:4444/graphql'
        browserName: 'chrome'
        browserVersion: '91.0'
```

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: selenium-grid-chrome-90-scaledobject
  namespace: keda
  labels:
    deploymentName: selenium-chrome-node-90
spec:
  maxReplicaCount: 8
  scaleTargetRef:
    name: selenium-chrome-node-90
  triggers:
    - type: selenium-grid
      metadata:
        url: 'http://selenium-hub:4444/graphql'
        browserName: 'chrome'
        browserVersion: '90.0'
```

### Authentication Parameters

It is possible to specify the Graphql url of your Selenium Grid using authentication parameters. This useful if you have enabled Selenium Grid's Basic HTTP Authentication and would like to keep your credentials secure.

- `url` - Graphql url of your Selenium Grid. Refer to the Selenium Grid's documentation [here](https://www.selenium.dev/documentation/en/grid/grid_4/graphql_support/) for more info.
- `username` - Username for basic authentication in GraphQL endpoint instead of embedding in the URL. (Optional)
- `password` - Password for basic authentication in GraphQL endpoint instead of embedding in the URL. (Optional)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: selenium-grid-secret
  namespace: keda
type: Opaque
data:
  graphql-url: base64 encoded value of GraphQL URL
  graphql-username: base64 encoded value of GraphQL Username
  graphql-password: base64 encoded value of GraphQL Password
---
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: keda-trigger-auth-selenium-grid-secret
  namespace: keda
spec:
  secretTargetRef:
  - parameter: url
    name: selenium-grid-secret
    key: graphql-url
  - parameter: username
    name: selenium-grid-secret
    key: graphql-username
  - parameter: password
    name: selenium-grid-secret
    key: graphql-password
---
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: selenium-grid-chrome-scaledobject
  namespace: keda
  labels:
    deploymentName: selenium-chrome-node
spec:
  maxReplicaCount: 8
  scaleTargetRef:
    name: selenium-chrome-node
  triggers:
    - type: selenium-grid
      metadata:
        browserName: 'chrome'
      authenticationRef:
        name: keda-trigger-auth-selenium-grid-secret
```
