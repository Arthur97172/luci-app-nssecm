# NSS ECM Control (luci-app-nssecm)

A JS LuCI front end for Qualcomm's NSS ECM hardware acceleration engine.

- Chinese name: **NSS 硬件加速** (shown under the "Network" menu)
- English name: **NSS ECM Control**

## What it does

It reads and writes the UCI config `ecm` (`/etc/config/ecm`) and restarts
`/etc/init.d/qca-nss-ecm` after saving. The form holds:

| Option | Type | Meaning |
|---|---|---|
| `acceleration_engine` | list | Engine mode: Auto / NSS / SFE / PPE / NSS+SFE / PPE+SFE |
| `max_con` | integer | Max TCP connections, range 1–655350, default 65535 |
| `bridge_acc` | flag | UDP bridge hardware redirect offload, default on |
| `sfp1_mode` | list | SFP1 port speed: Auto / 1G / 2.5G / 5G / 10G |
| `sfp2_mode` | list | SFP2 port speed: same |

Five further options (`wifi_plugin`, `ipv6_acc`, `ovs_acc`, `ovpn_acc`,
`mwan_acc`) are present but commented out — see
`htdocs/luci-static/resources/view/nssecm.js`.

## Why the backend is still called `ecm`

`/etc/config/ecm` and `/etc/init.d/qca-nss-ecm` are provided by Qualcomm's
`kmod-qca-nss-ecm-premium` / `kmod-qca-nss-ecm-wifi-plugin` packages and are
**not part of this LuCI app**. The app's own package name and menu entry use
`nssecm`; the config and service names are kept so the page works as-is on a
real device.

The menu entry carries `depends.uci.ecm`, so it only appears on a device that
has the acceleration engine installed and therefore has `/etc/config/ecm`.

## Layout

```
Makefile                                  package definition
htdocs/luci-static/resources/view/nssecm.js   the form view (JS)
root/usr/share/luci/menu.d/luci-app-nssecm.json  menu entry
root/usr/share/rpcd/acl.d/luci-app-nssecm.json   ACL
root/etc/uci-defaults/luci-nssecm         first boot: register ucitrack
po/zh_Hans/nssecm.po                      Simplified Chinese
po/templates/nssecm.pot                   translation template
tools/build.sh                            build with the local SDK, list artifacts
tools/lmo.py                              decode an .lmo / check it against a .po
```

## Building

Drop it into an OpenWrt buildroot (or SDK) under `package/`:

```sh
make package/luci-app-nssecm/compile V=s
```

This produces two packages: `luci-app-nssecm` and `luci-i18n-nssecm-zh-cn`.

## Installation

OpenWrt 24.10:

```sh
opkg install luci-app-nssecm_*.ipk
# install the translation package as well for a Chinese UI
opkg install luci-i18n-nssecm-zh-cn_*.ipk
```

OpenWrt 25.12:

```sh
apk add --allow-untrusted luci-app-nssecm-*.apk
# install the translation package as well for a Chinese UI
apk add --allow-untrusted luci-i18n-nssecm-zh-cn-*.apk
```

## Translations

Simplified Chinese has 22 entries, covering the form title, the section and
option labels, the dropdown values and the two messages the view emits. The menu
entry reuses the form title string, so it is translated from the same entry.

## License

GPL-3.0-only, see [LICENSE](LICENSE).
