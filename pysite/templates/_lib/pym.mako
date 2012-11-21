<%!
import pysite.lib
%>
## ===[ BREADCRUMBS ]=======
<%def name="breadcrumbs()">
<% bcs=pysite.lib.build_breadcrumbs(request) %>
% for elem in bcs:
<div class="breadcrumb"><a href="${elem[0]}">${elem[1]}</a></div>
% endfor
</%def>


## ===[ GROWL FLASH ]=======
<%def name="growl_flash()">
% for m in pysite.lib.build_growl_msgs(request):
    PYM.growl( ${m|n} );
% endfor
</%def>
