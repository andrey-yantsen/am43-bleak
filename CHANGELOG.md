# Changelog

## 0.1.0 (2023-06-10)


### ⚠ BREAKING CHANGES

* rename DeviceDiameter
* rename some of the settings
* nicer API for updating device time
* hide some of the fields
* merge messages into single class

### Features

* add another settings command & fix timers toggling ([e3e354c](https://github.com/andrey-yantsen/am43-bleak/commit/e3e354c44d9330311d0ae712791a98a416487eb5))
* add handling reset ([e52946d](https://github.com/andrey-yantsen/am43-bleak/commit/e52946d89624ab12fda61183aa5ae6cd7f34e153))
* add is_fully_configures for simplifying bootstrapping ([dbb6aa9](https://github.com/andrey-yantsen/am43-bleak/commit/dbb6aa96143df74576ee6680aee332baa1dbb053))
* initial commit, adding most of the protocol ([6a2488f](https://github.com/andrey-yantsen/am43-bleak/commit/6a2488f42cb35598f23d1531cd1665c375bb5ba0))


### Bug Fixes

* better handling for timers updating ([bf0b3e3](https://github.com/andrey-yantsen/am43-bleak/commit/bf0b3e3201dcaa722a7e7d8b334a09d150e1a18c))
* raise an error on incomplete Result message ([c6276a7](https://github.com/andrey-yantsen/am43-bleak/commit/c6276a7520888c19ea8ea080eeb073f1acb9e1c3))


### Documentation

* add a device's photo to readme ([ee823e9](https://github.com/andrey-yantsen/am43-bleak/commit/ee823e96933eeb4ffa0c47d1d31213efc58a1317))


### Miscellaneous

* **deps:** update bleak, pytest-cov & pytest-asyncio ([3fca5e4](https://github.com/andrey-yantsen/am43-bleak/commit/3fca5e4ccefea077a2454944b8e1a4ff468564b9))


### Code Refactoring

* hide some of the fields ([3ad98f6](https://github.com/andrey-yantsen/am43-bleak/commit/3ad98f60ec705d04062f6d35b4849777c9b9818e))
* merge messages into single class ([43ea9d7](https://github.com/andrey-yantsen/am43-bleak/commit/43ea9d732dd87fb9e5c32509ffd19c59e667e8ed))
* nicer API for updating device time ([2ac5cc0](https://github.com/andrey-yantsen/am43-bleak/commit/2ac5cc020bae4e3b2bcbd430a760fb30018f8bfa))
* rename DeviceDiameter ([4cd31be](https://github.com/andrey-yantsen/am43-bleak/commit/4cd31be1d4e68a8673af6b1c63d2b833cab1e106))
* rename some of the settings ([52575bf](https://github.com/andrey-yantsen/am43-bleak/commit/52575bff3174e887962e68d218aec42f0621e0df))
