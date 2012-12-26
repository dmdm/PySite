<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">Manage Principals</%block>
<%block name="styles">
${parent.styles()}
<link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/jqgrid/css/ui.jqgrid.css')}">
</%block>
<%block name="require_config">
	${parent.require_config()}
	${grid.render_requirejs_config()|n}
</%block>
${grid.render(is_fluid=True)|n}
<p>Add selected principals to these roles:
<select id="roles" name="roles" size="5" multiple="multiple" style="vertical-align: top;">
% for r in roles:
    <option value="${r.id}">${r.name}</option>
% endfor
</select>
<button id="btnCreateRolemember" name="btnCreateRolemember">GO</button>
<script>
require(['jquery', 'pym'], function($, PYM) {
    $('#btnCreateRolemember').on('click', function (evt) {
        var gr = $('#grid-principals')
            , principal_ids = gr.jqGrid('getGridParam','selarrrow')
            , role_ids = $('#roles').val()
            , m = []
            , url = '${create_rolemember_url}'
        ;
        if (! principal_ids.length) {
            m.push('You need to select at least one principal.');
        }
        if (! role_ids || ! role_ids.length) {
            m.push('You need to select at least one role.');
        }
        if (m.length) {
            alert(m.join('\n'));
            return false;
        }
        console.log(principal_ids);
        console.log(role_ids);
        var data = {
                cmd: 'put'
                , principal_ids: principal_ids
                , role_ids: role_ids
            }
        ;
        $.post(url, data, function (data, textStatus, jqXHR) {
            for (var i=0, imax=data.msgs.length; i<imax; i++) {
                PYM.growl(data.msgs[i]);
            }
        });
    });
});
</script>
