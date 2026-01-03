from amsdal.contrib.app_config import AppConfig


class AmsdalLangGraphAppConfig(AppConfig):
    name = 'amsdal_langgraph'
    verbose_name = 'AMSDAL Workflow Plugin'

    def on_ready(self) -> None: ...
