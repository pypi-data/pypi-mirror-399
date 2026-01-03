def get_provider_info():
    return {
        "package-name": "airflow-lark-provider",
        "name": "Lark Provider for Apache Airflow",
        "description": "Provider for Lark (Feishu) bot webhook integration",
        "connection-types": [
            {
                "connection-type": "lark_webhook",
                "hook-class": "airflow_lark_provider.hooks.lark_webhook_hook.LarkWebhookHook",
            }
        ],
        "extra-links": [],
        "versions": ["1.0.0"],
    }