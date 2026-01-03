"""cli main入口"""

from cyclopts import App

from .provider import provider_app

app = App()

# cyclopts默认把--help和--version放在'Commands' group里，但这样不符合cli的习惯
# Change the group of "--help" and "--version" to the implicitly created "Admin" group.
app["--help"].group = "Cli info options"
app["--version"].group = "Cli info options"

# Child app inherits parent's settings
provider_app = app.command(provider_app, "provider")


@app.default()
def _root_cmd():
    """
    One click install app on some cloud.

    ## Examples

    ```bash
    applab provider list
    applab provider info qcloud
    applab provider login qcloud
    applab zone list --provider qcloud
    applab install docker --provider qcloud --zone ap-shanghai-1
    applab x docker install --provider qcloud --zone ap-shanghai-1

    applab app list --provider qcloud --zone ap-shanghai-1
    applab app list --provider qcloud
    ```

    """
    # if help
    app.help_print()


def main():
    app()


#
if __name__ == "__main__":
    main()
