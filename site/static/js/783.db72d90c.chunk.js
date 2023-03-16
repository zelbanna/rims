"use strict";(self.webpackChunkrims_frontend=self.webpackChunkrims_frontend||[]).push([[783],{783:function(t,e,n){n.r(e),n.d(e,{Info:function(){return x},List:function(){return m},User:function(){return C}});var a=n(942),s=n(413),i=n(671),r=n(144),o=n(340),u=n(882),d=n(791),l=n(252),h=n(885),c=n(682),f=n(698),p=n(184),m=function(t){(0,o.Z)(n,t);var e=(0,u.Z)(n);function n(t){var a;return(0,i.Z)(this,n),(a=e.call(this,t)).listItem=function(t){return[t.id,t.alias,t.name,(0,p.jsxs)(p.Fragment,{children:[(0,p.jsx)(c.ConfigureButton,{onClick:function(){return a.changeContent((0,p.jsx)(x,{id:t.id},"user_info"))},title:"Edit user"},"config"),(0,p.jsx)(c.DeleteButton,{onClick:function(){return a.deleteList(t.id)},title:"Delete user"},"del")]})]},a.deleteList=function(t){return window.confirm("Really delete user?")&&(0,l.Fh)("api/master/user_delete",{id:t}).then((function(e){e.deleted&&(a.setState({data:a.state.data.filter((function(e){return e.id!==t}))}),a.changeContent(null))}))},a.state={},a}return(0,r.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,l.Fh)("api/master/user_list").then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;return(0,p.jsxs)(p.Fragment,{children:[(0,p.jsxs)(h.ContentList,{header:"Users",thead:["ID","Alias","Name",""],trows:this.state.data,listItem:this.listItem,children:[(0,p.jsx)(c.ReloadButton,{onClick:function(){return t.componentDidMount()}},"reload"),(0,p.jsx)(c.AddButton,{onClick:function(){return t.changeContent((0,p.jsx)(x,{id:"new"},"user_info"))},title:"Add user"},"add")]},"cl"),(0,p.jsx)(h.ContentData,{mountUpdate:function(e){return t.changeContent=e}},"cda")]})}}]),n}(d.Component),x=function(t){(0,o.Z)(n,t);var e=(0,u.Z)(n);function n(t){var r;return(0,i.Z)(this,n),(r=e.call(this,t)).onChange=function(t){return r.setState({data:(0,s.Z)((0,s.Z)({},r.state.data),{},(0,a.Z)({},t.target.name,t.target.value))})},r.updateInfo=function(){r.setState({update:!1,password_check:""}),r.context.settings.id===r.state.data.id&&r.context.changeTheme(r.state.data.theme),(0,l.Fh)("api/master/user_info",(0,s.Z)({op:"update"},r.state.data),{"X-Log":"false"}).then((function(t){return r.setState(t)}))},r.state={data:null,found:!0},r}return(0,r.Z)(n,[{key:"componentDidUpdate",value:function(t){var e=this;t!==this.props&&(0,l.Fh)("api/master/user_info",{id:this.props.id}).then((function(t){return e.setState(t)}))}},{key:"componentDidMount",value:function(){var t=this;(0,l.Fh)("api/portal/theme_list").then((function(e){return t.setState({themes:e.data})})),(0,l.Fh)("api/master/user_info",{id:this.props.id}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;if(this.state.found){if(this.state.data&&this.state.themes){var e=this.state.update?"OK - updated":"";return(0,p.jsxs)(h.InfoArticle,{header:"User",children:[(0,p.jsxs)(h.InfoColumns,{children:[this.context.settings.id===this.props.id?(0,p.jsx)(f.TextLine,{id:"alias",text:this.state.data.alias},"alias"):(0,p.jsx)(f.TextInput,{id:"alias",value:this.state.data.alias,onChange:this.onChange},"alias"),(0,p.jsx)(f.PasswordInput,{id:"password",placeholder:"******",onChange:this.onChange},"password"),"admin"===this.context.settings.class&&(0,p.jsx)(f.SelectInput,{id:"class",value:this.state.data.class,onChange:this.onChange,children:this.state.classes.map((function(t){return(0,p.jsx)("option",{value:t,children:t},t)}))},"class"),(0,p.jsx)(f.TextInput,{id:"email",label:"E-Mail",value:this.state.data.email,onChange:this.onChange},"email"),(0,p.jsx)(f.TextInput,{id:"name",label:"Full name",value:this.state.data.name,onChange:this.onChange},"name"),(0,p.jsx)(f.SelectInput,{id:"theme",value:this.state.data.theme,onChange:this.onChange,children:this.state.themes.map((function(t){return(0,p.jsx)("option",{value:t,children:t},t)}))},"theme")]},"ui_content"),(0,p.jsx)(c.SaveButton,{onClick:function(){return t.updateInfo()},title:"Save"},"ui_btn_save"),(0,p.jsx)(h.Result,{result:e},"ui_operation")]},"ui_art")}return(0,p.jsx)(h.Spinner,{})}return(0,p.jsxs)(h.InfoArticle,{children:["User with id: ",this.props.id," removed"]},"ui_art")}}]),n}(d.Component);x.contextType=h.RimsContext;var C=function(t){(0,o.Z)(n,t);var e=(0,u.Z)(n);function n(){return(0,i.Z)(this,n),e.apply(this,arguments)}return(0,r.Z)(n,[{key:"render",value:function(){return(0,p.jsx)(h.Flex,{style:{justifyContent:"space-evenly"},children:(0,p.jsx)(x,{id:this.props.id},"user_info")},"flex")}}]),n}(d.Component)}}]);
//# sourceMappingURL=783.db72d90c.chunk.js.map