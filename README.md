
Flashflood workspace sample
=============================

This repository provides sample setting of Flashflood environment.


Constructing workspace
------------------------

1. Prepare Python environment and install Flashflood

    see [Flashflood installation](https://github.com/mojaie/flashflood#installation)

1. Clone this sample repository

    ```
    git clone https://github.com/mojaie/flashflood-workspace-sample.git your-home-dir
    ```

1. Install Kiwiii (web application for data visualization) by using npm

    ```
    cd your-home-dir
    npm install kiwiii
    ```

    Or npm link for the client module development.

    ```
    cd your-home-dir
    npm link ../kiwiii
    ```


1. Server configuration

    Open server_config.yaml and edit.
    If you want to activate contrib modules, add the parameter below.

    ```
    externals:
      - "contrib.screenerapi"
    ```


1. Run workflow scripts to build sample databases

    ```
    make chem
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
