'use strict';
'require view';
'require form';
'require uci';
'require fs';
'require ui';

/*
 * NSS ECM Control -- Qualcomm NSS ECM 硬件加速引擎的 JS 版 LuCI 表单。
 *
 * 配置后端刻意保持原样：仍读写 UCI 配置 ecm（/etc/config/ecm），仍在保存后
 * 重启 /etc/init.d/qca-nss-ecm。这两者由 Qualcomm 的 kmod-qca-nss-ecm-* 包提供，
 * 不属于本应用；改名会让页面在真机上失效。
 *
 * 另有五个暂未启用的选项（wifi_plugin / ipv6_acc / ovs_acc / ovpn_acc /
 * mwan_acc）保留为注释；注释里刻意不写 _()，免得被 i18n 扫描器当成有效条目
 * 收进 .pot。
 */

return view.extend({
	load: function() {
		return uci.load('ecm');
	},

	render: function() {
		var m, s, o;

		m = new form.Map('ecm', _('NSS ECM Control'),
			_('Setting NSS ECM Acceleration Engine'));

		s = m.section(form.TypedSection, 'ecm', _('Global Settings'));
		s.anonymous = true;
		s.addremove = false;

		o = s.option(form.ListValue, 'acceleration_engine', _('Acceleration Engine'));
		o.value('auto', _('Auto'));
		o.value('nss', _('NSS Mode'));
		o.value('sfe', _('SFE Mode'));
		o.value('ppe', _('PPE Mode'));
		o.value('nss-sfe', _('NSS+SFE Hydrid Mode'));
		o.value('ppe-sfe', _('PPE+SFE Hydrid Mode'));
		o.default = 'auto';
		o.description = _('Acceleration Engine Mode');

		o = s.option(form.Value, 'max_con', _('Max TCP Connection'));
		o.datatype = 'range(1,655350)';
		o.rmempty = false;
		o.placeholder = '65535';
		o.default = '65535';
		o.description = _('This parameter limits the maximum number of connections that TCP can have open at the same time');

		/* 暂未启用的选项，保留备查：
		o = s.option(form.Flag, 'wifi_plugin', 'Wireless Hardware Acceleration');
		o.default = '1';
		o.description = 'Wireless Hardware Acceleration Plugin';

		o = s.option(form.Flag, 'ipv6_acc', 'IPv6 NAT Hardware Acceleration');
		o.default = '1';
		o.description = 'IPv6 NAT Hardware Acceleration';
		*/

		o = s.option(form.Flag, 'bridge_acc', _('UDP Bridge Hardware Redirect Offload'));
		o.default = '1';
		o.rmempty = false;
		o.description = _('Afford NATloopback/UDP Relay/Docker Network etc.');

		/* 暂未启用的选项，保留备查：
		o = s.option(form.Flag, 'ovs_acc', 'Open vSwitch Acceleration');
		o.default = '1';
		o.description = 'Open vSwitch Acceleration Setting';

		o = s.option(form.Flag, 'ovpn_acc', 'OpenVPN Acceleration');
		o.default = '1';
		o.description = 'OpenVPN Acceleration Setting';

		o = s.option(form.Flag, 'mwan_acc', 'Multi WAN (MWAN3) Acceleration');
		o.default = '1';
		o.description = 'Multi WAN Acceleration Setting';
		*/

		o = s.option(form.ListValue, 'sfp1_mode', _('SFP1 Port Speed Mode'));
		o.value('auto', _('Auto'));
		o.value('1000', _('Force 1Gbps'));
		o.value('2500', _('Force 2.5Gbps'));
		o.value('5000', _('Force 5Gbps'));
		o.value('10000', _('Force 10GBps'));
		o.default = 'auto';

		o = s.option(form.ListValue, 'sfp2_mode', _('SFP2 Port Speed Mode'));
		o.value('auto', _('Auto'));
		o.value('1000', _('Force 1Gbps'));
		o.value('2500', _('Force 2.5Gbps'));
		o.value('5000', _('Force 5Gbps'));
		o.value('10000', _('Force 10GBps'));
		o.default = 'auto';

		return m.render();
	},

	/*
	 * 提交后重启 ECM 服务。
	 *
	 * handleSaveApply 本来就返回 Promise，直接串起来即可，也能把失败暴露到页面上；
	 * 但重启会短暂打断转发，故放到保存成功之后，且不因失败而回滚已提交的配置。
	 */
	handleSaveApply: function(ev, mode) {
		return this.super('handleSaveApply', [ ev, mode ]).then(function() {
			return fs.exec('/etc/init.d/qca-nss-ecm', [ 'restart' ]).catch(function(err) {
				ui.addNotification(null,
					E('p', _('Configuration saved, but restarting the ECM service failed: %s').format(err.message)),
					'warning');
			});
		});
	}
});
