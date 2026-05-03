from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook

SLACK_CONN_ID = "slack_webhook"


def slack_failure_callback(context: dict) -> None:
    """Send a Slack alert when any task fails.

    Setup (Airflow UI → Admin → Connections):
      Conn Id   : slack_webhook
      Conn Type : Slack Webhook
      Password  : https://hooks.slack.com/services/T.../B.../...
    """
    ti = context["task_instance"]
    dag_id = ti.dag_id
    task_id = ti.task_id
    execution_date = context["logical_date"].strftime("%Y-%m-%d %H:%M UTC")
    log_url = ti.log_url
    exception = str(context.get("exception", "N/A"))[:300]

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":red_circle:  Airflow Task Failed",
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*DAG*\n`{dag_id}`"},
                {"type": "mrkdwn", "text": f"*Task*\n`{task_id}`"},
                {"type": "mrkdwn", "text": f"*Execution Date*\n{execution_date}"},
                {"type": "mrkdwn", "text": f"*Error*\n```{exception}```"},
            ],
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View Logs"},
                    "url": log_url,
                    "style": "danger",
                }
            ],
        },
    ]

    SlackWebhookHook(slack_webhook_conn_id=SLACK_CONN_ID).send(
        blocks=blocks,
        text=f":red_circle: `{task_id}` in `{dag_id}` failed on {execution_date}",
    )
