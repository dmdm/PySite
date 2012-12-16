<%namespace name="pym" file="pysite:templates/_lib/pym.mako"/>

<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <meta name="viewport" content="width=device-width">
  		<title><%block name="meta_title">PySite</%block></title>
		<meta name="description" content="<%block name="meta_descr">This is PySite on Pyramid</%block>">
		<meta name="keywords"    content="<%block name="meta_keywords">Python,PySite,Hosting,Web Site,Pyramid,Web Framework</%block>">
		<meta name="author"      content="<%block name="meta_author">Dirk Makowski (http://parenchym.com)</%block>">
		<%block name="styles">
        <link rel="stylesheet" href="${request.static_url('pysite:static/css/normalize.css')}">
        <link rel="stylesheet" href="${request.static_url('pysite:static/css/base1.css')}">
        <link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/jquery/ui/themes/humanity/jquery-ui.css')}">
        <link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/jquery/ui/pnotify/jquery.pnotify.default.css')}">
        <link rel="stylesheet" href="${request.static_url('pysite:static/css/styles.css')}">
        <link rel="stylesheet" href="${request.static_url('pysite:static/css/base2.css')}">
		</%block>
		<script>
		<%block name="require_config">
			var require = {
				  baseUrl: '${request.static_url('pysite:static/app')}'
				  // Dependencies are loaded before any "require()"d libraries.
				  // It seems we must use absolute URLs here.
				, deps: [
					'${request.static_url('pysite:static/app/libs/plugins.js')}'
				]
				, paths: {
					  'jquery': 'libs/jquery/jquery'
					, 'ui':     'libs/jquery/ui'
					// Define a path for requirejs, as it makes loading its plugins more comfortable
					, 'requirejs': 'libs/requirejs'
				}
				, shim: {
					  'ui/jquery-ui':                  ['jquery']
					, 'ui/timepicker/timepicker':      ['ui/jquery-ui']
					, 'ui/pnotify/jquery.pnotify.min': ['ui/jquery-ui']
				}
				, waitSeconds: 15
			};
		</%block>
		</script>
		<%block name="scripts">
			<script src="${request.static_url('pysite:static/app/libs/requirejs/require.js')}"></script>
		</%block>
    </head>
    <body>
        <!--[if lt IE 7]>
            <p class="chromeframe">You are using an outdated browser. <a href="http://browsehappy.com/">Upgrade your browser today</a> or <a href="http://www.google.com/chromeframe/?redirect=true">install Google Chrome Frame</a> to better experience this site.</p>
        <![endif]-->

	    ${next.body()}

		<script>
		require(['requirejs/domReady!', 'jquery', 'pym'], function(doc, $, PYM) {
			PYM.init({
				huhu: "HUHUHUHU"
			});
			${pym.growl_flash()}
		});
		</script>
    </body>
</html>
