# User

Types:

```python
from tekimax.types import UserAutoDetectModalityProfileResponse
```

Methods:

- <code title="post /v1/user/modality-profile">client.user.<a href="./src/tekimax/resources/user.py">auto_detect_modality_profile</a>(\*\*<a href="src/tekimax/types/user_auto_detect_modality_profile_params.py">params</a>) -> <a href="./src/tekimax/types/user_auto_detect_modality_profile_response.py">UserAutoDetectModalityProfileResponse</a></code>

# StreamLearningContent

Types:

```python
from tekimax.types import StreamLearningContentCreateResponse
```

Methods:

- <code title="post /v1/stream-learning-content">client.stream_learning_content.<a href="./src/tekimax/resources/stream_learning_content.py">create</a>(\*\*<a href="src/tekimax/types/stream_learning_content_create_params.py">params</a>) -> <a href="./src/tekimax/types/stream_learning_content_create_response.py">StreamLearningContentCreateResponse</a></code>

# ContestOutcome

Types:

```python
from tekimax.types import ContestOutcomeCreateResponse
```

Methods:

- <code title="post /v1/contest-outcome">client.contest_outcome.<a href="./src/tekimax/resources/contest_outcome.py">create</a>(\*\*<a href="src/tekimax/types/contest_outcome_create_params.py">params</a>) -> <a href="./src/tekimax/types/contest_outcome_create_response.py">ContestOutcomeCreateResponse</a></code>

# Redress

Types:

```python
from tekimax.types import RedressTriggerResponse
```

Methods:

- <code title="post /v1/redress/trigger">client.redress.<a href="./src/tekimax/resources/redress.py">trigger</a>(\*\*<a href="src/tekimax/types/redress_trigger_params.py">params</a>) -> <a href="./src/tekimax/types/redress_trigger_response.py">RedressTriggerResponse</a></code>

# Provenance

Types:

```python
from tekimax.types import ProvenanceRetrieveResponse
```

Methods:

- <code title="get /v1/provenance/{interaction_id}">client.provenance.<a href="./src/tekimax/resources/provenance.py">retrieve</a>(interaction_id) -> <a href="./src/tekimax/types/provenance_retrieve_response.py">ProvenanceRetrieveResponse</a></code>

# Signoff

Types:

```python
from tekimax.types import SignoffCreateResponse
```

Methods:

- <code title="post /v1/signoff">client.signoff.<a href="./src/tekimax/resources/signoff.py">create</a>(\*\*<a href="src/tekimax/types/signoff_create_params.py">params</a>) -> <a href="./src/tekimax/types/signoff_create_response.py">SignoffCreateResponse</a></code>

# Transparency

Types:

```python
from tekimax.types import TransparencyRetrieveResponse
```

Methods:

- <code title="get /v1/transparency/{interaction_id}">client.transparency.<a href="./src/tekimax/resources/transparency.py">retrieve</a>(interaction_id) -> <a href="./src/tekimax/types/transparency_retrieve_response.py">TransparencyRetrieveResponse</a></code>

# Metrics

Types:

```python
from tekimax.types import MetricRetrieveDashboardResponse
```

Methods:

- <code title="get /v1/metrics/dashboard">client.metrics.<a href="./src/tekimax/resources/metrics.py">retrieve_dashboard</a>() -> <a href="./src/tekimax/types/metric_retrieve_dashboard_response.py">MetricRetrieveDashboardResponse</a></code>

# AttributionReport

Types:

```python
from tekimax.types import AttributionReportRetrieveResponse
```

Methods:

- <code title="get /v1/attribution-report">client.attribution_report.<a href="./src/tekimax/resources/attribution_report.py">retrieve</a>(\*\*<a href="src/tekimax/types/attribution_report_retrieve_params.py">params</a>) -> <a href="./src/tekimax/types/attribution_report_retrieve_response.py">AttributionReportRetrieveResponse</a></code>

# ActivityLog

Types:

```python
from tekimax.types import ActivityLogListResponse
```

Methods:

- <code title="get /v1/activity-log">client.activity_log.<a href="./src/tekimax/resources/activity_log.py">list</a>(\*\*<a href="src/tekimax/types/activity_log_list_params.py">params</a>) -> <a href="./src/tekimax/types/activity_log_list_response.py">ActivityLogListResponse</a></code>

# Agent

Types:

```python
from tekimax.types import AgentListToolsResponse, AgentOrchestrateResponse
```

Methods:

- <code title="get /v1/agent/tools">client.agent.<a href="./src/tekimax/resources/agent.py">list_tools</a>() -> <a href="./src/tekimax/types/agent_list_tools_response.py">AgentListToolsResponse</a></code>
- <code title="post /v1/agent/orchestrate">client.agent.<a href="./src/tekimax/resources/agent.py">orchestrate</a>(\*\*<a href="src/tekimax/types/agent_orchestrate_params.py">params</a>) -> <a href="./src/tekimax/types/agent_orchestrate_response.py">AgentOrchestrateResponse</a></code>
