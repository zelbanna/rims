(this.webpackJsonprims=this.webpackJsonprims||[]).push([[12],{44:function(t,e,n){"use strict";n.r(e),n.d(e,"Main",(function(){return v})),n.d(e,"Report",(function(){return C}));var a=n(18),i=n(14),r=n(4),c=n(5),o=n(6),s=n(7),u=n(0),l=n.n(u),d=n(12),y=n(13),m=n(15),h=n(19),_=n(16),v=function(t){Object(s.a)(n,t);var e=Object(o.a)(n);function n(t){var a;return Object(r.a)(this,n),(a=e.call(this,t)).compileNavItems=function(){return a.context.loadNavigation(l.a.createElement(_.NavBar,{key:"activity_navbar"},l.a.createElement(_.NavDropDown,{key:"act_nav",title:"Activities"},l.a.createElement(_.NavDropButton,{key:"act_nav_new",title:"New",onClick:function(){return a.changeContent(l.a.createElement(p,{key:"activity_info",id:"new"}))}}),l.a.createElement(_.NavDropButton,{key:"act_nav_day",title:"Daily",onClick:function(){return a.changeContent(l.a.createElement(k,{key:"activity_daily",changeSelf:a.changeContent}))}}),l.a.createElement(_.NavDropButton,{key:"act_nav_list",title:"List",onClick:function(){return a.changeContent(l.a.createElement(f,{key:"activity_list"}))}})),l.a.createElement(_.NavButton,{key:"act_nav_types",title:"Types",onClick:function(){return a.changeContent(l.a.createElement(E,{key:"activity_type_list"}))}}),l.a.createElement(_.NavButton,{key:"act_nav_report",title:"Report",onClick:function(){return a.changeContent(l.a.createElement(C,{key:"activity_report"}))}})))},a.changeContent=function(t){return a.setState(t)},a.state=l.a.createElement(k,{key:"activity_daily",changeSelf:a.changeContent}),a}return Object(c.a)(n,[{key:"componentDidMount",value:function(){this.compileNavItems()}},{key:"componentDidUpdate",value:function(t){t!==this.props&&this.compileNavItems()}},{key:"render",value:function(){return l.a.createElement(u.Fragment,{key:"main_base"},this.state)}}]),n}(u.Component);v.contextType=y.RimsContext;var f=function(t){Object(s.a)(n,t);var e=Object(o.a)(n);function n(t){var a;return Object(r.a)(this,n),(a=e.call(this,t)).listItem=function(t){return[t.date+" - "+t.time,l.a.createElement(h.HrefButton,{key:"al_btn_hinfo_"+t.id,onClick:function(){return a.changeContent(l.a.createElement(p,{key:"activity_info_"+t.id,id:t.id}))},text:t.type}),l.a.createElement(u.Fragment,{key:"activity_buttons_"+t.id},l.a.createElement(h.InfoButton,{key:"al_btn_info_"+t.id,onClick:function(){return a.changeContent(l.a.createElement(p,{key:"activity_"+t.id,id:t.id}))},title:"Activity information"}),l.a.createElement(h.DeleteButton,{key:"al_btn_delete_"+t.id,onClick:function(){return a.deleteList(t.id)},title:"Delete activity"}))]},a.searchHandler=function(t){a.setState({searchfield:t.target.value})},a.changeContent=function(t){return a.setState({content:t})},a.deleteList=function(t){return window.confirm("Delete activity")&&Object(d.d)("api/master/activity_delete",{id:t}).then((function(e){return e.deleted&&a.setState({data:a.state.data.filter((function(e){return e.id!==t})),content:null})}))},a.state={searchfield:""},a}return Object(c.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(d.d)("api/master/activity_list").then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;if(this.state.data){var e=0===this.state.searchfield.length?this.state.data:this.state.data.filter((function(e){return e.type.includes(t.state.searchfield)}));return l.a.createElement(u.Fragment,{key:"al_fragment"},l.a.createElement(y.ContentList,{key:"al_cl",header:"Activities",thead:["Date","Type",""],trows:e,listItem:this.listItem},l.a.createElement(h.ReloadButton,{key:"al_btn_reload",onClick:function(){return t.componentDidMount()}}),l.a.createElement(h.AddButton,{key:"al_btn_add",onClick:function(){return t.changeContent(l.a.createElement(p,{key:"activity_new_"+Object(d.e)(),id:"new"}))},title:"Add activity"}),l.a.createElement(m.SearchInput,{key:"al_search",searchHandler:this.searchHandler,value:this.state.searchfield,placeholder:"Search activities"})),l.a.createElement(y.ContentData,{key:"al_cd"},this.state.content))}return l.a.createElement(y.Spinner,null)}}]),n}(u.Component),p=function(t){Object(s.a)(n,t);var e=Object(o.a)(n);function n(t){var c;return Object(r.a)(this,n),(c=e.call(this,t)).onChange=function(t){return c.setState({data:Object(i.a)({},c.state.data,Object(a.a)({},t.target.name,t.target.value))})},c.updateInfo=function(){Object(d.d)("api/master/activity_info",Object(i.a)({op:"update"},c.state.data)).then((function(t){return c.setState(t)}))},c.state={data:null},c}return Object(c.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(d.d)("api/master/activity_info",{id:this.props.id,extras:["types","users"]}).then((function(e){null===e.data.user_id&&(e.data.user_id=t.context.settings.id),t.setState(e)}))}},{key:"render",value:function(){var t=this;return this.state.data?l.a.createElement(y.InfoArticle,{key:"ai_art",header:"Activity"},l.a.createElement(y.InfoColumns,{key:"ai_content"},l.a.createElement(m.TextLine,{key:"ai_id",id:"id",label:"ID",text:this.state.data.id}),l.a.createElement(m.SelectInput,{key:"ai_user_id",id:"user_id",label:"User",value:this.state.data.user_id,onChange:this.onChange},this.state.users.map((function(t,e){return l.a.createElement("option",{key:"ai_u_"+e,value:t.id},t.alias)}))),l.a.createElement(m.SelectInput,{key:"ai_type_id",id:"type_id",label:"Type",value:this.state.data.type_id,onChange:this.onChange},this.state.types.map((function(t,e){return l.a.createElement("option",{key:"ai_t_"+e,value:t.id},t.type)}))),l.a.createElement(m.DateInput,{key:"ai_date",id:"date",value:this.state.data.date,onChange:this.onChange}),l.a.createElement(m.TimeInput,{key:"ai_time",id:"time",value:this.state.data.time,onChange:this.onChange})),l.a.createElement(m.TextAreaInput,{key:"ai_event",id:"event",value:this.state.data.event,onChange:this.onChange}),l.a.createElement(h.SaveButton,{key:"ai_btn_save",onClick:function(){return t.updateInfo()},title:"Save"}),l.a.createElement(y.Result,{key:"ai_result",result:JSON.stringify(this.state.update)})):l.a.createElement(y.Spinner,null)}}]),n}(u.Component);p.contextType=y.RimsContext;var k=function(t){Object(s.a)(n,t);var e=Object(o.a)(n);function n(t){var c;Object(r.a)(this,n),(c=e.call(this,t)).changeContent=function(t){return c.props.changeSelf(t)},c.deleteList=function(t){return window.confirm("Delete activity")&&Object(d.d)("api/master/activity_delete",{id:t}).then((function(e){if(e.deleted){var n=c.state.data.findIndex((function(e){return e.act_id===t})),a=c.state.data[n];Object.assign(a,{user_id:null,event:null,act_id:null}),c.setState({data:c.state.data})}}))},c.onChange=function(t){var e=t.target.name,n=t.target.value,r={date:"date"===e?n:c.state.date};Object(d.d)("api/master/activity_daily",r).then((function(t){return c.setState(Object(i.a)({},t,Object(a.a)({},e,n)))}))},c.syncEvent=function(t,e){return Object(d.d)("api/master/activity_info",{op:"update",id:e||"new",user_id:c.state.user_id,type_id:t,event:"auto",date:c.state.date}).then((function(e){if(e.update){var n=c.state.data.findIndex((function(e){return e.id===t})),a=c.state.data[n];Object.assign(a,{user_id:c.state.user_id,event:"auto",act_id:e.data.id}),c.setState({data:c.state.data})}}))},c.listItem=function(t){return[t.type,t.user_id?c.state.users[t.user_id].alias:"-",t.event?t.event:"-",l.a.createElement(u.Fragment,{key:"ad_btn_"+t.id},!t.user_id&&l.a.createElement(h.AddButton,{key:"ad_add_"+t.id,onClick:function(){return c.syncEvent(t.id,t.act_id)}}),t.user_id&&t.user_id!==parseInt(c.state.user_id)&&l.a.createElement(h.SyncButton,{key:"ad_sync_"+t.id,onClick:function(){return c.syncEvent(t.id,t.act_id)}}),t.act_id&&l.a.createElement(h.InfoButton,{key:"ad_info",onClick:function(){return c.changeContent(l.a.createElement(p,{key:"activity_"+t.act_id,id:t.act_id}))}}),t.act_id&&l.a.createElement(h.DeleteButton,{key:"ad_del",onClick:function(){return c.deleteList(t.act_id)}}))]};var o=new Date(Date.now());return c.state={data:[],date:o.toISOString().substring(0,10),user_id:void 0,users:{}},c}return Object(c.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(d.d)("api/master/activity_daily",{extras:["users"]}).then((function(e){return t.setState(Object(i.a)({},e,{user_id:t.context.settings.id}))}))}},{key:"render",value:function(){var t=this;return this.state.data?l.a.createElement(y.ContentReport,{key:"ad_cr",header:"Activities",thead:["Type","User","Event",""],trows:this.state.data,listItem:this.listItem},l.a.createElement(h.ReloadButton,{key:"ad_reload_btn",onClick:function(){return t.componentDidMount()}}),l.a.createElement(m.SelectInput,{key:"ad_user_id",id:"user_id",label:"User",value:this.state.user_id,onChange:this.onChange},Object.values(this.state.users).map((function(t,e){return l.a.createElement("option",{key:"ai_u_"+e,value:t.id},t.alias)}))),l.a.createElement(m.DateInput,{key:"ad_date",id:"date",value:this.state.date,onChange:this.onChange})):l.a.createElement(y.Spinner,null)}}]),n}(u.Component);k.contextType=y.RimsContext;var C=function(t){Object(s.a)(n,t);var e=Object(o.a)(n);function n(t){var a;return Object(r.a)(this,n),(a=e.call(this,t)).listItem=function(t){return[t.date+" - "+t.time,t.user,t.type,t.class,t.event]},a.state={},a}return Object(c.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(d.d)("api/master/activity_list",{group:"month",mode:"full"}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){return l.a.createElement(y.ContentReport,{key:"act_cr",header:"Activities",thead:["Time","User","Type","Class","Event"],trows:this.state.data,listItem:this.listItem})}}]),n}(u.Component),E=function(t){Object(s.a)(n,t);var e=Object(o.a)(n);function n(t){var a;return Object(r.a)(this,n),(a=e.call(this,t)).listItem=function(t){return[t.id,t.type,t.class,l.a.createElement(u.Fragment,{key:"activity_buttons"},l.a.createElement(h.ConfigureButton,{key:"act_tp_info",onClick:function(){return a.changeContent(l.a.createElement(b,{key:"activity_type_"+t.id,id:t.id}))},title:"Edit type information"}),l.a.createElement(h.DeleteButton,{key:"act_tp_delete",onClick:function(){return a.deleteList(t.id)},title:"Delete type"}))]},a.changeContent=function(t){return a.setState({content:t})},a.deleteList=function(t){return window.confirm("Really delete type?")&&Object(d.d)("api/master/activity_type_delete",{id:t}).then((function(e){return e.deleted&&a.setState({data:a.state.data.filter((function(e){return e.id!==t})),content:null})}))},a.state={},a}return Object(c.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(d.d)("api/master/activity_type_list").then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;return l.a.createElement(u.Fragment,{key:"act_tp_fragment"},l.a.createElement(y.ContentList,{key:"act_tp_cl",header:"Activity Types",thead:["ID","Type","Class",""],trows:this.state.data,listItem:this.listItem},l.a.createElement(h.ReloadButton,{key:"act_tp_btn_reload",onClick:function(){return t.componentDidMount()}}),l.a.createElement(h.AddButton,{key:"act_tp_btn_add",onClick:function(){return t.changeContent(l.a.createElement(b,{key:"act_tp_new_"+Object(d.e)(),id:"new"}))},title:"Add activity type"})),l.a.createElement(y.ContentData,{key:"act_tp_cd"},this.state.content))}}]),n}(u.Component),b=function(t){Object(s.a)(n,t);var e=Object(o.a)(n);function n(t){var c;return Object(r.a)(this,n),(c=e.call(this,t)).onChange=function(t){return c.setState({data:Object(i.a)({},c.state.data,Object(a.a)({},t.target.name,t.target.value))})},c.changeContent=function(t){return c.setState({content:t})},c.updateInfo=function(){return Object(d.d)("api/master/activity_type_info",Object(i.a)({op:"update"},c.state.data)).then((function(t){return c.setState(t)}))},c.state={data:null,content:null},c}return Object(c.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(d.d)("api/master/activity_type_info",{id:this.props.id}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;return this.state.data?l.a.createElement(y.InfoArticle,{key:"at_art",header:"Activity Type"},l.a.createElement(y.InfoColumns,{key:"at_content"},l.a.createElement(m.TextLine,{key:"id",id:"id",text:this.state.data.id}),l.a.createElement(m.TextInput,{key:"type",id:"type",value:this.state.data.type,onChange:this.onChange,placeholder:"name"}),l.a.createElement(m.SelectInput,{key:"class",id:"class",value:this.state.data.class,onChange:this.onChange},this.state.classes.map((function(t){return l.a.createElement("option",{key:"at_class_"+t,value:t},t)})))),l.a.createElement(h.SaveButton,{key:"at_save",onClick:function(){return t.updateInfo()},title:"Save"})):l.a.createElement(y.Spinner,null)}}]),n}(u.Component)}}]);
//# sourceMappingURL=12.834cdf5e.chunk.js.map