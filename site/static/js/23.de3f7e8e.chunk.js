(this.webpackJsonprims=this.webpackJsonprims||[]).push([[23],{57:function(e,t,n){"use strict";n.r(t),n.d(t,"List",(function(){return f})),n.d(t,"Info",(function(){return k})),n.d(t,"User",(function(){return y}));var a=n(18),i=n(14),r=n(4),s=n(5),o=n(6),u=n(7),c=n(0),l=n.n(c),d=n(12),h=n(13),m=n(20),p=n(15),f=function(e){Object(u.a)(n,e);var t=Object(o.a)(n);function n(e){var a;return Object(r.a)(this,n),(a=t.call(this,e)).listItem=function(e){return[e.id,e.alias,e.name,l.a.createElement(l.a.Fragment,null,l.a.createElement(m.ConfigureButton,{key:"config",onClick:function(){return a.changeContent(l.a.createElement(k,{key:"user_info",id:e.id}))},title:"Edit user"}),l.a.createElement(m.DeleteButton,{key:"del",onClick:function(){return a.deleteList(e.id)},title:"Delete user"}))]},a.deleteList=function(e){return window.confirm("Really delete user?")&&Object(d.d)("api/master/user_delete",{id:e}).then((function(t){t.deleted&&(a.setState({data:a.state.data.filter((function(t){return t.id!==e}))}),a.changeContent(null))}))},a.state={},a}return Object(s.a)(n,[{key:"componentDidMount",value:function(){var e=this;Object(d.d)("api/master/user_list").then((function(t){return e.setState(t)}))}},{key:"render",value:function(){var e=this;return l.a.createElement(l.a.Fragment,null,l.a.createElement(h.ContentList,{key:"cl",header:"Users",thead:["ID","Alias","Name",""],trows:this.state.data,listItem:this.listItem},l.a.createElement(m.ReloadButton,{key:"reload",onClick:function(){return e.componentDidMount()}}),l.a.createElement(m.AddButton,{key:"add",onClick:function(){return e.changeContent(l.a.createElement(k,{key:"user_info",id:"new"}))},title:"Add user"})),l.a.createElement(h.ContentData,{key:"cda",mountUpdate:function(t){return e.changeContent=t}}))}}]),n}(c.Component),k=function(e){Object(u.a)(n,e);var t=Object(o.a)(n);function n(e){var s;return Object(r.a)(this,n),(s=t.call(this,e)).onChange=function(e){return s.setState({data:Object(i.a)({},s.state.data,Object(a.a)({},e.target.name,e.target.value))})},s.updateInfo=function(){s.setState({update:!1,password_check:""}),s.context.settings.id===s.state.data.id&&s.context.changeTheme(s.state.data.theme),Object(d.d)("api/master/user_info",Object(i.a)({op:"update"},s.state.data),{"X-Log":"false"}).then((function(e){return s.setState(e)}))},s.state={data:null,found:!0},s}return Object(s.a)(n,[{key:"componentDidUpdate",value:function(e){var t=this;e!==this.props&&Object(d.d)("api/master/user_info",{id:this.props.id}).then((function(e){return t.setState(e)}))}},{key:"componentDidMount",value:function(){var e=this;Object(d.d)("api/portal/theme_list").then((function(t){return e.setState({themes:t.data})})),Object(d.d)("api/master/user_info",{id:this.props.id}).then((function(t){return e.setState(t)}))}},{key:"render",value:function(){var e=this;if(this.state.found){if(this.state.data&&this.state.themes){var t=this.state.update?"OK - updated":"";return l.a.createElement(h.InfoArticle,{key:"ui_art",header:"User"},l.a.createElement(h.InfoColumns,{key:"ui_content"},this.context.settings.id===this.props.id?l.a.createElement(p.TextLine,{key:"alias",id:"alias",text:this.state.data.alias}):l.a.createElement(p.TextInput,{key:"alias",id:"alias",value:this.state.data.alias,onChange:this.onChange}),l.a.createElement(p.PasswordInput,{key:"password",id:"password",placeholder:"******",onChange:this.onChange}),"admin"===this.context.settings.class&&l.a.createElement(p.SelectInput,{key:"class",id:"class",value:this.state.data.class,onChange:this.onChange},this.state.classes.map((function(e){return l.a.createElement("option",{key:e,value:e},e)}))),l.a.createElement(p.TextInput,{key:"email",id:"email",label:"E-Mail",value:this.state.data.email,onChange:this.onChange}),l.a.createElement(p.TextInput,{key:"name",id:"name",label:"Full name",value:this.state.data.name,onChange:this.onChange}),l.a.createElement(p.SelectInput,{key:"theme",id:"theme",value:this.state.data.theme,onChange:this.onChange},this.state.themes.map((function(e){return l.a.createElement("option",{key:e,value:e},e)})))),l.a.createElement(m.SaveButton,{key:"ui_btn_save",onClick:function(){return e.updateInfo()},title:"Save"}),l.a.createElement(h.Result,{key:"ui_operation",result:t}))}return l.a.createElement(h.Spinner,null)}return l.a.createElement(h.InfoArticle,{key:"ui_art"},"User with id: ",this.props.id," removed")}}]),n}(c.Component);k.contextType=h.RimsContext;var y=function(e){Object(u.a)(n,e);var t=Object(o.a)(n);function n(){return Object(r.a)(this,n),t.apply(this,arguments)}return Object(s.a)(n,[{key:"render",value:function(){return l.a.createElement(h.Flex,{key:"flex",style:{justifyContent:"space-evenly"}},l.a.createElement(k,{key:"user_info",id:this.props.id}))}}]),n}(c.Component)}}]);
//# sourceMappingURL=23.de3f7e8e.chunk.js.map