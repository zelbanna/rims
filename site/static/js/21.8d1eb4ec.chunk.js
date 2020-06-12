(this.webpackJsonprims=this.webpackJsonprims||[]).push([[21],{57:function(e,t,n){"use strict";n.r(t),n.d(t,"List",(function(){return f}));var a=n(18),i=n(14),r=n(3),o=n(4),c=n(5),s=n(6),l=n(0),u=n.n(l),d=n(12),p=n(13),m=n(16),h=n(15),v=n(19),f=function(e){Object(s.a)(List,e);var t=Object(c.a)(List);function List(e){var n;return Object(r.a)(this,List),(n=t.call(this,e)).listItem=function(e){return[e.node,e.service,e.type,u.a.createElement(l.Fragment,null,u.a.createElement(v.InfoButton,{key:"sl_btn_info_"+e.id,onClick:function onClick(){return n.changeContent(u.a.createElement(k,{key:"server_info_"+e.id,id:e.id}))},title:"Service information"}),u.a.createElement(v.DeleteButton,{key:"sl_btn_delete"+e.id,onClick:function onClick(){return n.deleteList(e.id)},title:"Delete service"}),e.hasOwnProperty("ui")&&e.ui.length>0&&u.a.createElement(v.UiButton,{key:"sl_btn_ui"+e.id,onClick:function onClick(){return window.open(e.ui,"_blank")},title:"Server UI"}))]},n.changeContent=function(e){return n.setState({content:e})},n.deleteList=function(e){return window.confirm("Really delete service?")&&Object(d.d)("api/master/server_delete",{id:e}).then((function(t){return t.deleted&&n.setState({data:n.state.data.filter((function(t){return t.id!==e})),content:null})}))},n.state={},n}return Object(o.a)(List,[{key:"componentDidMount",value:function componentDidMount(){var e=this;Object(d.d)("api/master/server_list",{type:this.props.type}).then((function(t){return e.setState(t)}))}},{key:"componentDidUpdate",value:function componentDidUpdate(e){var t=this;e!==this.props&&Object(d.d)("api/master/server_list",{type:this.props.type}).then((function(e){return t.setState(e)}))}},{key:"render",value:function render(){var e=this;return u.a.createElement(l.Fragment,null,u.a.createElement(p.ContentList,{key:"sl_cl",header:"Servers",thead:["Node","Service","Type",""],trows:this.state.data,listItem:this.listItem},u.a.createElement(v.ReloadButton,{key:"sl_btn_reload",onClick:function onClick(){return e.componentDidMount()}}),u.a.createElement(v.AddButton,{key:"sl_btn_add",onClick:function onClick(){return e.changeContent(u.a.createElement(k,{key:"sl_new_"+Object(d.e)(),id:"new",type:e.props.type}))},title:"Add service"})),u.a.createElement(p.ContentData,{key:"sl_cd"},this.state.content))}}]),List}(l.Component),k=function(e){Object(s.a)(Info,e);var t=Object(c.a)(Info);function Info(e){var n;return Object(r.a)(this,Info),(n=t.call(this,e)).onChange=function(e){return n.setState({data:Object(i.a)({},n.state.data,Object(a.a)({},e.target.name,e.target.value))})},n.changeContent=function(e){return n.setState({content:e})},n.updateInfo=function(){return Object(d.d)("api/master/server_info",Object(i.a)({op:"update"},n.state.data)).then((function(e){return n.setState(e)}))},n.state={data:null,found:!0,content:null},n}return Object(o.a)(Info,[{key:"componentDidMount",value:function componentDidMount(){var e=this;Object(d.d)("api/master/server_info",{id:this.props.id}).then((function(t){t.data.node||(t.data.node=t.nodes[0]),t.data.type_id||(t.data.type_id=t.services[0].id),e.setState(t)}))}},{key:"render",value:function render(){var e=this;if(this.state.found){if(this.state.data){var t="new"!==this.state.data.id;return u.a.createElement(l.Fragment,null,u.a.createElement(p.InfoArticle,{key:"si_art",header:"Server"},u.a.createElement(p.InfoColumns,{key:"si_content"},u.a.createElement(h.TextLine,{key:"server",id:"server",label:"ID",text:this.state.data.id}),u.a.createElement(h.SelectInput,{key:"node",id:"node",value:this.state.data.node,onChange:this.onChange},this.state.nodes.map((function(e){return u.a.createElement("option",{key:e,value:e},e)}))),u.a.createElement(h.SelectInput,{key:"type_id",id:"type_id",label:"Service",value:this.state.data.type_id,onChange:this.onChange},this.state.services.map((function(e){return u.a.createElement("option",{key:e.id,value:e.id},"".concat(e.service," (").concat(e.type,")"))}))),u.a.createElement(h.UrlInput,{key:"ui",id:"ui",label:"UI",value:this.state.data.ui,onChange:this.onChange})),u.a.createElement(v.SaveButton,{key:"si_btn_save",onClick:function onClick(){return e.updateInfo()},title:"Save"}),t&&u.a.createElement(v.SyncButton,{key:"si_sync",onClick:function onClick(){return e.changeContent(u.a.createElement(y,{key:"srv_op_sync",id:e.state.data.id,operation:"sync"}))},title:"Sync service"}),t&&u.a.createElement(v.ReloadButton,{key:"si_restart",onClick:function onClick(){return e.changeContent(u.a.createElement(y,{key:"srv_op_rst",id:e.state.data.id,operation:"restart"}))},title:"Restart service"}),t&&u.a.createElement(v.SearchButton,{key:"si_status",onClick:function onClick(){return e.changeContent(u.a.createElement(y,{key:"srv_op_stat",id:e.state.data.id,operation:"status"}))},title:"Service status"}),t&&u.a.createElement(v.CheckButton,{key:"si_params",onClick:function onClick(){return e.changeContent(u.a.createElement(y,{key:"srv_op_params",id:e.state.data.id,operation:"parameters"}))},title:"Service parameters"})),u.a.createElement(m.NavBar,{key:"server_navigation",id:"server_navigation"}),this.state.content)}return u.a.createElement(p.Spinner,null)}return u.a.createElement(p.InfoArticle,{key:"si_art"},"Server with id: ",this.props.id," removed")}}]),Info}(l.Component),y=function(e){Object(s.a)(Operation,e);var t=Object(c.a)(Operation);function Operation(){return Object(r.a)(this,Operation),t.apply(this,arguments)}return Object(o.a)(Operation,[{key:"componentDidMount",value:function componentDidMount(){var e=this;Object(d.d)("api/master/server_operation",{op:this.props.operation,id:this.props.id}).then((function(t){return e.setState(t)}))}},{key:"render",value:function render(){return this.state?u.a.createElement(p.CodeArticle,{key:"srv_operation"},JSON.stringify(this.state,null,2)):u.a.createElement(p.Spinner,null)}}]),Operation}(l.Component)}}]);
//# sourceMappingURL=21.8d1eb4ec.chunk.js.map