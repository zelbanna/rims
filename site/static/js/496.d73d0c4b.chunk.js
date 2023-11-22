"use strict";(self.webpackChunkrims_frontend=self.webpackChunkrims_frontend||[]).push([[496,208],{208:function(t,n,e){e.r(n),e.d(n,{Info:function(){return x},List:function(){return v}});var i=e(942),a=e(413),o=e(671),r=e(144),c=e(340),s=e(882),u=e(791),l=e(252),d=e(885),h=e(682),f=e(698),p=e(184),v=function(t){(0,c.Z)(e,t);var n=(0,s.Z)(e);function e(t){var i;return(0,o.Z)(this,e),(i=n.call(this,t)).deleteList=function(t){return window.confirm("Really delete location?")&&(0,l.Fh)("api/location/delete",{id:t}).then((function(n){n.deleted&&(i.setState({data:i.state.data.filter((function(n){return n.id!==t}))}),i.changeContent(null))}))},i.listItem=function(t){return[t.id,t.name,(0,p.jsxs)(p.Fragment,{children:[(0,p.jsx)(h.ConfigureButton,{onClick:function(){return i.changeContent((0,p.jsx)(x,{id:t.id},"location"))},title:"Edit location"},"conf"),(0,p.jsx)(h.DeleteButton,{onClick:function(){return i.deleteList(t.id)},title:"Delete location"},"del")]})]},i.state={},i}return(0,r.Z)(e,[{key:"componentDidMount",value:function(){var t=this;(0,l.Fh)("api/location/list").then((function(n){return t.setState(n)}))}},{key:"render",value:function(){var t=this;return(0,p.jsxs)(p.Fragment,{children:[(0,p.jsxs)(d.ContentList,{header:"Locations",thead:["ID","Name",""],trows:this.state.data,listItem:this.listItem,children:[(0,p.jsx)(h.ReloadButton,{onClick:function(){return t.componentDidMount()}},"reload"),(0,p.jsx)(h.AddButton,{onClick:function(){return t.changeContent((0,p.jsx)(x,{id:"new"},"location"))},title:"Add location"},"add")]},"cl"),(0,p.jsx)(d.ContentData,{mountUpdate:function(n){return t.changeContent=n}},"cda")]})}}]),e}(u.Component),x=function(t){(0,c.Z)(e,t);var n=(0,s.Z)(e);function e(t){var r;return(0,o.Z)(this,e),(r=n.call(this,t)).onChange=function(t){return r.setState({data:(0,a.Z)((0,a.Z)({},r.state.data),{},(0,i.Z)({},t.target.name,t.target.value))})},r.updateInfo=function(){return(0,l.Fh)("api/location/info",(0,a.Z)({op:"update"},r.state.data)).then((function(t){return r.setState(t)}))},r.state={data:null,found:!0},r}return(0,r.Z)(e,[{key:"componentDidUpdate",value:function(t,n){t!==this.props&&this.componentDidMount()}},{key:"componentDidMount",value:function(){var t=this;(0,l.Fh)("api/location/info",{id:this.props.id}).then((function(n){return t.setState(n)}))}},{key:"render",value:function(){var t=this;return this.state.found?this.state.data?(0,p.jsxs)(d.InfoArticle,{header:"Location",children:[(0,p.jsx)(d.InfoColumns,{children:(0,p.jsx)(f.TextInput,{id:"name",value:this.state.data.name,onChange:this.onChange},"name")},"ic"),(0,p.jsx)(h.SaveButton,{onClick:function(){return t.updateInfo()},title:"Save"},"save")]},"ia_loc"):(0,p.jsx)(d.Spinner,{}):(0,p.jsxs)(d.InfoArticle,{children:["Location id: ",this.props.id," removed"]},"ia_loc")}}]),e}(u.Component)},496:function(t,n,e){e.r(n),e.d(n,{Infra:function(){return D},Layout:function(){return Z},List:function(){return I},Main:function(){return g}});var i=e(942),a=e(413),o=e(671),r=e(144),c=e(340),s=e(882),u=e(791),l=e(252),d=e(885),h=e(698),f=e(682),p=e(355),v="rack_rack__l-0E+",x="rack_rackLeft__jopWv",m="rack_rackRight__cbJDU",k="rack_rackItem__UiGLd",_=e(531),C=e(208),j=e(184),g=function(t){(0,c.Z)(e,t);var n=(0,s.Z)(e);function e(t){var i;return(0,o.Z)(this,e),(i=n.call(this,t)).compileNavItems=function(){return i.context.loadNavigation((0,j.jsxs)(p.NavBar,{children:[(0,j.jsxs)(p.NavDropDown,{title:"Rack",children:[(0,j.jsx)(p.NavDropButton,{title:"Racks",onClick:function(){return i.changeContent((0,j.jsx)(I,{},"rack_list"))}},"dev_nav_all_rack"),(0,j.jsx)(p.NavDropButton,{title:"PDUs",onClick:function(){return i.changeContent((0,j.jsx)(D,{type:"pdu"},"pdu_list"))}},"dev_nav_all_pdu"),(0,j.jsx)(p.NavDropButton,{title:"Consoles",onClick:function(){return i.changeContent((0,j.jsx)(D,{type:"console"},"console_list"))}},"dev_nav_all_con")]},"dev_nav_racks"),(0,j.jsx)(p.NavButton,{title:"Locations",onClick:function(){return i.changeContent((0,j.jsx)(C.List,{},"location_list"))}},"dev_nav_loc")]},"rack_navbar"))},i.changeContent=function(t){return i.setState(t)},i.state=(0,j.jsx)(I,{},"rack_list"),i}return(0,r.Z)(e,[{key:"componentDidMount",value:function(){this.compileNavItems()}},{key:"componentDidUpdate",value:function(t){t!==this.props&&this.compileNavItems()}},{key:"render",value:function(){return(0,j.jsx)(j.Fragment,{children:this.state})}}]),e}(u.Component);g.contextType=d.RimsContext;var I=function(t){(0,c.Z)(e,t);var n=(0,s.Z)(e);function e(t){var i;return(0,o.Z)(this,e),(i=n.call(this,t)).listItem=function(t){return[(0,j.jsx)(f.HrefButton,{text:t.location,onClick:function(){return i.changeContent((0,j.jsx)(C.Info,{id:t.location_id},"li_"+t.location_id))}},"rl_btn_loc_"+t.id),t.name,(0,j.jsxs)(j.Fragment,{children:[(0,j.jsx)(f.InfoButton,{onClick:function(){return i.changeContent((0,j.jsx)(y,{id:t.id},"rack_info_"+t.id))},title:"Rack information"},"info"),(0,j.jsx)(f.GoButton,{onClick:function(){return i.context.changeMain((0,j.jsx)(_.Main,{rack_id:t.id},"rack_device_"+t.id))},title:"Rack inventory"},"go"),(0,j.jsx)(f.ItemsButton,{onClick:function(){return i.changeContent((0,j.jsx)(Z,{id:t.id,changeSelf:i.changeContent},"rack_layout_"+t.id))},title:"Rack layout"},"items"),(0,j.jsx)(f.DeleteButton,{onClick:function(){return i.deleteList(t.id)},title:"Delete rack"},"del")]})]},i.deleteList=function(t){return window.confirm("Really delete rack?")&&(0,l.Fh)("api/rack/delete",{id:t}).then((function(n){n.deleted&&(i.setState({data:i.state.data.filter((function(n){return n.id!==t}))}),i.changeContent(null))}))},i.state={},i}return(0,r.Z)(e,[{key:"componentDidMount",value:function(){var t=this;(0,l.Fh)("api/rack/list",{sort:"name"}).then((function(n){return t.setState(n)}))}},{key:"render",value:function(){var t=this;return(0,j.jsxs)(j.Fragment,{children:[(0,j.jsxs)(d.ContentList,{header:"Racks",thead:["Location","Name",""],trows:this.state.data,listItem:this.listItem,children:[(0,j.jsx)(f.ReloadButton,{onClick:function(){return t.componentDidMount()}},"reload"),(0,j.jsx)(f.AddButton,{onClick:function(){return t.changeContent((0,j.jsx)(y,{id:"new"},"rack_new_"+(0,l.P4)()))},title:"Add rack"},"add")]},"cl"),(0,j.jsx)(d.ContentData,{mountUpdate:function(n){return t.changeContent=n}},"cda")]})}}]),e}(u.Component);I.contextType=d.RimsContext;var y=function(t){(0,c.Z)(e,t);var n=(0,s.Z)(e);function e(t){var r;return(0,o.Z)(this,e),(r=n.call(this,t)).onChange=function(t){return r.setState({data:(0,a.Z)((0,a.Z)({},r.state.data),{},(0,i.Z)({},t.target.name,t.target.value))})},r.updateInfo=function(){return(0,l.Fh)("api/rack/info",(0,a.Z)({op:"update"},r.state.data)).then((function(t){return r.setState(t)}))},r.state={data:null,found:!0},r}return(0,r.Z)(e,[{key:"componentDidMount",value:function(){var t=this;(0,l.Fh)("api/rack/info",{id:this.props.id}).then((function(n){return t.setState(n)}))}},{key:"render",value:function(){var t=this;return this.state.data?(0,j.jsxs)(d.InfoArticle,{header:"Rack",children:[(0,j.jsxs)(d.InfoColumns,{children:[(0,j.jsx)(h.TextInput,{id:"name",value:this.state.data.name,onChange:this.onChange},"name"),(0,j.jsx)(h.TextInput,{id:"size",value:this.state.data.size,onChange:this.onChange},"size"),(0,j.jsx)(h.SelectInput,{id:"console",value:this.state.data.console,onChange:this.onChange,children:this.state.consoles.map((function(t){return(0,j.jsx)("option",{value:t.id,children:t.hostname},t.id)}))},"console"),(0,j.jsx)(h.SelectInput,{id:"location_id",label:"Location",value:this.state.data.location_id,onChange:this.onChange,children:this.state.locations.map((function(t){return(0,j.jsx)("option",{value:t.id,children:t.name},t.id)}))},"location_id"),(0,j.jsx)(h.SelectInput,{id:"pdu_1",label:"PDU1",value:this.state.data.pdu_1,onChange:this.onChange,children:this.state.pdus.map((function(t){return(0,j.jsx)("option",{value:t.id,children:t.hostname},t.id)}))},"pdu_1"),(0,j.jsx)(h.SelectInput,{id:"pdu_2",label:"PDU2",value:this.state.data.pdu_2,onChange:this.onChange,children:this.state.pdus.map((function(t){return(0,j.jsx)("option",{value:t.id,children:t.hostname},t.id)}))},"pdu_2")]},"rack_content"),(0,j.jsx)(f.SaveButton,{onClick:function(){return t.updateInfo()},title:"Save"},"ri_btn_save")]},"rack_article"):(0,j.jsx)(d.Spinner,{})}}]),e}(u.Component),Z=function(t){(0,c.Z)(e,t);var n=(0,s.Z)(e);function e(t){var i;return(0,o.Z)(this,e),(i=n.call(this,t)).changeContent=function(t){i.props.changeSelf&&i.props.changeSelf(t)},i.state={},i}return(0,r.Z)(e,[{key:"componentDidMount",value:function(){var t=this;(0,l.Fh)("api/rack/devices",{id:this.props.id}).then((function(n){return t.setState(n)}))}},{key:"createRack",value:function(t,n,e){for(var i=this,a=[],o=1;o<this.state.size+1;o++)a.push((0,j.jsx)("div",{className:x,style:{gridRow:-o},children:o},"left_"+o),(0,j.jsx)("div",{className:m,style:{gridRow:-o},children:o},"right_"+o));return n.forEach((function(t){return a.push((0,j.jsx)("div",{className:k,style:{gridRowStart:i.state.size+2-e*t.rack_unit,gridRowEnd:i.state.size+2-(e*t.rack_unit+t.rack_size)},children:(0,j.jsx)(f.HrefButton,{style:{color:"var(--ui-txt-color)"},onClick:function(){return i.changeContent((0,j.jsx)(_.Info,{id:t.id},"device_info"))},text:t.hostname},"rd_btn_"+t.id)},"dev_"+t.id))})),(0,j.jsx)("div",{className:v,style:{grid:"repeat(".concat(this.state.size-1,", 2vw)/2vw 25vw 2vw")},children:a})}},{key:"render",value:function(){return this.state.size?(0,j.jsxs)(j.Fragment,{children:[(0,j.jsx)(d.InfoArticle,{header:"Front",children:this.createRack("front",this.state.front,1)},"rl_front"),(0,j.jsx)(d.InfoArticle,{header:"Back",children:this.createRack("back",this.state.back,-1)},"rl_back")]}):(0,j.jsx)(d.Spinner,{})}}]),e}(u.Component),D=function(t){(0,c.Z)(e,t);var n=(0,s.Z)(e);function e(t){var i;return(0,o.Z)(this,e),(i=n.call(this,t)).listItem=function(t){return[(0,j.jsx)(f.HrefButton,{text:t.id,onClick:function(){return i.changeContent((0,j.jsx)(_.Info,{id:t.id},"device_"+t.id))},title:"Device info"},"dev_"+t.id),t.hostname,(0,j.jsx)(f.InfoButton,{onClick:function(){return i.context.changeMain({module:t.type_base,function:"Manage",args:{device_id:t.id,type:t.type_name}})},title:"Manage device"},"rinfra_btn_"+t.id)]},i.state={},i}return(0,r.Z)(e,[{key:"componentDidMount",value:function(){var t=this;(0,l.Fh)("api/device/list",{field:"base",search:this.props.type,extra:["type"]}).then((function(n){return t.setState(n)}))}},{key:"render",value:function(){var t=this;return(0,j.jsxs)(j.Fragment,{children:[(0,j.jsx)(d.ContentList,{header:this.props.type,thead:["ID","Name",""],trows:this.state.data,listItem:this.listItem,children:(0,j.jsx)(f.ReloadButton,{onClick:function(){return t.componentDidMount()}},"reload")},"cl"),(0,j.jsx)(d.ContentData,{mountUpdate:function(n){return t.changeContent=n}},"cda")]})}}]),e}(u.Component);D.contextType=d.RimsContext}}]);
//# sourceMappingURL=496.d73d0c4b.chunk.js.map