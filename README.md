
kiwiii workspace sample
==========================

This repository provides sample setting of kiwiii server environment.


Constructing workspace
------------------------

1. Prepare Python environment and install kiwiii-server

  see kiwiii-server installation

1. Clone this sample repository

  ```
  git clone https://github.com/mojaie/kw-workspace-sample.git your-home-dir
  ```

1. Install kiwiii-client by using npm

  ```
  cd your-home-dir
  npm install kiwiii-client
  ```

1. Run build scripts for sample database

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
