
kiwiii workspace sample
==========================

This repository provides sample setting of kiwiii server environment.


Constructing workspace
------------------------

1. Prepare Python environment and install kiwiii-server

    see [kiwiii-server installation](https://github.com/mojaie/kiwiii-server#installation)

1. Clone this sample repository

    ```
    git clone https://github.com/mojaie/kw-workspace-sample.git your-home-dir
    ```

1. Install kiwiii-client by using npm

    ```
    cd your-home-dir
    npm install kiwiii-client
    ```

    Or npm link for the client module development.

    ```
    cd your-home-dir
    npm link ../kiwiii-client
    ```


1. Server configuration

    Open server_config.yaml and edit.

    If you have working copy of the client module, change `web_home` parameter.

    ```
    # web_home: "node_modules/kiwiii-client/dist"
    web_home: "node_modules/kiwiii-client/_build"
    ```

1. Run build scripts for sample databases

    ```
    make chem
    make chemidx
    make assay
    ```

1. Run server

    ```
    make serve
    ```


License
--------------

[MIT license](http://opensource.org/licenses/MIT)

Test datasets provided by [DrugBank](https://www.drugbank.ca/) are permitted to use under [Creative Common’s by-nc 4.0 License](https://creativecommons.org/licenses/by-nc/4.0/legalcode)



Copyright
--------------

(C) 2014-2017 Seiji Matsuoka
