from uuid import UUID

import pandas as pd

from ...clients.cozo import client
from ...common.utils.cozo import cozo_process_mutate_data
from ...common.utils.datetime import utcnow


def patch_agent_query(
    agent_id: UUID,
    developer_id: UUID,
    default_settings: dict = {},
    **update_data,
) -> pd.DataFrame:
    # Agent update query
    agent_update_cols, agent_update_vals = cozo_process_mutate_data(
        {
            **{k: v for k, v in update_data.items() if v is not None},
            "agent_id": str(agent_id),
            "developer_id": str(developer_id),
            "updated_at": utcnow().timestamp(),
        }
    )

    agent_update_query = f"""
    {{
        # update the agent
        ?[{agent_update_cols}] <- $agent_update_vals

        :update agents {{
            {agent_update_cols}
        }}
        :returning
    }}
    """

    # Settings update query
    settings_cols, settings_vals = cozo_process_mutate_data(
        {
            **default_settings,
            "agent_id": agent_id,
        }
    )

    settings_update_query = f"""
    {{
        # update the agent settings
        ?[{settings_cols}] <- $settings_vals

        :update agent_default_settings {{
            {settings_cols}
        }}
    }}
    """

    # Combine the queries
    queries = [agent_update_query]

    if len(default_settings) != 0:
        queries.insert(0, settings_update_query)

    combined_query = "\n".join(queries)

    return client.run(
        combined_query,
        {"agent_update_vals": agent_update_vals, "settings_vals": settings_vals},
    )