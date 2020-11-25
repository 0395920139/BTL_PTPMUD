from gatco_jinja2 import GatcoJinja2

class Jinja(GatcoJinja2):
    def init_app(self, app, loader=None, pkg_name=None, pkg_path=None):
        super(Jinja, self).init_app(app, loader, pkg_name, pkg_path)
        self.add_env("host_url", app.config.get("HOST", ""))
        self.add_env("static_url", app.config.get("STATIC_URL", ""))
        self.add_env("release_version", app.config.get("RELEASE_VERSION", ""))
        self.add_env("zalo_app_id", app.config.get("ZALO_APP_ID", ""))
