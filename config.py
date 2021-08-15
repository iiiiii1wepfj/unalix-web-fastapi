port_str: str = "8000"

app_port = int(
    port_str,
)

app_host: str = "0.0.0.0"

app_title: str = "Unalix-web"

app_description: str = '# links <p>source code: <a href="https://github.com/AmanoTeam/unalix-web-fastapi">https://github.com/AmanoTeam/unalix-web-fastapi</a></p><p>donations: <a href="https://amanoteam.com/donate">https://amanoteam.com/donate</a></p>'

app_version_one: str = "2.0"

app_version_two = float(
    app_version_one,
)

app_version = str(
    app_version_two,
)

log_format = "<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>"

the_license_name: str = "LGPL-3.0 License"

the_license_link: str = "https://www.gnu.org/licenses/lgpl-3.0.en.html"

org_name: str = "AmanoTeam"

org_website: str = "https://amanoteam.com"

org_mail: str = "contact@amanoteam.com"

app_debug_mode: bool = False

unalix_conf_http_timeout_one: str = "10"

unalix_conf_http_timeout = int(
    unalix_conf_http_timeout_one,
)

show_server_errors: bool = False
