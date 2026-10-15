# NSS ECM Control (luci-app-nssecm)

Qualcomm NSS ECM 硬件加速引擎的 LuCI 前端，用 JS 编写。

- 中文名：**NSS 硬件加速**（菜单里显示在「网络」下）
- 英文名：**NSS ECM Control**

## 这个包做什么

读写 UCI 配置 `ecm`（`/etc/config/ecm`），并在保存后重启
`/etc/init.d/qca-nss-ecm`。表单包含：

| 选项 | 类型 | 说明 |
|---|---|---|
| `acceleration_engine` | 列表 | 加速引擎模式：Auto / NSS / SFE / PPE / NSS+SFE / PPE+SFE |
| `max_con` | 整数 | 最大 TCP 连接数，范围 1–655350，默认 65535 |
| `bridge_acc` | 开关 | UDP 桥接硬件重定向卸载，默认开 |
| `sfp1_mode` | 列表 | SFP1 端口速率：Auto / 1G / 2.5G / 5G / 10G |
| `sfp2_mode` | 列表 | SFP2 端口速率：同上 |

另有 `wifi_plugin`、`ipv6_acc`、`ovs_acc`、`ovpn_acc`、`mwan_acc` 五个选项保留为注释
（见 `htdocs/luci-static/resources/view/nssecm.js`）。

## 为什么后端仍叫 `ecm`

`/etc/config/ecm` 和 `/etc/init.d/qca-nss-ecm` 由 Qualcomm 的
`kmod-qca-nss-ecm-premium` / `kmod-qca-nss-ecm-wifi-plugin` 包提供，**不属于这个
LuCI 应用**。本应用自身的包名与菜单项用的是 `nssecm`；底层配置与服务名保持原样，
装到真机上即可直接工作。

菜单项带 `depends.uci.ecm`，所以只有装了加速引擎、`/etc/config/ecm` 存在的设备才会
显示这个入口。

## 目录

```
Makefile                                  包定义
htdocs/luci-static/resources/view/nssecm.js   表单视图（JS）
root/usr/share/luci/menu.d/luci-app-nssecm.json  菜单项
root/usr/share/rpcd/acl.d/luci-app-nssecm.json   ACL
root/etc/uci-defaults/luci-nssecm         首次启动：注册 ucitrack
po/zh_Hans/nssecm.po                      简体中文
po/templates/nssecm.pot                   翻译模板
tools/build.sh                            用本地 SDK 构建并列出产物
tools/lmo.py                              .lmo 解码 / 对照 .po 校验
```

## 构建

放进 OpenWrt 构建树（或 SDK）的 `package/` 下：

```sh
make package/luci-app-nssecm/compile V=s
```

产出两个包：`luci-app-nssecm` 与 `luci-i18n-nssecm-zh-cn`。

## 安装

OpenWrt 24.10：

```sh
opkg install luci-app-nssecm_*.ipk
# 中文界面需额外安装翻译包
opkg install luci-i18n-nssecm-zh-cn_*.ipk
```

OpenWrt 25.12：

```sh
apk add --allow-untrusted luci-app-nssecm-*.apk
# 中文界面需额外安装翻译包
apk add --allow-untrusted luci-i18n-nssecm-zh-cn-*.apk
```

## 翻译

简体中文共 22 条，覆盖表单标题、区块与选项标签、下拉项取值，以及视图发出的两条提示
文案；菜单入口复用表单标题那条字符串，因此由同一条目翻译。

## 许可

GPL-3.0-only，见 [LICENSE](LICENSE)。
