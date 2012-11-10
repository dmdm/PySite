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
        <link rel="stylesheet" href="${request.static_url('pysite:static/css/styles.css')}">
        <link rel="stylesheet" href="${request.static_url('pysite:static/css/base2.css')}">
        <link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/jquery/ui/themes/humanity/jquery-ui.css')}">
        <link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/jquery/ui/timepicker/timepicker.css')}">
		</%block>
		<%block name="scripts">
	    <script src="${request.static_url('pysite:static/app/libs/modernizr.js')}"></script>
	    <script src="${request.static_url('pysite:static/app/libs/jquery/jquery.js')}"></script>
	    <script src="${request.static_url('pysite:static/app/libs/jquery/ui/jquery-ui.js')}"></script>
	    <script src="${request.static_url('pysite:static/app/libs/jquery/ui/timepicker/timepicker.js')}"></script>
		</%block>
    </head>
    <body>
        <!--[if lt IE 7]>
            <p class="chromeframe">You are using an outdated browser. <a href="http://browsehappy.com/">Upgrade your browser today</a> or <a href="http://www.google.com/chromeframe/?redirect=true">install Google Chrome Frame</a> to better experience this site.</p>
        <![endif]-->

		<div id="pageContainer"><!-- BEGIN #pageContainer -->
			<div id="pageHeaderWrapper">
				<%block name="pageHeader">
				<header class="clearfix">
				<h1>${self.meta_title()}</h1>
				</header>
				</%block>
			</div>

			<div id="content"><!-- BEGIN #content -->
				  ${next.body()}
			</div><!-- END #content -->

		</div><!-- END #pageContainer -->

		<div id="pageFooterWrapper">
			<%block name="pageFooter">
			<footer>
				&copy;2012 by <a href="http://parenchym.com">Dirk Makowski</a>.
				All rights reserved.
			</footer>
			</%block>
		</div>
    </body>
</html>



