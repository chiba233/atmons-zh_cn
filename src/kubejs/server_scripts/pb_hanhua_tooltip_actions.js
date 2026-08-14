// ATM10 汉化补丁 · 资源蜜蜂 tooltip 汉化 (服务端部分)
// KubeJS 2101 的 modifyTooltips 是服务端事件, 动作列表由服务器同步给客户端;
// 客户端的 client_scripts/pb_hanhua_tooltip.js 里的 dynamicTooltips 负责实际替换。
ItemEvents.modifyTooltips(event => {
    event.modify('productivebees:gene', t => t.dynamic('pb_hanhua'))
    event.modify('productivebees:gene_bottle', t => t.dynamic('pb_hanhua'))
    event.modify('productivebees:bee_cage', t => t.dynamic('pb_hanhua'))
    event.modify('productivebees:sturdy_bee_cage', t => t.dynamic('pb_hanhua'))
})
