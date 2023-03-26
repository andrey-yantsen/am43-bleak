# Python AM43 (bluetooth) driver

## What's this?

Python library for controlling blind motors, build on top of A-OK AM43.
This blinds are distributed by Zemismart, Moes and probably other resellers.

In general, the device looks like this:

![image](https://user-images.githubusercontent.com/629281/226755076-cfbfc160-7ca9-4302-b921-e3710e8b038c.png)

## Current project status and todo

- [ ] Protocol
  - [x] Authentication
  - [x] Controling the blinds
  - [x] Changing the device's settings (incl. name, password & current time)
  - [x] Reading/updating timers
  - [x] Reading/updating seasons
  - [x] Reading battery status, blind position, illuminance levels
  - [ ] Validation of the parameters
  - [ ] Check if there're any changes in responses when connected to charger
  - [ ] Full protocol support
    - [ ] 0xA3 (Speed) notification
    - [ ] 0xA6 (Fault) notification
    - [x] Support for client-side messages without checksum
    - [x] Client-side confirmations for some of the messages
  - [ ] Documentation for everything
- [ ] API Wrapper
  - [ ] Device discovery
  - [ ] Connecting to a device
  - [ ] Basic controls: open/close/set position
  - [ ] Display battery level
  - [ ] Changing the configured device's settings
  - [ ] Setting up a non-configured device
- [ ] Tests
- [ ] Nice and easy releases

## Contribution

You can find the contribution documentation in the [CONTRIBUTING.md](./CONTRIBUTING.md) file.
