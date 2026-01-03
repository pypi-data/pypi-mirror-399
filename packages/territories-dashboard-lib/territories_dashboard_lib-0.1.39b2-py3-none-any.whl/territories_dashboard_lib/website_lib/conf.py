from territories_dashboard_lib.website_lib.models import MainConf


class MissingMainConf(Exception):
    def __init__(self):
        super().__init__()
        self.message = "Configuration principale du site (MainConf) manquante, veuillez la créer via le backoffice ou le shell."


def get_main_conf():
    main_conf = MainConf.objects.first()
    if main_conf is None:
        raise MissingMainConf
    return main_conf
