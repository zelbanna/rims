"use strict";(self.webpackChunkrims_frontend=self.webpackChunkrims_frontend||[]).push([[166],{166:function(t,e,n){n.r(e),n.d(e,{Inventory:function(){return j},Main:function(){return _},Manage:function(){return y}});var i=n(942),s=n(413),a=n(671),o=n(144),r=n(340),c=n(882),d=n(791),u=n(252),p=n(885),h=n(682),v=n(698),l=n(355),f=n(531),m=n(184),_=function(t){(0,r.Z)(n,t);var e=(0,c.Z)(n);function n(t){var i;return(0,a.Z)(this,n),(i=e.call(this,t)).listItem=function(t){var e="up"===t.ip_state;return[t.hostname,t.type_name,(0,m.jsxs)(m.Fragment,{children:[(0,m.jsx)(p.StateLeds,{state:t.ip_state},"state"),e&&"manage"===t.type_functions&&(0,m.jsx)(h.InfoButton,{onClick:function(){return i.context.changeMain((0,m.jsx)(y,{device_id:t.id,type:t.type_name},"hypervisor_manage_"+t.id))}},"info"),e&&t.url&&t.url.length>0&&(0,m.jsx)(h.UiButton,{onClick:function(){return window.open(t.url,"_blank")}},"ui")]})]},i.state={},i}return(0,o.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,u.Fh)("api/device/list",{field:"base",search:"hypervisor",extra:["type","functions","url"],sort:"hostname"}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;return(0,m.jsxs)(m.Fragment,{children:[(0,m.jsx)(p.ContentList,{header:"Hypervisor",thead:["Hostname","Type",""],trows:this.state.data,listItem:this.listItem,children:(0,m.jsx)(h.SyncButton,{onClick:function(){return t.changeContent((0,m.jsx)(x,{},"vm_sync"))}},"sync")},"cl"),(0,m.jsx)(p.ContentData,{mountUpdate:function(e){return t.changeContent=e}},"cda")]})}}]),n}(d.Component);_.contextType=p.RimsContext;var x=function(t){(0,r.Z)(n,t);var e=(0,c.Z)(n);function n(t){var i;return(0,a.Z)(this,n),(i=e.call(this,t)).listItem=function(t){return[t.type,t.host_id,t.device_id,t.vm,t.bios_uuid,t.config]},i.state={},i}return(0,o.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,u.Fh)("api/device/vm_mapping",{device_id:this.props.device_id}).then((function(e){var n=[];["existing","inventory","discovered","database"].forEach((function(t){e.hasOwnProperty(t)&&e[t].forEach((function(e){e.type=t,n.push(e)}))})),t.setState({data:n})}))}},{key:"render",value:function(){return(0,m.jsx)(p.ContentReport,{header:"VM Mapping",thead:["Status","Host","Device","VM Name","Device UUID","Config"],trows:this.state.data,listItem:this.listItem},"hyp_cr")}}]),n}(d.Component),y=function(t){(0,r.Z)(n,t);var e=(0,c.Z)(n);function n(t){var i;return(0,a.Z)(this,n),(i=e.call(this,t)).changeContent=function(t){return i.setState({content:t})},i.state={},i}return(0,o.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,u.Fh)("api/device/management",{id:this.props.device_id}).then((function(e){t.context.loadNavigation((0,m.jsxs)(l.NavBar,{children:[(0,m.jsx)(l.NavButton,{title:"Inventory",onClick:function(){return t.changeContent((0,m.jsx)(j,{device_id:t.props.device_id,type:t.props.type},"hypervisor_inventory"))}},"hyp_nav_inv"),e.data.url&&e.data.url.length>0&&(0,m.jsx)(l.NavButton,{title:"UI",onClick:function(){return window.open(e.data.url,"_blank")}},"hyp_nav_ui"),(0,m.jsx)(l.NavInfo,{title:e.data.hostname},"hyp_nav_name")]},"hypervisor_navbar")),t.setState((0,s.Z)((0,s.Z)({},e),{},{content:(0,m.jsx)(j,{device_id:t.props.device_id,type:t.props.type},"hypervisor_inventory")}))}))}},{key:"render",value:function(){return(0,m.jsx)(m.Fragment,{children:this.state.content})}}]),n}(d.Component);y.contextType=p.RimsContext;var j=function(t){(0,r.Z)(n,t);var e=(0,c.Z)(n);function n(t){var i;return(0,a.Z)(this,n),(i=e.call(this,t)).sortList=function(t){var e=i.state.data;"name"===t?e.sort((function(t,e){return t.name.localeCompare(e.name)})):e.sort((function(t,e){return t.id-e.id})),i.setState({sort:t})},i.listItem=function(t){return[t.id,t.name,(0,m.jsx)(C,{vm_id:t.id,device_id:i.props.device_id,type:i.props.type,changeContent:function(t){return i.changeContent(t)},state:t.state},"hl_op_"+t.id)]},i.state={sort:"name",searchfield:""},i}return(0,o.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,u.Fh)("api/devices/"+this.props.type+"/inventory",{device_id:this.props.device_id,sort:this.state.sort}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;if(this.state.data){var e=this.state.searchfield,n=0===e.length?this.state.data:this.state.data.filter((function(t){return t.name.toLowerCase().includes(e)})),i=[(0,m.jsx)(h.HeaderButton,{text:"ID",highlight:"id"===this.state.sort,onClick:function(){return t.sortList("id")}},"id"),(0,m.jsx)(h.HeaderButton,{text:"VM",highlight:"name"===this.state.sort,onClick:function(){return t.sortList("name")}},"vm"),"Operations"];return(0,m.jsxs)(m.Fragment,{children:[(0,m.jsxs)(p.ContentList,{header:"Inventory",thead:i,trows:n,listItem:this.listItem,children:[(0,m.jsx)(h.ReloadButton,{onClick:function(){t.setState({data:void 0}),t.componentDidMount()}},"reload"),(0,m.jsx)(h.SyncButton,{onClick:function(){return t.changeContent((0,m.jsx)(x,{device_id:t.props.device_id},"vm_sync"))},title:"Map VMs"},"sync"),(0,m.jsx)(v.SearchField,{searchFire:function(e){return t.setState({searchfield:e})},placeholder:"Search inventory"},"search")]},"cl"),(0,m.jsx)(p.ContentData,{mountUpdate:function(e){return t.changeContent=e}},"cda")]})}return(0,m.jsx)(p.Spinner,{})}}]),n}(d.Component),C=function(t){(0,r.Z)(n,t);var e=(0,c.Z)(n);function n(t){var i;return(0,a.Z)(this,n),(i=e.call(this,t)).operation=function(t){i.setState({wait:(0,m.jsx)(p.Spinner,{})}),(0,u.Fh)("api/devices/"+i.props.type+"/vm_op",{device_id:i.props.device_id,vm_id:i.props.vm_id,op:t}).then((function(t){return i.setState((0,s.Z)((0,s.Z)({},t),{},{wait:null}))}))},i.snapshot=function(t){i.setState({wait:(0,m.jsx)(p.Spinner,{})}),(0,u.Fh)("api/devices/"+i.props.type+"/vm_snapshot",{device_id:i.props.device_id,vm_id:i.props.vm_id,op:t}).then((function(t){return i.setState((0,s.Z)((0,s.Z)({},t),{},{wait:null}))}))},i.state={state:i.props.state,status:"",wait:null},i}return(0,o.Z)(n,[{key:"render",value:function(){var t=this,e="on"===this.state.state,n="off"===this.state.state;return(0,m.jsxs)(m.Fragment,{children:[(0,m.jsx)(h.InfoButton,{onClick:function(){return t.props.changeContent((0,m.jsx)(g,{device_id:t.props.device_id,vm_id:t.props.vm_id,type:t.props.type,changeSelf:t.props.changeContent},"hypervisor_info"))},title:"VM info"},"info"),(n||"suspended"===this.state.state)&&(0,m.jsx)(h.StartButton,{onClick:function(){return t.operation("on")},title:this.state.status},"start"),e&&(0,m.jsx)(h.StopButton,{onClick:function(){return t.operation("shutdown")},title:this.state.status},"stop"),e&&(0,m.jsx)(h.ReloadButton,{onClick:function(){return t.operation("reboot")},title:this.state.status},"reload"),e&&(0,m.jsx)(h.PauseButton,{onClick:function(){return t.operation("suspend")},title:this.state.status},"suspend"),(e||"suspended"===this.state.state)&&(0,m.jsx)(h.ShutdownButton,{onClick:function(){return t.operation("off")},title:this.state.status},"shutdown"),n&&(0,m.jsx)(h.SnapshotButton,{onClick:function(){return t.snapshot("create")},title:"Take snapshot"},"snapshot"),n&&(0,m.jsx)(h.ItemsButton,{onClick:function(){return t.props.changeContent((0,m.jsx)(S,{device_id:t.props.device_id,vm_id:t.props.vm_id,type:t.props.type},"hypervisor_snapshots_"+t.props.vm_id))},title:"Snapshot info"},"snapshots"),this.state.wait]})}}]),n}(d.Component),g=function(t){(0,r.Z)(_,t);var e=(0,c.Z)(_);function _(t){var o;return(0,a.Z)(this,_),(o=e.call(this,t)).onChange=function(t){return o.setState({data:(0,s.Z)((0,s.Z)({},o.state.data),{},(0,i.Z)({},t.target.name,t.target.value))})},o.changeSelf=function(t){return o.props.changeSelf(t)},o.changeContent=function(t){return o.setState({content:t})},o.changeImport=function(t){return n.e(167).then(n.bind(n,167)).then((function(e){return o.setState({content:(0,m.jsx)(e.Info,{device_id:o.state.data.device_id,class:"virtual",mac:t.mac,name:t.name,interface_id:t.interface_id,description:t.port,changeSelf:o.changeContent},"interface_info")})}))},o.state={},o}return(0,o.Z)(_,[{key:"componentDidUpdate",value:function(t){t!==this.props&&this.componentDidMount()}},{key:"componentDidMount",value:function(){var t=this;(0,u.Fh)("api/devices/"+this.props.type+"/vm_info",{device_id:this.props.device_id,vm_id:this.props.vm_id}).then((function(e){null===e.data.device_id&&(e.data.device_id=""),t.setState(e)}))}},{key:"syncDatabase",value:function(){var t=this;(0,u.Fh)("api/devices/"+this.props.type+"/vm_info",{device_id:this.props.device_id,vm_id:this.props.vm_id,op:"update"}).then((function(e){return t.setState(e)}))}},{key:"updateInfo",value:function(){var t=this;(0,u.Fh)("api/devices/"+this.props.type+"/vm_map",{bios_uuid:this.state.data.bios_uuid,device_id:this.state.data.device_id,host_id:this.props.device_id,op:"update"}).then((function(e){return t.setState({update:e.update})}))}},{key:"interfaceButton",value:function(t,e){var n=this;return this.state.data.device_id?e.interface_id?(0,m.jsx)(h.InfoButton,{onClick:function(){return n.changeImport({interface_id:e.interface_id})}},"info"):(0,m.jsx)(h.AddButton,{onClick:function(){return n.changeImport((0,s.Z)((0,s.Z)({},e),{},{interface_id:"new"}))}},"add"):(0,m.jsx)("div",{})}},{key:"render",value:function(){var t=this;if(this.state.data){var e=this.state.data;return(0,m.jsxs)(m.Fragment,{children:[(0,m.jsxs)(p.InfoArticle,{header:"VM info",children:[(0,m.jsxs)(p.InfoColumns,{columns:3,children:[(0,m.jsx)(v.TextLine,{id:"name",text:e.name},"name"),(0,m.jsx)("div",{}),(0,m.jsx)(v.TextInput,{id:"device_id",label:"Device ID",value:e.device_id,onChange:this.onChange},"device_id"),(0,m.jsx)("div",{}),(0,m.jsx)(v.TextLine,{id:"device",label:"Device Name",text:e.device_name},"device_name"),(0,m.jsx)("div",{}),(0,m.jsx)(v.TextLine,{id:"snmp_id",label:"SNMP id",text:e.snmp_id},"snmp"),(0,m.jsx)("div",{}),(0,m.jsx)(v.TextLine,{id:"uuid",label:"UUID",text:e.bios_uuid},"uuid"),(0,m.jsx)("div",{}),(0,m.jsx)(v.StateLine,{id:"state",state:e.state},"state"),(0,m.jsx)("div",{}),(0,m.jsx)(v.TextLine,{id:"config",text:e.config},"config"),(0,m.jsx)("div",{}),Object.entries(this.state.interfaces).map((function(e){return(0,m.jsxs)(d.Fragment,{children:[(0,m.jsx)(v.TextLine,{id:"interface_"+e[0],label:"Interface",text:"".concat(e[1].name," - ").concat(e[1].mac," - ").concat(e[1].port)},"interface"),t.interfaceButton(e[0],e[1])]},e[0])}))]},"hyp_ic"),(0,m.jsx)(h.ReloadButton,{onClick:function(){return t.componentDidMount()},title:"Reload"},"reload"),(0,m.jsx)(h.SaveButton,{onClick:function(){return t.updateInfo()},title:"Save mapping"},"save"),(0,m.jsx)(h.SyncButton,{onClick:function(){return t.syncDatabase()},title:"Resync database with VM info"},"sync"),e.device_id&&(0,m.jsx)(h.GoButton,{onClick:function(){return t.changeSelf((0,m.jsx)(f.Info,{id:e.device_id,changeSelf:t.props.changeSelf},"device_info"))},title:"VM device info"},"go"),(0,m.jsx)(p.Result,{result:JSON.stringify(this.state.update)},"result")]},"hyp_article"),(0,m.jsx)(l.NavBar,{}),this.state.content]})}return(0,m.jsx)(p.Spinner,{})}}]),_}(d.Component),S=function(t){(0,r.Z)(n,t);var e=(0,c.Z)(n);function n(t){var i;return(0,a.Z)(this,n),(i=e.call(this,t)).snapshot=function(t,e){i.setState({wait:(0,m.jsx)(p.Spinner,{})}),(0,u.Fh)("api/devices/"+i.props.type+"/vm_snapshot",{device_id:i.props.device_id,vm_id:i.props.vm_id,op:t,snapshot:e}).then((function(t){return i.setState((0,s.Z)((0,s.Z)({},t),{},{wait:null}))}))},i.deleteList=function(t){window.confirm("Really delete snapshot?")&&(i.setState({wait:(0,m.jsx)(p.Spinner,{})}),(0,u.Fh)("api/devices/"+i.props.type+"/vm_snapshot",{device_id:i.props.device_id,vm_id:i.props.vm_id,op:"remove",snapshot:t}).then((function(e){if(e.deleted){var n=0,s=i.state.data.filter((function(e){return e.id!==t}));s.forEach((function(t){n=n<parseInt(t.id)?parseInt(t.id):n})),i.setState({data:s,highest:n,wait:null})}})))},i.listItem=function(t){return[t.name,t.id,t.desc,t.created,t.state,(0,m.jsxs)(m.Fragment,{children:[(0,m.jsx)(h.RevertButton,{onClick:function(){return i.snapshot("revert",t.id)},title:"Revert to snapshot"},"revert"),(0,m.jsx)(h.DeleteButton,{onClick:function(){return i.deleteList(t.id)},title:"Delete snapshot"},"del")]})]},i.state={},i}return(0,o.Z)(n,[{key:"componentDidMount",value:function(){this.snapshot("list",void 0)}},{key:"render",value:function(){var t=this;return(0,m.jsxs)(p.ContentReport,{header:"Snapshot (".concat(this.props.vm_id,") Highest ID:").concat(this.state.highest),thead:["Name","ID","Description","Created","State",""],trows:this.state.data,listItem:this.listItem,children:[(0,m.jsx)(h.ReloadButton,{onClick:function(){return t.snapshot("list",void 0)},title:"Reload list"},"reload"),this.state.wait]},"hyp_snapshot_cr")}}]),n}(d.Component)}}]);
//# sourceMappingURL=166.3365032a.chunk.js.map