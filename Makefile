#
# Copyright (C) 2026 Arthur97172 <arthur97172@outlook.com>
#
# This is free software, licensed under the GNU General Public License v3.0
# (SPDX: GPL-3.0-only).
#
# NSS ECM Control -- a JS LuCI front end for Qualcomm's NSS ECM acceleration
# engine.
#

include $(TOPDIR)/rules.mk

LUCI_NAME:=luci-app-nssecm
PKG_VERSION:=1.0.0
# 版本约定：每次提交 PKG_RELEASE +1（1.0.0-r1 ~ r9）；
# 达到 r10 时 PKG_VERSION 末位 +1（1.0.0 -> 1.0.1），PKG_RELEASE 重置为 1。
PKG_RELEASE:=1
PKG_LICENSE:=GPL-3.0-only
PKG_LICENSE_FILES:=LICENSE

# LUCI_MAINTAINER, not PKG_MAINTAINER: luci.mk's Package/$(PKG_NAME) sets
# MAINTAINER:=$(LUCI_MAINTAINER) after Package/Default has set it from
# PKG_MAINTAINER, so LUCI_MAINTAINER is the one that reaches the package.
LUCI_MAINTAINER:=Arthur97172 <Arthur97172@users.noreply.github.com>

# Shown as the package's Title. The menu entry the user actually sees is the
# "title" in root/usr/share/luci/menu.d/luci-app-nssecm.json.
#
# All three must stay byte-identical: the menu.d title is translated *only* by
# coinciding with the string the view passes to _() (htdocs/.../nssecm.js),
# because LuCI's i18n scanner collects _() calls from JS/Lua sources and never
# reads menu.d JSON. Themes then render it as _(child.title) -- menu-bootstrap.js
# line 72, and the same in every other theme -- so the catalog entry is what the
# user sees. The zh_Hans catalog renders this string as "NSS 硬件加速".
LUCI_TITLE:=NSS ECM Control

LUCI_DESCRIPTION:=LuCI front end for Qualcomm's NSS ECM (acceleration engine). \
	Configures the acceleration engine mode (NSS / SFE / PPE and the hybrids), \
	the maximum TCP connection count, the UDP bridge hardware redirect offload \
	and the SFP1/SFP2 port speed, then restarts the qca-nss-ecm service.

# +luci-base is the only dependency: every module the view resolves (view, form,
# uci, fs, ui) comes from luci-base's htdocs, and the menu/ACL JSON live under
# root/.
#
# Deliberately NOT depended on: the kmod-qca-nss-ecm-* packages and the
# /etc/init.d/qca-nss-ecm service. They own /etc/config/ecm, and the menu entry
# is hidden until that config exists (depends.uci.ecm in the menu.d file), so on
# a device without the engine the page simply does not appear rather than
# offering switches that do nothing.
LUCI_DEPENDS:=+luci-base

# Simplified Chinese ships as its own luci-i18n-nssecm-zh-cn package. luci.mk
# builds one translation package per directory under ./po, but only for names
# its built-in LUCI_LANG.* table knows, so the directory is po/zh_Hans and
# luci.mk turns it into luci-i18n-nssecm-zh-cn, compiling po/zh_Hans/*.po with
# po2lmo into usr/lib/lua/luci/i18n/nssecm.zh-cn.lmo and registering 简体中文 in
# luci.languages. English needs no file: _() returns the msgid unchanged when
# nothing matches.
#
# Pinned so every package in a release tells the same version; luci.mk assigns
# PKG_PO_VERSION with ?=, so this definition is respected.
PKG_PO_VERSION:=$(PKG_VERSION)-r$(PKG_RELEASE)

include $(TOPDIR)/feeds/luci/luci.mk

# call BuildPackage - OpenWrt buildroot signature
#
# The line above is load bearing: OpenWrt's package scanner finds package
# directories by grepping their Makefile for the literal text "call
# BuildPackage" (include/scan.mk). Without it the package is silently skipped
# and "make package/luci-app-nssecm/compile" fails with "No rule to make
# target". The macro itself is not invoked here -- luci.mk already calls
# BuildPackage for every entry in LUCI_BUILD_PACKAGES.
