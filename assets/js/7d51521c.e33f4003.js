"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[789],{3905:function(e,t,n){n.d(t,{Zo:function(){return p},kt:function(){return m}});var r=n(67294);function o(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function i(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function s(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?i(Object(n),!0).forEach((function(t){o(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):i(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function l(e,t){if(null==e)return{};var n,r,o=function(e,t){if(null==e)return{};var n,r,o={},i=Object.keys(e);for(r=0;r<i.length;r++)n=i[r],t.indexOf(n)>=0||(o[n]=e[n]);return o}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(r=0;r<i.length;r++)n=i[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(o[n]=e[n])}return o}var a=r.createContext({}),c=function(e){var t=r.useContext(a),n=t;return e&&(n="function"==typeof e?e(t):s(s({},t),e)),n},p=function(e){var t=c(e.components);return r.createElement(a.Provider,{value:t},e.children)},u={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},d=r.forwardRef((function(e,t){var n=e.components,o=e.mdxType,i=e.originalType,a=e.parentName,p=l(e,["components","mdxType","originalType","parentName"]),d=c(n),m=o,k=d["".concat(a,".").concat(m)]||d[m]||u[m]||i;return n?r.createElement(k,s(s({ref:t},p),{},{components:n})):r.createElement(k,s({ref:t},p))}));function m(e,t){var n=arguments,o=t&&t.mdxType;if("string"==typeof e||o){var i=n.length,s=new Array(i);s[0]=d;var l={};for(var a in t)hasOwnProperty.call(t,a)&&(l[a]=t[a]);l.originalType=e,l.mdxType="string"==typeof e?e:o,s[1]=l;for(var c=2;c<i;c++)s[c]=n[c];return r.createElement.apply(null,s)}return r.createElement.apply(null,n)}d.displayName="MDXCreateElement"},13875:function(e,t,n){n.r(t),n.d(t,{frontMatter:function(){return l},contentTitle:function(){return a},metadata:function(){return c},toc:function(){return p},default:function(){return d}});var r=n(87462),o=n(63366),i=(n(67294),n(3905)),s=["components"],l={sidebar_label:"compose",title:"links.compose"},a=void 0,c={unversionedId:"reference/links/compose",id:"reference/links/compose",title:"links.compose",description:"ComposedLink Objects",source:"@site/docs/reference/links/compose.md",sourceDirName:"reference/links",slug:"/reference/links/compose",permalink:"/rath/docs/reference/links/compose",editUrl:"https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/docs/reference/links/compose.md",tags:[],version:"current",frontMatter:{sidebar_label:"compose",title:"links.compose"},sidebar:"tutorialSidebar",previous:{title:"base",permalink:"/rath/docs/reference/links/base"},next:{title:"context",permalink:"/rath/docs/reference/links/context"}},p=[{value:"ComposedLink Objects",id:"composedlink-objects",children:[{value:"links",id:"links",children:[],level:4}],level:2},{value:"TypedComposedLink Objects",id:"typedcomposedlink-objects",children:[{value:"compose",id:"compose",children:[],level:4}],level:2}],u={toc:p};function d(e){var t=e.components,n=(0,o.Z)(e,s);return(0,i.kt)("wrapper",(0,r.Z)({},u,n,{components:t,mdxType:"MDXLayout"}),(0,i.kt)("h2",{id:"composedlink-objects"},"ComposedLink Objects"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},"class ComposedLink(TerminatingLink)\n")),(0,i.kt)("p",null,"A composed link is a link that is composed of multiple links. The links\nare executed in the order they are passed to the constructor."),(0,i.kt)("p",null,"The first link in the chain is the first link that is executed. The last\nlink in the chain is the terminating link, which is responsible for sending\nthe operation to the server."),(0,i.kt)("h4",{id:"links"},"links"),(0,i.kt)("p",null,"The links that are composed to form the chain. pydantic will validate that the last link is a terminating link."),(0,i.kt)("h2",{id:"typedcomposedlink-objects"},"TypedComposedLink Objects"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},"class TypedComposedLink(TerminatingLink)\n")),(0,i.kt)("p",null,"A typed composed link is a base class to create a definition for\na composed link. It is a link that is composed of multiple links that\nwill be set at compile time and not at runtime. Just add links\nthat you want to use to the class definition and they will be\nautomatically composed together."),(0,i.kt)("h4",{id:"compose"},"compose"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},"def compose(*links: Link) -> ComposedLink\n")),(0,i.kt)("p",null,"Compose a chain of links together. The first link in the chain is the first link that is executed.\nThe last link in the chain is the terminating link, which is responsible for sending the operation to the server."),(0,i.kt)("p",null,(0,i.kt)("strong",{parentName:"p"},"Returns"),":"),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("inlineCode",{parentName:"li"},"ComposedLink")," - The composed link")))}d.isMDXComponent=!0}}]);